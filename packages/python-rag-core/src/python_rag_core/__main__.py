"""
Allows executing the package via:
    poetry run python -m python_rag_core
"""

from .main import run_rag_service

if __name__ == "__main__":
    run_rag_service()
