from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from typing import Dict, Optional
import os
import pathlib

from .models import CultureModel
from .utils import setup_logging, get_cached_response, cache_response

# Setup logging
logger = logging.getLogger(__name__)
setup_logging()

app = FastAPI(
    title="CultureBot API",
    description="A FastAPI service that answers culture and arts questions using the Mistral-7B-Instruct model",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a simple HTML template for the UI
@app.get("/ui", response_class=HTMLResponse)
async def get_ui():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CultureBot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .container {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                margin-top: 20px;
                background-color: #f9f9f9;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 15px;
                resize: vertical;
            }
            button {
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #2980b9;
            }
            .response {
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                min-height: 100px;
                white-space: pre-wrap;
            }
            .loading {
                text-align: center;
                display: none;
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
        <h1>🌍 CultureBot</h1>
        <p>Ask any question about world cultures, traditions, arts, or history.</p>
        <div class="container">
            <form id="questionForm">
                <label for="question">Your Question:</label>
                <textarea id="question" rows="4" placeholder="e.g., What is the cultural significance of tea ceremonies in Japan?"></textarea>
                <button type="submit">Ask CultureBot</button>
            </form>
            <div class="loading" id="loading">Thinking...</div>
            <div class="response" id="response"></div>
        </div>

        <script>
            document.getElementById('questionForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const question = document.getElementById('question').value;
                if (!question) return;

                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('response').innerText = '';

                try {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question }),
                    });

                    const data = await response.json();
                    document.getElementById('response').innerText = data.answer;
                } catch (error) {
                    document.getElementById('response').innerText = 'Error: ' + error.message;
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

# Initialize the model
culture_model = CultureModel()

@app.get("/")
async def root():
    """Health check endpoint."""
    logger.info("Health check endpoint called")
    return {"status": "healthy", "service": "CultureBot"}

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    logger.info("Detailed health check endpoint called")
    return {
        "status": "healthy",
        "service": "CultureBot",
        "model": "mistralai/Mistral-7B-Instruct",
        "version": "0.1.0"
    }

@app.post("/ask")
async def ask_question(request: Dict[str, str]):
    """
    Ask a culture or arts related question.
    
    Args:
        request: A dictionary containing the question with key 'question'
        
    Returns:
        Dict with the answer
    """
    if "question" not in request:
        logger.error("Missing 'question' in request")
        raise HTTPException(status_code=400, detail="Question is required")
    
    question = request["question"]
    logger.info(f"Question received: {question}")
    
    # Check cache first
    cached_response = get_cached_response(question)
    if cached_response:
        logger.info(f"Cache hit for question: {question}")
        return {"answer": cached_response}
    
    # Get response from model
    try:
        answer = await culture_model.get_answer(question)
        
        # Cache the response
        cache_response(question, answer)
        
        logger.info(f"Answer provided for: {question}")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
