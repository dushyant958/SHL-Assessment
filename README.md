# SHL Assessment Recommendation System

> ⚠️ **Important Deployment Notice (Read First)**
>
> This is a **heavy RAG-based application** involving LLM inference + vector search. The **backend is deployed on Render (free tier ~512 MB RAM)** and the **frontend on Streamlit Cloud**. Due to limited memory and compute on free tiers, **responses may take several minutes or may feel slow/unresponsive**.
>
> This is a **deployment limitation, not a system design issue**.
>
> • The application runs **fast and smoothly on a local machine**.
> • There is **no free-tier hosting platform** that currently supports heavy RAG workloads efficiently.
> • To address this, a **working proof video** demonstrating real-time performance has been uploaded to the GitHub repository.

---

## Project Overview

This project implements an **intelligent SHL Assessment Recommendation System** that helps hiring managers and recruiters find the most relevant SHL assessments for a given **job description or natural language query**.

Instead of relying on keyword matching, the system understands **intent, skills, and role requirements**, then retrieves **semantically relevant assessments** while maintaining a **balanced mix of test types** (Knowledge, Ability, Personality, etc.).

The system is built using:

• **LLM-powered query understanding (Groq – Llama 3.1 8B Instant)**
• **Pre-computed embeddings stored in FAISS** for fast similarity search
• **RAG-style retrieval pipeline** optimized for real-world recruiter queries

---

## Key Features

• Natural language job description understanding
• Semantic assessment retrieval using FAISS
• Intelligent skill extraction (hard + soft skills) via LLM
• Balanced recommendations across assessment types
• Precomputed embeddings for low-latency vector search
• End-to-end pipeline: Scraping → Preprocessing → Embedding → Retrieval → Evaluation
• Clean API-first backend with FastAPI
• Interactive Streamlit frontend for recruiters

---

## System Architecture

The system consists of **two independent components**:

### Backend (Deployed on Render)

• FastAPI-based REST service
• FAISS vector search engine
• Groq Llama 3.1 for query intent extraction
• Handles retrieval logic, scoring, and ranking

> Render was chosen over Vercel because **Vercel is not suitable for long-running RAG inference workloads**.

### Frontend (Deployed on Streamlit Cloud)

• Lightweight Streamlit UI
• Sends natural language queries to backend API
• Displays ranked assessment recommendations
• Highlights assessment type diversity

---

## System Block Diagram

> 📊 **Overall System Flow Diagram**

```
[PLACE BLOCK DIAGRAM IMAGE HERE]
```

This diagram should illustrate:
• URL scraping and data collection
• Preprocessing and embedding generation
• FAISS vector storage
• Query understanding via LLM
• Retrieval and ranking
• API → Frontend interaction

---

## Working Prototype

### UI Screenshot

<img width="1919" height="925" alt="Working Proof Image" src="https://github.com/user-attachments/assets/f16302b1-7f50-4cb1-b44f-9916a5e0ae7a" />

### Working Proof Video

• Demonstrates real-time query → recommendation flow
• Shows fast inference on local machine
• Confirms correct system behavior and output quality

Due to free-tier deployment limitations, a complete **working proof video** has been provided to demonstrate the system’s real-time performance and correctness.

▶️ **Access Working Proof:**
[View Demo Video Folder](https://github.com/dushyant958/SHL-Assessment/tree/main/Working%20Proof)

This video confirms:

• Correct query understanding
• Relevant assessment recommendations
• Balanced test-type outputs

> The video serves as **performance and functionality proof**.

---

## Repository Structure

```
.
├── api/
│   ├── app.py                # FastAPI backend for recommendation
│   ├── retrieval_engine.py   # Core retrieval engine using Groq + FAISS
│   └── vector_store/
│       ├── faiss_index.bin
│       ├── faiss_index.py
│       ├── embeddings.pkl
│       └── metadata.pkl
├── data/
│   ├── assessments.txt            # Raw scraped data from assessment detail pages
│   ├── assessments_final.json     # Cleaned JSON converted from assessments.txt
│   ├── processed_assessments.json # Preprocessed JSON for embedding
│   └── urls.json                  # URLs collected from SHL catalog pages
├── embeddings/
│   └── embeddings.py          # Script to generate embeddings (Gemini used previously)
├── evaluation/
│   ├── evaluation.py          # Script for recall-based evaluation and re-ranking
│   ├── SHL_submission.csv     # Final submission file provided to SHL
│   └── Gen_AI Dataset.csv     # Labeled ground-truth dataset used for evaluation
├── frontend/
│   └── app.py                 # Streamlit frontend to query recommendations
├── scraper/
│   ├── collect_urls.py        # Script to collect assessment URLs (32 pages)
│   └── scrape_details.py      # Script to scrape assessment details from each URL
├── preprocessing.py           # Preprocessing raw JSON into structured JSON
├── requirements.txt
└── README.md
```

---

## Data Collection and Processing Pipeline

The data pipeline follows a **clear, multi-stage process**:

### 1. URL Collection

• SHL product catalog contains **32 pages** of Individual Test Solutions
• `scraper/collect_urls.py` scrapes all assessment URLs
• URLs are stored in `data/urls.json`

### 2. Assessment Data Scraping

• Each URL is visited using `scraper/scrape_details.py`
• Detailed assessment information is extracted
• Raw scraped output is stored in `data/assessments.txt`

### 3. JSON Conversion

• `assessments.txt` is converted into structured JSON
• Output saved as `data/assessments_final.json`

### 4. Preprocessing

• `preprocessing.py` cleans and normalizes data
• Generates canonical text representation for embeddings
• Output saved as `data/processed_assessments.json`

---

## Embeddings

• Generated using **Gemini Embedding Model** during data preparation
• Stored in **FAISS** inside the backend vector store
• Embedding dimensionality is fixed and consistent

> ⚠️ Gemini embeddings are **not regenerated** during runtime due to API exhaustion.

> Only **query embeddings** are generated at inference time, ensuring dimensional compatibility.

---

## Retrieval Engine

Implemented in `api/retrieval_engine.py`:

• FAISS-based semantic retrieval
• LLM-driven query intent extraction using Groq Llama 3.1
• Skill identification:
• Hard skills
• Soft skills
• Intelligent ranking with test-type balancing

### Output Includes

• Assessment Name
• Assessment URL
• Test Type
• Similarity Score

---

## API

### Backend Framework

• FastAPI

### Endpoints

**Health Check**

```
GET /health
```

Returns

```
{"status": "ok"}
```

**Assessment Recommendation**

```
POST /recommend
```

Request Body

```
{
  "query": "Looking for a Java backend developer with strong communication skills"
}
```

Response

```
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

• Built with Streamlit
• Accepts free-form recruiter queries
• Displays ranked recommendations in tabular format
• Highlights assessment diversity

---

## Evaluation

• Implemented in `evaluation/evaluation.py`
• Uses **Gen_AI Dataset.csv** as ground-truth labels
• Dataset corresponds to the **official SHL submission format**

### Purpose

• Measure Recall@10
• Validate ranking quality
• Support re-ranking experimentation

Results saved to `SHL_submission.csv`.

---

## How to Run Locally

### Setup

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Backend

```
cd api
uvicorn app:app --reload
```

### Run Frontend

```
cd frontend
streamlit run app.py
```

---

## Final Notes

• This is a **production-style RAG system**, not a toy demo
• Free-tier cloud hosting is the primary performance bottleneck
• Local execution demonstrates intended speed and behavior
• Working proof video compensates for deployment constraints

---

## References

• SHL Product Catalog
• FAISS Vector Search
• Groq Llama 3.1

---
