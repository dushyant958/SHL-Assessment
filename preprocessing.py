# data/preprocess_assessments.py

import json
import re

def clean_text(text):
    """
    Cleans text - removes extra whitespace, normalizes
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing
    text = text.strip()
    return text

def create_embedding_text(assessment):
    """
    Creates the canonical text block for embedding.
    This is CRITICAL for good Recall@10.
    """
    parts = []
    
    # Assessment name
    parts.append(f"Assessment: {assessment['name']}")
    
    # Test types
    test_types_full = assessment.get('test_type_full', '')
    if test_types_full:
        parts.append(f"Test Types: {test_types_full}")
    
    # Description (most important)
    if assessment.get('description'):
        parts.append(f"Description: {assessment['description']}")
    
    # Job levels
    if assessment.get('job_levels'):
        levels = assessment['job_levels']
        if isinstance(levels, list):
            levels = ', '.join(levels)
        parts.append(f"Job Levels: {levels}")
    
    # Languages
    if assessment.get('languages'):
        langs = assessment['languages']
        if isinstance(langs, list):
            langs = ', '.join(langs)
        parts.append(f"Languages: {langs}")
    
    # Duration
    if assessment.get('assessment_length'):
        parts.append(f"Duration: {assessment['assessment_length']}")
    
    # Remote testing
    if assessment.get('remote_testing'):
        parts.append(f"Remote Testing: {assessment['remote_testing']}")
    
    # Join all parts
    embedding_text = ' | '.join(parts)
    
    return clean_text(embedding_text)

def preprocess_assessments():
    """
    Main preprocessing function
    """
    print("="*60)
    print("PHASE 2: Data Preprocessing")
    print("="*60)
    
    # ✅ FIXED INPUT FILE PATH
    input_path = r"C:\Users\Hrutam Sabale\Documents\Dushyant SHL AI Research Intern\Code\data\assessments_final.json"

    with open(input_path, 'r', encoding='utf-8') as f:
        raw_assessments = json.load(f)
    
    print(f"\nLoaded {len(raw_assessments)} raw assessments")
    
    processed_assessments = []
    
    for idx, assessment in enumerate(raw_assessments):
        processed = {
            'name': clean_text(assessment['name']),
            'url': assessment['url'],
            'description': clean_text(assessment.get('description', '')),
            'test_type': assessment['test_type'],
            'test_type_full': assessment.get('test_type_full', ''),
            'job_levels': assessment.get('job_levels', []),
            'languages': assessment.get('languages', []),
            'assessment_length': assessment.get('assessment_length', ''),
            'remote_testing': assessment.get('remote_testing', 'Unknown'),
            'embedding_text': create_embedding_text(assessment)
        }
        
        processed_assessments.append(processed)
        
        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(raw_assessments)}...")
    
    # Output stays local (same folder as script)
    with open('processed_assessments.json', 'w', encoding='utf-8') as f:
        json.dump(processed_assessments, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(processed_assessments)} processed assessments")
    print("✅ Created embedding_text for each assessment")
    
    print("\n" + "="*60)
    print("SAMPLE EMBEDDING TEXT:")
    print("="*60)
    print(processed_assessments[0]['embedding_text'][:300] + "...")

if __name__ == "__main__":
    preprocess_assessments()
