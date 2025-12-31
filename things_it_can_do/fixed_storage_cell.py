"""
Fixed Storage Cell - Copy and paste this into your notebook

This replaces the problematic storage cell with auto-fetching logic.
"""

import numpy as np
import json
import os
import requests

# Complete storage and retrieval system
class EmbeddingStore:
    def __init__(self, store_dir='embedding_store'):
        self.store_dir = store_dir
        os.makedirs(store_dir, exist_ok=True)
        self.embeddings_file = os.path.join(store_dir, 'embeddings.npy')
        self.metadata_file = os.path.join(store_dir, 'metadata.json')
        self.load()
    
    def load(self):
        """Load embeddings and metadata from disk"""
        if os.path.exists(self.embeddings_file):
            self.embeddings = np.load(self.embeddings_file)
        else:
            self.embeddings = np.array([])
        
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = []
    
    def add_video(self, video_id, embedding, metadata_dict):
        """Add a video embedding to the store"""
        embedding_array = np.array(embedding).reshape(1, -1)
        
        if len(self.embeddings) == 0:
            self.embeddings = embedding_array
        else:
            self.embeddings = np.vstack([self.embeddings, embedding_array])
        
        self.metadata.append({
            'video_id': video_id,
            **metadata_dict
        })
        self.save()
    
    def save(self):
        """Save embeddings and metadata to disk"""
        np.save(self.embeddings_file, self.embeddings)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def search(self, query_embedding, top_k=5):
        """Search for similar videos using cosine similarity"""
        if len(self.embeddings) == 0:
            return []
        
        query_vec = np.array(query_embedding).reshape(1, -1)
        
        # Normalize for cosine similarity
        query_norm = query_vec / np.linalg.norm(query_vec)
        embeddings_norm = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        
        # Calculate cosine similarities
        similarities = np.dot(embeddings_norm, query_norm.T).flatten()
        
        # Get top K indices
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return results with metadata
        results = []
        for idx in top_k_indices:
            results.append({
                'index': int(idx),
                'similarity': float(similarities[idx]),
                'metadata': self.metadata[idx]
            })
        
        return results

# Initialize store
store = EmbeddingStore()

# Auto-fetch embeddings if not in memory
if 'embeddings_data' not in locals() or 'result' not in locals():
    print("📥 Fetching embeddings from API...")
    task_id = "695556329f7b96b9f6d09851"
    
    response = requests.get(
        f"https://api.twelvelabs.io/v1.3/embed-v2/tasks/{task_id}",
        headers={"x-api-key": apiKey}
    )
    
    if response.status_code == 200:
        result = response.json()
        embeddings_data = result['data']
        print(f"✓ Retrieved {len(embeddings_data)} embeddings")
    else:
        print(f"❌ Failed to fetch embeddings: {response.status_code}")
        embeddings_data = []

# Store the embeddings
if len(embeddings_data) > 0:
    store.add_video(
        video_id='695556329f7b96b9f6d09851',
        embedding=embeddings_data[0]['embedding'],  # visual asset embedding
        metadata_dict={
            'duration': result['metadata']['duration'],
            'url': result['metadata']['input_url'],
            'type': 'visual_asset'
        }
    )
    print(f"✓ Stored video embedding. Total videos: {len(store.metadata)}")
else:
    print("⚠ No embeddings available to store")

# Fast search function
def search_numpy(query_embedding, top_k=5):
    """Search using the embedding store"""
    return store.search(query_embedding, top_k)

print("\nStorage system ready! Use search_numpy(query_embedding) to search.")
