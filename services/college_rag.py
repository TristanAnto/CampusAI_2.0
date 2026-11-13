import os
import chromadb
from google import genai
from services.document_parser import parse_document

# Initialize Gemini Client & ChromaDB
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="storage/chroma_db")

# Dedicated shared collection for official college documents
official_collection = chroma_client.get_or_create_collection(name="official_college_docs")

def index_official_pdf(file_path: str, pdf_title: str):
    """
    Extracts text with page numbers, generates embeddings using gemini-embedding-001, and stores in ChromaDB.
    """
    pages = parse_document(file_path)
    filename = os.path.basename(file_path)
    print(f"DEBUG: Parsed {len(pages)} pages from {filename}")

    for item in pages:
        page_num = item["page"]
        text_chunk = item["text"]
        
        if not text_chunk.strip():
            continue

        # Generate embedding using gemini-embedding-001
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text_chunk
        )
        embedding = response.embeddings[0].values

        doc_id = f"{filename}_p{page_num}"
        print(f"DEBUG: Upserting document ID: {doc_id}")
        
        official_collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text_chunk],
            metadatas=[{
                "pdf_name": pdf_title,
                "filename": filename,
                "page": page_num,
                "status": "active"
            }]
        )
    print("DEBUG: Indexing complete. Total items in collection:", official_collection.count())

def query_college_assistant(user_query: str) -> dict:
    """
    Retrieves top-5 passages using gemini-embedding-001, enforces evidence grounding, exact citations,
    and abstention with robust multi-model fallback.
    """
    try:
        # 1. Embed query
        query_response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=user_query
        )
        query_embedding = query_response.embeddings[0].values

        # 2. Retrieve top-5 relevant passages
        results = official_collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )

        # Safely extract documents and metadatas (ChromaDB returns list-of-lists)
        documents = []
        metadatas = []
        if results.get("documents") and results["documents"][0]:
            documents = results["documents"][0]
        if results.get("metadatas") and results["metadatas"][0]:
            metadatas = results["metadatas"][0]

        if not documents:
            return {
                "answer": "I cannot verify this from the official college documents currently available. No documents have been indexed yet.",
                "citations": []
            }

        # 3. Construct context bundle with metadata
        context_blocks = []
        citations = []
        for doc, meta in zip(documents, metadatas):
            if meta and isinstance(meta, dict):
                source_label = f"[{meta.get('pdf_name', 'Unknown')}, Page {meta.get('page', '?')}]"
            else:
                source_label = "[Unknown Source]"
            context_blocks.append(f"Content: {doc}\nSource: {source_label}")
            citations.append(source_label)

        context_str = "\n\n---\n\n".join(context_blocks)

        # 4. Prompt Gemini with strict RAG guardrails
        prompt = f"""
        You are the official CampusAI 2.0 College Assistant. Answer the student's question using ONLY the provided official college document chunks below.
        
        RULES:
        1. Provide an evidence-grounded answer.
        2. Append exact inline citations like [Document Name, Page X] for every claim.
        3. If the retrieved documents do not contain enough information to answer the question, you MUST abstain by responding strictly with: "I cannot verify this from the official college documents currently available."

        Context Chunks:
        {context_str}

        Student Question: {user_query}
        """

        # 5. Generate content with fallback models (library handles internal retries for 503)
        response = None
        last_error = None
        models_to_try = ["gemini-3.5-flash", "gemini-3.6-flash"]

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and getattr(response, 'text', None):
                    break
            except Exception as e:
                last_error = e
                continue

        if response is None or not getattr(response, 'text', None):
            error_msg = str(last_error) if last_error else "no response received"
            return {
                "answer": f"I'm unable to generate an answer right now due to a technical issue ({error_msg}). Please try again in a moment.",
                "citations": []
            }

        return {
            "answer": response.text,
            "citations": list(set(citations))
        }
    except Exception as e:
        return {
            "answer": f"I encountered an error while processing your question: {str(e)}",
            "citations": []
        }