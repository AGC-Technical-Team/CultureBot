from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict, Optional
import os

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
