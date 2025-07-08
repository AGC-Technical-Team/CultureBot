# CultureBot 🌍🤖

A FastAPI microservice that answers culture and arts questions using the Mistral-7B-Instruct model from Hugging Face.

## Features

- **AI-Powered Responses**: Uses the open source "mistralai/Mistral-7B-Instruct" model via Hugging Face API
- **FastAPI Framework**: Modern, fast, web framework for building APIs
- **Prompt Engineering Layer**: Clearly separated prompt template for consistent AI responses
- **Caching**: Optional Redis or in-memory LRU caching for faster responses
- **Containerized**: Docker support for easy deployment
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing and deployment
- **Separation of Concerns**: Clear separation between ML wrapper, API routing, and UI
- **Comprehensive Logging**: Built-in logging for questions, answers, and errors

## Project Structure

```
culturebot/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI endpoints
│   ├── models.py      # Async wrapper around HF API + prompt template
│   └── utils.py       # Redis/LRU cache + logging helpers
├── tests/
│   ├── __init__.py
│   └── test_api.py    # API tests
├── .env.example       # Environment variables template
├── .github/
│   └── workflows/
│       └── deploy.yml # CI/CD pipeline
├── Dockerfile         # Container definition
├── README.md          # This documentation
└── requirements.txt   # Python dependencies
```

## Setup and Installation

### Prerequisites

- Python 3.11 or higher
- [Hugging Face account](https://huggingface.co/join) and API token
- Docker (optional, for containerization)
- Redis (optional, for caching)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/culturebot.git
   cd culturebot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file and add your Hugging Face API token:
   ```
   HF_TOKEN=your_huggingface_token_here
   ```

6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

7. Access the API at http://localhost:8000

### Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t culturebot .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env culturebot
   ```

3. Access the API at http://localhost:8000

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the cultural significance of tea ceremonies in Japan?"}'
```

## Deployment

The project includes a GitHub Actions workflow that:

1. Runs tests on every push and pull request
2. Builds and pushes a Docker image to GitHub Container Registry
3. Deploys to cloud platforms like Render, Fly.io, or Railway

To set up deployment:

1. Add the following secrets to your GitHub repository:
   - `HF_TOKEN`: Your Hugging Face API token
   - `RENDER_DEPLOY_HOOK`: Your Render.com deploy hook URL (or equivalent for other platforms)

2. Push to the main branch to trigger the deployment workflow

## Testing

Run the tests with pytest:

```bash
pytest
```

## Configuration Options

Environment variables that can be set in `.env`:

- `HF_TOKEN`: Hugging Face API token (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `USE_REDIS`: Whether to use Redis for caching (default: false)
- `REDIS_URL`: Redis connection URL (default: redis://localhost:6379)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

MIT

---

Made with ❤️ by DevOps × AI
