import re
from collections import Counter
from typing import List, Dict
from pymongo.collection import Collection

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    # Simple chunking by sentences, fallback to fixed size
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) < chunk_size:
            current += sent + " "
        else:
            if current:
                chunks.append(current.strip())
            current = sent + " "
    if current:
        chunks.append(current.strip())
    return chunks

def index_chunks(chunks: List[str], filename: str, user_id: str, collection: Collection):
    docs = []
    for i, chunk in enumerate(chunks):
        keywords = Counter(re.findall(r'\w+', chunk.lower()))
        docs.append({
            "user_id": user_id,
            "filename": filename,
            "chunk_id": i,
            "text": chunk,
            "keywords": list(keywords.keys()),
            "keyword_counts": dict(keywords)
        })
    if docs:
        collection.insert_many(docs)

def search_chunks(query: str, user_id: str, collection: Collection, top_k: int = 5) -> List[Dict]:
    query_words = set(re.findall(r'\w+', query.lower()))
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$addFields": {
            "relevance": {"$size": {"$setIntersection": ["$keywords", list(query_words)]}}
        }},
        {"$sort": {"relevance": -1}},
        {"$limit": top_k}
    ]
    return list(collection.aggregate(pipeline))
