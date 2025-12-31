# TwelveLabs Video Embeddings & Semantic Search

This notebook demonstrates how to work with video embeddings using the TwelveLabs API, including creating embeddings, storing them, and performing semantic search.

## Documentation

- Official API Reference: https://docs.twelvelabs.io/v1.3/sdk-reference/python
- Embeddings API: https://docs.twelvelabs.io/v1.3/sdk-reference/python/embeddings

## Overview

TwelveLabs embeddings convert videos and text into high-dimensional vectors that capture their semantic meaning. This enables:

- **Semantic Search**: Find videos using natural language queries
- **Similarity Comparison**: Identify similar video segments
- **Content Understanding**: Extract visual, audio, and transcription embeddings
- **Efficient Storage**: Save and reuse embeddings for fast retrieval

**Key Features:**

- Multiple embedding types: visual, audio, transcription
- Multiple scopes: clip-level (segments) and asset-level (entire video)
- Sync and async processing
- Text-to-video search capabilities

## What You'll Learn

1. Create text embeddings
2. Create video embeddings (sync and async)
3. Retrieve and analyze embedding data
4. Build a storage system for embeddings
5. Perform text-to-video semantic search

## Prerequisites

- TwelveLabs API key (stored in `.env` file as `TL_API_KEY`)
- Required packages: `requests`, `numpy`, `scikit-learn`, `python-dotenv`

---

## Configuration

### Cell 1: Import Libraries

```python
# Import required libraries for TwelveLabs API interaction
import uuid  # For generating unique identifiers if needed
from twelvelabs import TwelveLabs  # Main TwelveLabs client class
from twelvelabs.indexes import IndexesCreateRequestModelsItem  # Type hint for index model configuration
from twelvelabs.tasks import TasksRetrieveResponse  # Type hint for task response objects
```

### Cell 2: Load API Key

```python
# Load environment variables from .env file
import os
from dotenv import load_dotenv

# Load environment variables (including API key)
load_dotenv()

# Retrieve the TwelveLabs API key from environment variables
apiKey = os.getenv("TL_API_KEY")

# Verify that the API key was successfully loaded
print(f"Key loaded: {bool(apiKey)}")
```

---

## Part 1: Text Embeddings

### Creating Embeddings from Text

Text embeddings convert natural language into vector representations that can be compared with video embeddings for semantic search.

### Cell 3: Sync Text Embedding

```python
import requests

# Create sync embeddings (POST /embed-v2)
response = requests.post(
    "https://api.twelvelabs.io/v1.3/embed-v2",
    headers={"x-api-key": apiKey},
    json={
        "input_type": "text",
        "model_name": "marengo3.0",
        "text": {
            "input_text": "riding a bike"
        }
    },
)

print(response.json())
```

**Output**: A 512-dimensional embedding vector representing the semantic meaning of "riding a bike"

---

## Part 2: Video Embeddings

### Sync Video Segmentation

Process videos and get embeddings immediately (synchronous). Best for short videos or when you need instant results.

### Cell 4: Sync Video Embedding from URL

```python
import requests

# Convert Google Drive sharing link to direct download URL
def convert_gdrive_url(share_url):
    """Extract file ID and create direct download URL"""
    file_id = share_url.split('/d/')[1].split('/')[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# Configure video URL
original_url = "https://drive.google.com/file/d/1mzKhQJF6eP37QXdzHzIQ0TNJqICWKxTX/view?usp=sharing"
direct_url = convert_gdrive_url(original_url)

# Create sync embeddings (processes immediately)
response = requests.post(
    "https://api.twelvelabs.io/v1.3/embed-v2",
    headers={
        "x-api-key": apiKey,
        "Content-Type": "application/json"
    },
    json={
        "input_type": "video",
        "model_name": "marengo3.0",
        "video": {
            "media_source": {"url": direct_url},
            "start_sec": 0,
            "end_sec": 12,
            "segmentation": {
                "strategy": "dynamic",
                "dynamic": {"min_duration_sec": 4}
            },
            "embedding_option": ["visual", "audio", "transcription"],
            "embedding_scope": ["clip", "asset"]
        }
    }
)

print(f"Status: {response.status_code}")
print(response.json())
```

**Segmentation Strategies:**

- `dynamic`: Automatically detect scene changes
- `fixed`: Split into equal-duration segments

**Embedding Options:**

- `visual`: Image/video content
- `audio`: Sound and music
- `transcription`: Spoken words

**Embedding Scopes:**

- `clip`: Individual segments
- `asset`: Entire video

---

### Async Video Segmentation

For longer videos or batch processing, use async tasks that process in the background.

### Cell 5: Create Async Embedding Task

