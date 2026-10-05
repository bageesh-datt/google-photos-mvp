from backend.app.main import app

# Vercel Python Serverless Function entrypoint
# Exposes FastAPI ASGI app for serverless handling
__all__ = ["app"]
