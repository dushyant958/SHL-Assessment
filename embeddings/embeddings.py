# embedding/generate_embeddings.py

import json
import os
from google import genai
from google.genai import types
import numpy as np
import pickle

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_embeddings(assessments):
    print("="*60)
    print("PHASE 3: Generate Embeddings")
    print("="*60)
    
    embeddings_data = []
    
    for idx, assessment in enumerate(assessments):
        try:
            # FIXED: Changed 'content' to 'contents'
            response = client.models.embed_content(
                model='models/text-embedding-004',
                contents=assessment['embedding_text']
            )
            
            embedding_vector = response.embeddings[0].values
            
            embeddings_data.append({
                'id': idx,
                'name': assessment['name'],
                'url': assessment['url'],
                'test_type': assessment['test_type'],
                'test_type_full': assessment['test_type_full'],
                'embedding': embedding_vector,
                'embedding_text': assessment['embedding_text']
            })
            
            if (idx + 1) % 10 == 0:
                print(f"  Generated {idx + 1}/{len(assessments)} embeddings...")
                
        except Exception as e:
            print(f"  ⚠ Error on assessment {idx}: {e}")
            continue
    
    print(f"\n✅ Generated {len(embeddings_data)} embeddings")
    return embeddings_data

def save_embeddings(embeddings_data):
    os.makedirs('../vector_store', exist_ok=True)
    
    with open('../vector_store/embeddings.pkl', 'wb') as f:
        pickle.dump(embeddings_data, f)
    
    print(f"✅ Saved embeddings to vector_store/embeddings.pkl")

def main():
    with open('../data/processed_assessments.json', 'r', encoding='utf-8') as f:
        assessments = json.load(f)
    
    print(f"Loaded {len(assessments)} assessments")
    
    embeddings_data = generate_embeddings(assessments)
    save_embeddings(embeddings_data)
    
    print("\n✅ Phase 3 Complete!")

if __name__ == "__main__":
    main()