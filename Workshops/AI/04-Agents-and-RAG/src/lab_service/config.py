import os
from dotenv import load_dotenv
load_dotenv()

# Paths / embeddings
PERSIST_DIR = os.getenv("PERSIST_DIR", "artifacts/chroma")
KB_DIR = os.getenv("KB_DIR", "data/policies")
EMB_MODEL = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Hugging Face
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.3")
