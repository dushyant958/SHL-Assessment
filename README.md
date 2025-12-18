Perfect, bro—I can see the screenshot. Based on all the context you gave, here’s how we can structure your README.md. I’ll make it **professional, complete, and aligned with your repo structure**, covering all key points like project overview, data, pipeline, API, frontend, embeddings, evaluation, and usage instructions.

---

# SHL Assessment Recommendation System

## Project Overview

This project implements an **intelligent SHL Assessment Recommendation System** that helps hiring managers and recruiters find the most relevant assessments for any given job description or natural language query. The system leverages **LLM-based query understanding (Groq Llama 3.1 8B instant)** and **pre-computed embeddings** stored in **FAISS** for fast and accurate retrieval.

The system was designed to handle real-world scenarios where queries can include multiple hard and soft skills, ensuring that recommendations are **balanced across test types** (e.g., Knowledge, Personality, Ability).

---

## Repository Structure

```
.
├── api/
│   ├── app.py                # FastAPI backend for recommendation
│   └── retrieval_engine.py   # Core retrieval engine using Groq + FAISS
├── data/
│   ├── assessments_final.json    # Raw scraped assessment data
│   ├── processed_assessments.json # Preprocessed JSON for embedding
│   └── urls.json                  # URLs collected from scraping
├── embeddings/
│   └── embeddings.py          # Script to generate embeddings (Gemini used previously)
├── evaluation/
│   ├── evaluation.py          # Script to evaluate recommendation accuracy
│   ├── SHL_submission.csv  # Output results from evaluation
│   └── Gen_AI Dataset.csv     # Labeled train/test data
├── frontend/
│   └── app.py                 # Streamlit frontend to query recommendations
├── scraper/
│   ├── collect_urls.py        # Script to collect assessment URLs
│   └── scrape_details.py      # Script to scrape individual assessment details
├── vector_store/
│   ├── faiss_index.bin
│   ├── faiss_index.py
│   ├── embeddings.pkl
│   └── metadata.pkl
├── preprocessing.py           # Preprocessing raw JSON into structured JSON
├── requirements.txt
└── README.md
```

---

## Dataset

* **Raw data source**: SHL product catalog [SHL Product Catalog](https://www.shl.com/solutions/products/product-catalog/)
* **Number of assessments scraped**: 377 Individual Test Solutions (excluding pre-packaged job solutions)
* **Files used**:

  * `assessments_final.json`: Raw scraped data
  * `processed_assessments.json`: Cleaned and structured data ready for embedding
  * `metadata.pkl`: Metadata for FAISS retrieval
  * `embeddings.pkl`: Precomputed embeddings

> Note: Embeddings were originally generated using **Gemini API**. Due to API exhaustion, **Groq Llama 3.1 8B instant** is used for query understanding only, ensuring retrieval works with precomputed embeddings.

---

## Data Preprocessing

The `preprocessing.py` script:

* Cleans text fields (name, description, job levels, languages)
* Normalizes whitespace
* Converts test type codes and generates a canonical **embedding text** for each assessment
* Saves the processed assessments as `processed_assessments.json`

---

## Embeddings

* Generated using **Gemini embeddings model** (expired for later use)
* Embeddings stored in FAISS for **fast vector search**
* Shape of embeddings and vector store ensures **efficient similarity search**
* `embeddings.py` script generates embeddings for raw data

> **Important**: Only query embeddings are now generated using the same dimensional model (`SentenceTransformer` equivalent) to match precomputed embeddings.

---

## Retrieval Engine

Implemented in `api/retrieval_engine.py`:

* Uses **FAISS vector search** for candidate assessments
* Uses **Groq Llama 3.1 8B instant** for **query intent extraction**:

  * Hard skills
  * Soft skills
  * Required test types (Knowledge, Ability, Personality, etc.)
* Balances recommendations across test types
* Returns top 5–10 recommendations with:

  * Assessment Name
  * URL
  * Test Type
  * Similarity Score

---

## API

**Backend**: FastAPI (`api/app.py`)

Endpoints:

1. **Health Check**

   * `GET /health`
   * Returns: `{"status": "ok"}`

2. **Assessment Recommendation**

   * `POST /recommend`
   * Body: `{"query": "<job description text>"}`
   * Returns: List of top 5–10 recommended assessments (JSON)

   ```json
   [
     {
       "assessment_name": "Adobe Photoshop CC",
       "assessment_url": "https://www.shl.com/...",
       "test_type": "K",
       "similarity_score": 0.87
     }
   ]
   ```

---

## Frontend

**Streamlit app** (`frontend/app.py`):

* Accepts **natural language query** input
* Calls FastAPI `/recommend` endpoint
* Displays recommended assessments in **tabular format**
* Highlights **test type balance**

---

## Evaluation

* `evaluation/evaluation.py` compares recommendations against **labeled train/test queries**
* Metrics computed:

  * **Mean Recall@10** (how many relevant assessments appear in top 10)
  * **Balanced recommendations across test types**
* Output saved to `evaluation_result.csv`

---

## How to Run

1. **Set up environment**:

```bash
python -m venv venv
source venv/bin/activate        # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. **Run API**:

```bash
cd api
uvicorn app:app --reload
```

3. **Run Frontend**:

```bash
cd frontend
streamlit run app.py
```

4. **Test API**:

```bash
POST http://localhost:8000/recommend
{
    "query": "Looking for Java backend developer with strong communication skills"
}
```

5. **Evaluate system**:

```bash
python evaluation/evaluation.py
```

---

## Notes

* Query embeddings **must match the dimensionality** of precomputed embeddings.
* Adding fake assessments to increase dataset size is **strongly discouraged**. Stick with real scraped data.
* Groq Llama is only for **query understanding**, not for embeddings.

---

## References

* SHL Product Catalog: [https://www.shl.com/solutions/products/product-catalog/](https://www.shl.com/solutions/products/product-catalog/)
* FAISS: [https://faiss.ai/](https://faiss.ai/)
* Groq Llama 3.1: [https://www.groq.ai/](https://www.groq.ai/)

---
