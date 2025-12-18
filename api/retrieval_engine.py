# api/retrieval_engine.py - REVERT TO THIS (original without BM25)

import os
import pickle
import faiss
import numpy as np
from google import genai
import re
import json
from groq import Groq

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
gemini_client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

class RetrievalEngine:
    def __init__(self):
        # Get absolute path of this file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Correct vector store path (inside api/)
        vector_store_dir = os.path.join(BASE_DIR, 'vector_store')
        index_path = os.path.join(vector_store_dir, 'faiss_index.bin')
        metadata_path = os.path.join(vector_store_dir, 'metadata.pkl')

        # Load FAISS index
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at {index_path}")
        self.index = faiss.read_index(index_path)

        # Load metadata
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found at {metadata_path}")
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)

        print(f"✅ Loaded {len(self.metadata)} assessments from {vector_store_dir}")

    
    def analyze_query_with_llm(self, query_text):
        prompt = f"""Analyze this job query and extract:
1. Hard skills (Java, Python, SQL, etc.)
2. Soft skills (leadership, communication, etc.)
3. Required test types: K (Knowledge), P (Personality), A (Ability)

Query: {query_text}

Respond ONLY in JSON format:
{{"hard_skills": ["skill1"], "soft_skills": ["skill2"], "required_test_types": ["K", "P"]}}"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        text = response.choices[0].message.content
        
        json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        text = text.strip()
        result = json.loads(text)
        return result
    
    def embed_query(self, query_text):
        response = gemini_client.models.embed_content(
            model='models/text-embedding-004',
            contents=query_text
        )
        return np.array(response.embeddings[0].values).astype('float32')
    
    def vector_search(self, query_embedding, top_k=100):
        # Increased from 50 to 100
        query_embedding = query_embedding.reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append({
                    'metadata': self.metadata[idx],
                    'similarity_score': float(1 / (1 + dist))
                })
        
        return results
    
    def balance_by_test_type(self, candidates, required_types, target_count=10):
        """RELAXED balancing - prioritize similarity score more"""
        if not required_types or len(required_types) == 0:
            # No required types - just return top by score
            return sorted(candidates, key=lambda x: x['similarity_score'], reverse=True)[:target_count]
        
        # Get top candidates first
        sorted_candidates = sorted(candidates, key=lambda x: x['similarity_score'], reverse=True)
        
        # Try to balance but don't force it
        balanced = []
        seen_urls = set()
        
        # First pass: get at least 1-2 from each required type if available
        type_counts = {t: 0 for t in required_types}
        min_per_type = 2  # Reduced from strict equal distribution
        
        for candidate in sorted_candidates:
            if len(balanced) >= target_count:
                break
            
            meta = candidate['metadata']
            url = meta['url']
            
            if url in seen_urls:
                continue
            
            # Check if this candidate helps balance
            candidate_types = [t for t in meta['test_type'] if t in required_types]
            
            if candidate_types:
                # Does this help balance?
                needs_balance = any(type_counts[t] < min_per_type for t in candidate_types)
                
                if needs_balance or len(balanced) < target_count:
                    balanced.append(candidate)
                    seen_urls.add(url)
                    
                    for t in candidate_types:
                        if t in type_counts:
                            type_counts[t] += 1
        
        # Second pass: fill remaining slots with best scores regardless of type
        for candidate in sorted_candidates:
            if len(balanced) >= target_count:
                break
            
            url = candidate['metadata']['url']
            if url not in seen_urls:
                balanced.append(candidate)
                seen_urls.add(url)
        
        return balanced[:target_count]
    
    def retrieve(self, query_text, top_k=10):
        print(f"\n🔍 Query: {query_text[:100]}...")
        
        query_analysis = self.analyze_query_with_llm(query_text)
        print(f"📊 Analysis: {query_analysis}")
        
        query_embedding = self.embed_query(query_text)
        
        candidates = self.vector_search(query_embedding, top_k=100)
        print(f"🔎 Found {len(candidates)} candidates")
        
        required_types = query_analysis.get('required_test_types', [])
        balanced_results = self.balance_by_test_type(candidates, required_types, top_k)
        
        print(f"⚖️  Balanced to {len(balanced_results)} results")
        
        recommendations = []
        for result in balanced_results:
            meta = result['metadata']
            recommendations.append({
                'assessment_name': meta['name'],
                'assessment_url': meta['url'],
                'test_type': meta['test_type'],
                'similarity_score': result['similarity_score']
            })
        
        return recommendations

if __name__ == "__main__":
    engine = RetrievalEngine()
    
    test_query = "Looking for Java developer with strong communication skills"
    results = engine.retrieve(test_query, top_k=10)
    
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    for i, rec in enumerate(results, 1):
        print(f"{i}. {rec['assessment_name']}")
        print(f"   Types: {rec['test_type']}")
        print(f"   Score: {rec['similarity_score']:.3f}")
        print()