```python
import requests

def convert_gdrive_url(share_url):
    """Extract file ID and create direct download URL"""
    file_id = share_url.split('/d/')[1].split('/')[0]
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# Configure video URL
original_url = "https://drive.google.com/file/d/1wTLUa2AyEOwreLzoppt6hcCh29EiQPX8/view?usp=drive_link"
direct_url = convert_gdrive_url(original_url)

# Store task ID for later retrieval
TASK_ID = None  # Will be set after creating the task

# Create async embedding task
response = requests.post(
    "https://api.twelvelabs.io/v1.3/embed-v2/tasks",
    headers={
        "x-api-key": apiKey,
        "Content-Type": "application/json"
    },
    json={
        "input_type": "video",
        "model_name": "marengo3.0",
        "video": {
            "media_source": {"url": direct_url},
            "start_sec": 0,
            "end_sec": 12,
            "segmentation": {
                "strategy": "fixed",
                "fixed": {"duration_sec": 6}
            },
            "embedding_option": ["visual", "audio", "transcription"],
            "embedding_scope": ["clip", "asset"]
        }
    }
)

result = response.json()
if '_id' in result:
    TASK_ID = result['_id']
    print(f"✓ Created task: {TASK_ID}")
    print(f"Status: {result['status']}")
else:
    print(f"Task creation response: {result}")
```

### Cell 6: List All Embedding Tasks

```python
import requests

# List all embedding tasks
response = requests.get(
    "https://api.twelvelabs.io/v1.3/embed-v2/tasks",
    headers={"x-api-key": apiKey}
)

result = response.json()

if 'data' in result:
    tasks = result['data']
    print(f"📊 Total tasks: {len(tasks)}\n")

    for task in tasks:
        task_id = task.get('_id')
        status = task.get('status')
        created = task.get('created_at')

        print(f"Task ID: {task_id}")
        print(f"Status: {status}")
        print(f"Created: {created}")
        print("-" * 60)

        # Auto-set TASK_ID to most recent ready task
        if status == 'ready' and TASK_ID is None:
            TASK_ID = task_id
            print(f"✓ Using this task for retrieval\n")
else:
    print("No tasks found")
```

### Cell 7: Retrieve Task Embeddings

```python
import requests

# Use task ID from previous cell or specify manually
if TASK_ID is None:
    TASK_ID = "695556329f7b96b9f6d09851"  # Replace with your task ID

# Retrieve the task embeddings
response = requests.get(
    f"https://api.twelvelabs.io/v1.3/embed-v2/tasks/{TASK_ID}",
    headers={"x-api-key": apiKey}
)

result = response.json()

# Extract embeddings data
embeddings_data = result['data']

print(f"📥 Total embeddings: {len(embeddings_data)}\n")
print("Embedding breakdown:")

for idx, item in enumerate(embeddings_data):
    embedding_type = item['embedding_option']
    scope = item['embedding_scope']
    start = item['start_sec']
    end = item['end_sec']
    vector_length = len(item['embedding'])

    print(f"\n{idx + 1}. Type: {embedding_type} | Scope: {scope}")
    print(f"   ⏱️  Time: {start}s - {end}s")
    print(f"   📊 Vector dimensions: {vector_length}")
    print(f"   🔢 First 5 values: {item['embedding'][:5]}")

# Metadata
metadata = result['metadata']
print(f"\n\n📹 Video Info:")
print(f"Duration: {metadata['duration']}s")
print(f"URL: {metadata['input_url']}")
print(f"Clip length: {metadata.get('clip_length', 'N/A')}s")
```

---

## Part 3: Similarity Search

Compare embeddings to find similar content using cosine similarity.

### Cell 8: Basic Similarity Comparison

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Store embeddings for retrieval
video_embeddings = {
    'visual_asset': embeddings_data[0]['embedding'],
    'visual_clips': [embeddings_data[1]['embedding'], embeddings_data[2]['embedding']],
    'transcription_asset': embeddings_data[3]['embedding'],
    'audio_asset': embeddings_data[5]['embedding']
}

# Query similarity function
def find_similar_segment(query_embedding, stored_embeddings):
    """Calculate cosine similarity between query and stored embeddings"""
    query_vec = np.array(query_embedding).reshape(1, -1)

    similarities = {}
    for key, emb in stored_embeddings.items():
        if isinstance(emb, list) and isinstance(emb[0], list):
            # Handle clip-level embeddings
            for idx, clip_emb in enumerate(emb):
                emb_vec = np.array(clip_emb).reshape(1, -1)
                sim = cosine_similarity(query_vec, emb_vec)[0][0]
                similarities[f"{key}_{idx}"] = sim
        else:
            emb_vec = np.array(emb).reshape(1, -1)
            sim = cosine_similarity(query_vec, emb_vec)[0][0]
            similarities[key] = sim

    return similarities

# Example: Compare with itself (should give score ~1.0)
similarities = find_similar_segment(
    query_embedding=video_embeddings['visual_asset'],
    stored_embeddings=video_embeddings
)

print("🔍 Similarity scores:")
for key, score in sorted(similarities.items(), key=lambda x: x[1], reverse=True):
    print(f"  {key}: {score:.4f}")
