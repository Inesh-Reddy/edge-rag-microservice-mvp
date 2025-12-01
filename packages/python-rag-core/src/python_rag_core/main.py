def run_rag_service():
    print("🚀 Starting RAG core service...")

    # Load embedding model
    print("📥 Loading embedding model...")

    # Initialize Qdrant (in memory mode for dev)
    print("🧠 Initializing Qdrant (in-memory)...")


    # Sample document
    sample_text = "LangChain makes building LLM apps easier"
    print(f"📄 Embedding sample doc: '{sample_text}'")


# Allow running directly when executing this file
if __name__ == "__main__":
    run_rag_service()
