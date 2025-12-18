import sys
sys.path.append('../api')

from retrieval_engine import RetrievalEngine
import pandas as pd

def normalize_url(url):
    """
    Normalize URLs by removing /solutions/ path difference
    """
    return url.replace('/solutions/products/', '/products/')

def generate_shl_submission(input_csv='Gen_AI Dataset.csv', output_csv='SHL_submission.csv'):
    """
    Generates a submission CSV in SHL's required format:
    Each query repeated per recommended URL.
    """
    # Load your dataset
    df = pd.read_csv(input_csv)
    
    # Get unique queries
    queries = df['Query'].unique()
    print(f"Loaded {len(queries)} unique queries from {input_csv}")
    
    engine = RetrievalEngine()
    
    submission_rows = []

    for idx, query in enumerate(queries, 1):
        print(f"\nQuery {idx}/{len(queries)}: {query[:80]}...")
        
        try:
            recommendations = engine.retrieve(query, top_k=10)
        except Exception as e:
            print(f"   ⚠ Failed to retrieve recommendations: {e}")
            recommendations = []

        if not recommendations:
            print("   ❌ No recommendations found for this query")
            continue

        for rec in recommendations:
            url = normalize_url(rec['assessment_url'])
            submission_rows.append({'Query': query, 'Assessment_url': url})
        
        print(f"   ✅ Added {len(recommendations)} recommendations")
    
    # Save CSV in SHL format
    submission_df = pd.DataFrame(submission_rows)
    submission_df.to_csv(output_csv, index=False)
    print(f"\n✅ Submission CSV saved as {output_csv}")
    print("SHL submission generation complete!")

if __name__ == "__main__":
    generate_shl_submission()
