import sys
sys.path.append('../api')

from retrieval_engine import RetrievalEngine
import pandas as pd

def normalize_url(url):
    """
    Normalize URLs by removing /solutions/ path difference
    """
    return url.replace('/solutions/products/', '/products/')

def calculate_recall_at_k(predicted_urls, ground_truth_urls, k=10):
    """
    Calculates Recall@K with URL normalization
    """
    predicted_set = set(normalize_url(url) for url in predicted_urls[:k])
    ground_truth_set = set(normalize_url(url) for url in ground_truth_urls)
    
    hits = len(predicted_set.intersection(ground_truth_set))
    total_relevant = len(ground_truth_set)
    
    if total_relevant == 0:
        return 0.0
    
    recall = hits / total_relevant
    return recall

def evaluate_system():
    print("="*60)
    print("PHASE 7: EVALUATION - Recall@10")
    print("="*60)
    
    # Fixed path to actual CSV
    df = pd.read_csv('Gen_AI Dataset.csv')
    queries_data = df.groupby('Query')['Assessment_url'].apply(list).to_dict()
    
    print(f"\nLoaded {len(queries_data)} unique queries")
    print(f"Total ground truth pairs: {len(df)}")
    
    engine = RetrievalEngine()
    
    results = []
    
    for idx, (query, ground_truth_urls) in enumerate(queries_data.items(), 1):
        print(f"\n{'='*60}")
        print(f"Query {idx}/{len(queries_data)}")
        print(f"{'='*60}")
        print(f"Query: {query[:80]}...")
        print(f"Ground truth count: {len(ground_truth_urls)}")
        
        max_retries = 3
        recommendations = None
        
        for attempt in range(max_retries):
            try:
                recommendations = engine.retrieve(query, top_k=10)
                break
            except Exception as e:
                print(f"   ⚠ Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print(f"   ❌ Skipping query after {max_retries} attempts")
                    recommendations = []
        
        if not recommendations:
            results.append({
                'query': query,
                'ground_truth_count': len(ground_truth_urls),
                'predicted_count': 0,
                'matches': 0,
                'recall@10': 0.0
            })
            continue
        
        predicted_urls = [rec['assessment_url'] for rec in recommendations]
        
        recall = calculate_recall_at_k(predicted_urls, ground_truth_urls, k=10)
        
        print(f"\n📊 Results:")
        print(f"   Predicted URLs: {len(predicted_urls)}")
        print(f"   Recall@10: {recall:.3f}")
        
        predicted_set = set(normalize_url(url) for url in predicted_urls)
        ground_truth_set = set(normalize_url(url) for url in ground_truth_urls)
        matches = predicted_set.intersection(ground_truth_set)
        
        if matches:
            print(f"   ✓ Matched {len(matches)} URLs:")
            for url in matches:
                assessment_name = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
                print(f"     - {assessment_name}")
        
        results.append({
            'query': query,
            'ground_truth_count': len(ground_truth_urls),
            'predicted_count': len(predicted_urls),
            'matches': len(matches),
            'recall@10': recall
        })
    
    avg_recall = sum(r['recall@10'] for r in results) / len(results)
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"\n📊 Average Recall@10: {avg_recall:.3f}")
    print(f"   Total queries evaluated: {len(results)}")
    
    print("\nPer-Query Results:")
    for i, result in enumerate(results, 1):
        print(f"   Query {i}: Recall@10 = {result['recall@10']:.3f} ({result['matches']}/{result['ground_truth_count']} matched)")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv('evaluation_results.csv', index=False)
    print(f"\n✅ Saved detailed results to evaluation_results.csv")
    
    return avg_recall, results

if __name__ == "__main__":
    avg_recall, results = evaluate_system()
    
    print("\n" + "="*60)
    print("EVALUATION COMPLETE!")
    print("="*60)
    print(f"\n🎯 Your Recall@10 score: {avg_recall:.3f}")
    
    if avg_recall >= 0.7:
        print("   ✅ EXCELLENT")
    elif avg_recall >= 0.5:
        print("   ✓ GOOD")
    elif avg_recall >= 0.3:
        print("   ⚠ FAIR")
    else:
        print("   ⚠ NEEDS IMPROVEMENT")


