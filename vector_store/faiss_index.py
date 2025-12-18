import pickle
import faiss
import numpy as np

def build_faiss_index():
    print("="*60)
    print("Building FAISS Vector Index")
    print("="*60)
    
    # Load embeddings
    with open('embeddings.pkl', 'rb') as f:
        embeddings_data = pickle.load(f)
    
    print(f"Loaded {len(embeddings_data)} embeddings")
    
    # Extract vectors
    vectors = np.array([item['embedding'] for item in embeddings_data]).astype('float32')
    
    print(f"Vector shape: {vectors.shape}")
    
    # Build FAISS index (using L2 distance)
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)
    
    print(f"✅ Added {index.ntotal} vectors to FAISS index")
    
    # Save index
    faiss.write_index(index, 'faiss_index.bin')
    print("✅ Saved FAISS index to faiss_index.bin")
    
    # Save metadata separately (for quick lookup)
    metadata = [{
        'id': item['id'],
        'name': item['name'],
        'url': item['url'],
        'test_type': item['test_type'],
        'test_type_full': item['test_type_full']
    } for item in embeddings_data]
    
    with open('metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)
    
    print("✅ Saved metadata to metadata.pkl")
    print("\n✅ Vector store ready!")

if __name__ == "__main__":
    build_faiss_index()