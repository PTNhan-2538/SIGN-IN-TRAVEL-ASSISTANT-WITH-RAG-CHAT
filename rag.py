import os
import json
import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()

# Đọc URL từ biến môi trường (.env)
OLLAMA_PUBLIC_URL = os.getenv("OLLAMA_PUBLIC_URL", "").strip().rstrip("/")
EMBED_MODEL = "embeddinggemma"
CHAT_MODEL = "qwen3:4b"
CACHE_VECTOR_FILE = "vector_cache.npy"

def load_knowledge_base(filepath="knowledge_base.json"):
    """Đọc dữ liệu từ file JSON cẩm nang du lịch."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def get_embedding(text: str) -> list:
    """Gọi Ollama API để tạo vector cho một đoạn văn bản (dùng cho câu hỏi)."""
    url = f"{OLLAMA_PUBLIC_URL}/api/embed"
    payload = {
        "model": EMBED_MODEL,
        "input": [text]
    }
    try:
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        data = res.json()
        return data["embeddings"][0]
    except Exception as e:
        raise RuntimeError(f"Lỗi kết nối Ollama Embeddings: {str(e)}")

def get_embeddings_batch(texts: list) -> np.ndarray:
    """Tạo vector cho danh sách tài liệu bằng cách gọi tuần tự từng đoạn để tránh quá tải kết nối tunnel."""
    url = f"{OLLAMA_PUBLIC_URL}/api/embed"
    embeddings = []
    
    for text in texts:
        payload = {
            "model": EMBED_MODEL,
            "input": [text]
        }
        try:
            res = requests.post(url, json=payload, timeout=60)
            res.raise_for_status()
            data = res.json()
            embeddings.append(data["embeddings"][0])
        except Exception as e:
            raise RuntimeError(f"Lỗi khi embed văn bản qua Ollama: {str(e)}")
            
    return np.array(embeddings, dtype=float)

def load_or_create_kb_vectors(kb_entries: list) -> np.ndarray:
    """
    Load vector từ file cache nếu có để tránh gọi Ollama liên tục gây lỗi timeout.
    Nếu chưa có, gọi tuần tự qua Ollama và lưu lại file cache.
    """
    if not kb_entries:
        return np.array([])
        
    if os.path.exists(CACHE_VECTOR_FILE):
        try:
            vectors = np.load(CACHE_VECTOR_FILE)
            if len(vectors) == len(kb_entries):
                return vectors
        except Exception:
            pass

    texts = [f"{entry['title']}: {entry['text']}" for entry in kb_entries]
    vectors = get_embeddings_batch(texts)
    np.save(CACHE_VECTOR_FILE, vectors)
    return vectors

def cosine_similarity(a, b):
    """Tính độ tương đồng Cosine giữa 2 vector."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def retrieve_top_k(query: str, kb_entries: list, kb_vectors: np.ndarray, k=3) -> list:
    """
    Truy xuất top-k entries dựa trên độ tương đồng Cosine.
    Trả về danh sách các tuple: (entry, score)
    """
    if not kb_entries or kb_vectors.size == 0:
        return []
    
    query_vector = np.array(get_embedding(query), dtype=float)
    scores = []
    
    for i, vec in enumerate(kb_vectors):
        score = cosine_similarity(query_vector, vec)
        scores.append((kb_entries[i], score))
        
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:k]

def generate_rag_answer(query: str, retrieved_docs: list) -> str:
    """
    Sử dụng qwen3:4b để sinh câu trả lời chỉ dựa trên các tài liệu được truy xuất.
    Nếu thông tin không đủ, buộc phải nói 'I don't know'.
    """
    url = f"{OLLAMA_PUBLIC_URL}/api/chat"
    
    context_str = ""
    for entry, score in retrieved_docs:
        context_str += f"ID: {entry['id']}\nTitle: {entry['title']}\nContent: {entry['text']}\nSource: {entry['source']}\n\n"
        
    system_prompt = (
        "You are a professional, helpful travel assistant for Ho Chi Minh City. "
        "Answer the user's question STRICTLY using ONLY the provided context entries below. "
        "You must cite the source entry IDs (e.g., [G01], [G03]) in your response. "
        "If the answer cannot be found in the provided context, you MUST say exactly: "
        "\"I don't know based on the provided travel guide.\" Do not guess or invent facts."
    )
    
    user_prompt = f"Context Entries:\n{context_str}\nUser Question: {query}"
    
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    
    try:
        res = requests.post(url, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        return data.get("message", {}).get("content", "Không thể tạo phản hồi từ mô hình.")
    except Exception as e:
        return f"Lỗi kết nối Ollama Chat Model (`{CHAT_MODEL}`): {str(e)}"