```

---

## Part 4: Storage System

Save embeddings to disk for fast retrieval without re-processing videos.

### Cell 9: EmbeddingStore Class with Auto-Fetch

```python
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
        query_norm = query_vec / np.linalg.norm(query_vec)
        embeddings_norm = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        similarities = np.dot(embeddings_norm, query_norm.T).flatten()
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]

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

    # Use TASK_ID from previous cells or specify manually
    fetch_task_id = TASK_ID if 'TASK_ID' in locals() and TASK_ID else "695556329f7b96b9f6d09851"

    response = requests.get(
        f"https://api.twelvelabs.io/v1.3/embed-v2/tasks/{fetch_task_id}",
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
        video_id=TASK_ID if 'TASK_ID' in locals() and TASK_ID else 'unknown',
        embedding=embeddings_data[0]['embedding'],
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

print("\n✅ Storage system ready! Use search_numpy(query_embedding) to search.")
```

---

## Part 5: Text-to-Video Semantic Search

Search videos using natural language queries by converting text to embeddings.

### Cell 10: Text-to-Video Search Function

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def text_to_video_search(query_text, video_embeddings_dict, top_k=3):
    """
    Search videos using a text query.

    Args:
        query_text: Natural language search query
        video_embeddings_dict: Dictionary with video embeddings
        top_k: Number of top results to return

    Returns:
        List of top matching videos with similarity scores
    """
    # Step 1: Convert text query to embedding
    text_response = requests.post(
        "https://api.twelvelabs.io/v1.3/embed-v2",
        headers={"x-api-key": apiKey},
        json={
            "input_type": "text",
            "model_name": "marengo3.0",
            "text": {"input_text": query_text}
        },
    )

    if text_response.status_code != 200:
        print(f"Error creating text embedding: {text_response.text}")
        return []

    query_embedding = np.array(text_response.json()['data'][0]['embedding'])

    # Step 2: Compare with video embeddings
    results = []
    for video_id, embeddings in video_embeddings_dict.items():
        if isinstance(embeddings, dict):
            for emb_type, emb_data in embeddings.items():
                # Check if it's a list of embeddings (clips)
                if isinstance(emb_data, list) and len(emb_data) > 0:
                    # Check if first element is itself a list (clip embeddings)
                    if isinstance(emb_data[0], list):
                        for idx, clip_emb in enumerate(emb_data):
                            clip_array = np.array(clip_emb)
                            if clip_array.ndim == 1 and clip_array.shape[0] == 512:
                                sim = cosine_similarity(
                                    query_embedding.reshape(1, -1),
                                    clip_array.reshape(1, -1)
                                )[0][0]
                                results.append({
                                    'video_id': video_id,
                                    'type': f"{emb_type}_clip_{idx}",
                                    'similarity': float(sim)
                                })
                    else:
                        # It's a single embedding
                        emb_array = np.array(emb_data)
                        if emb_array.ndim == 1 and emb_array.shape[0] == 512:
                            sim = cosine_similarity(
                                query_embedding.reshape(1, -1),
                                emb_array.reshape(1, -1)
                            )[0][0]
                            results.append({
                                'video_id': video_id,
                                'type': emb_type,
                                'similarity': float(sim)
                            })

    # Step 3: Sort by similarity and return top K
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:top_k]

# Prepare video embeddings dictionary
if 'embeddings_data' in locals() and len(embeddings_data) > 0:
    # Show video info
    print(f"📹 Searching video: {result['metadata']['input_url']}\n")

    video_emb_dict = {
        TASK_ID if 'TASK_ID' in locals() and TASK_ID else 'video_1': {
            'visual_asset': embeddings_data[0]['embedding'],
            'visual_clips': [embeddings_data[1]['embedding'], embeddings_data[2]['embedding']],
            'audio_asset': embeddings_data[5]['embedding']
        }
    }

    # Search with a text query
    query = "person walking or moving"
    search_results = text_to_video_search(query, video_emb_dict, top_k=5)

    print(f"🔍 Search results for: '{query}'")
    print("-" * 60)
    for i, result in enumerate(search_results, 1):
        print(f"{i}. Video: {result['video_id']}")
        print(f"   Type: {result['type']}")
        print(f"   Similarity: {result['similarity']:.4f}")

        # Show timestamps if available
        if 'clip' in result['type']:
            clip_idx = int(result['type'].split('_')[-1])
            for emb in embeddings_data:
                if emb['embedding_scope'] == 'clip' and embeddings_data.index(emb) == clip_idx + 1:
                    print(f"   ⏱️  Time: {emb['start_sec']}s - {emb['end_sec']}s")
                    break
        print()
else:
    print("⚠ Run the embeddings retrieval cell first")
```

---

## Summary & Next Steps

**What you've accomplished:**

1. ✅ **Text embeddings** - Convert text to vector representations
2. ✅ **Video embeddings** - Extract embeddings from videos (sync & async)
3. ✅ **Similarity search** - Compare embeddings using cosine similarity
4. ✅ **Storage system** - Save/load embeddings with `EmbeddingStore` class
5. ✅ **Text-to-video search** - Search videos using natural language queries

**Potential enhancements:**

- **Batch processing**: Process multiple videos at once
- **Hybrid search**: Combine visual, audio, and transcription with weighted scores
- **Vector databases**: Use FAISS, Pinecone, or Weaviate for large-scale search
- **Visualization**: Plot embeddings in 2D/3D space using t-SNE or UMAP
- **Real-time indexing**: Continuously index new videos and update search index
