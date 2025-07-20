import os

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
PDF_DIR = os.path.join(DATA_DIR, 'pdfs')
CHROMA_DB_DIR = os.path.join(DATA_DIR, 'chroma_db')

# Path to local LLM (GGUF file) and llama.cpp binary
LLM_MODEL_PATH = os.environ.get('LLM_MODEL_PATH', os.path.join(DATA_DIR, 'models', 'llama-3-8b.Q4_K_M.gguf'))
LLAMA_CPP_PATH = os.environ.get('LLAMA_CPP_PATH', '/usr/local/bin/llama.cpp')

EMBEDDING_MODEL_NAME = os.environ.get('EMBEDDING_MODEL_NAME', 'BAAI/bge-m3')

# ChromaDB collection prefix
CHROMA_COLLECTION_PREFIX = 'elimu_topic_'

# Similarity threshold for knowledge sufficiency
SIMILARITY_THRESHOLD = 0.6

# Chunk size for PDF splitting
CHUNK_SIZE = 400  # tokens
CHUNK_OVERLAP = 50 