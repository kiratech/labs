"""Configuration module for the RAG & Agents service.

This module reads runtime configuration from environment variables (optionally
loaded from a .env file) and exposes simple constants used across the codebase.

Documented variables:
- PERSIST_DIR: path where embedding/vector DB artifacts are stored.
- KB_DIR: directory containing the policy knowledge base used by the retriever.
- EMB_MODEL: embedding model id used to encode documents (default: sentence-transformers/all-MiniLM-L6-v2).
- HUGGINGFACEHUB_API_TOKEN: API token for Hugging Face; required for HF model inference / router calls.
- HF_MODEL_ID: Hugging Face model id used for chat/completions calls.

Notes
-----
- Keep sensitive values (HUGGINGFACEHUB_API_TOKEN) out of source control; prefer environment variables
  or a secrets manager. The .env loader is included for local development convenience.
- If you change defaults here, ensure tests and deployment configs are updated accordingly.
"""
import os
from dotenv import load_dotenv

# Load .env in development; load_dotenv is a no-op if no .env file is present.
load_dotenv()

# Paths / embeddings
# Directory where persistent vector DB / chroma artifacts are stored.
PERSIST_DIR = os.getenv("PERSIST_DIR", "artifacts/chroma")
# Directory containing the knowledge base used by the retriever (policy markdown files).
KB_DIR = os.getenv("KB_DIR", "data/policies")
# Embedding model identifier (used by the embedding client). Default is a lightweight sentence-transformer.
EMB_MODEL = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Hugging Face
# Token used to authenticate with the Hugging Face Hub / Inference API.
# Required for model inference that uses HF router or private models.
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
# HF model id for chat/completions calls. Make sure this model supports the endpoint your client uses.
# Example: "mistralai/Mistral-7B-Instruct-v0.3" or "Qwen/Qwen2.5-7B-Instruct" or any OpenAI-compatible HF router model.
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-7B-Instruct")
