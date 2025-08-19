import os
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIR = os.getenv("PERSIST_DIR", "artifacts/chroma")
KB_DIR = os.getenv("KB_DIR", "data/policies")
EMB_MODEL = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Step 2 (LLM) placeholders
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL_ID = os.getenv("MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.3")
