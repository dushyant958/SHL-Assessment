# frontend/app.py

import streamlit as st
import requests

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")

st.title("SHL Assessment Recommendation System")
st.markdown("Enter a job description or query to get personalized assessment recommendations")

# API endpoint
API_URL = "https://shl-assessment-iqkp.onrender.com"

# Input
query = st.text_area(
    "Enter Job Description or Query:",
    placeholder="e.g., Looking for a Java developer with strong communication skills and leadership experience",
    height=150
)

if st.button("Get Recommendations", type="primary"):
    if not query.strip():
        st.error("Please enter a query")
    else:
        with st.spinner("Analyzing query and finding best assessments..."):
            try:
                # Call API
                response = requests.post(
                    f"{API_URL}/recommend",
                    json={"query": query}
                )
                
                if response.status_code == 200:
                    recommendations = response.json()
                    
                    st.success(f"Found {len(recommendations)} recommendations")
                    
                    # Display results in table
                    st.markdown("### 📋 Recommended Assessments")
                    
                    for i, rec in enumerate(recommendations, 1):
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{i}. {rec['assessment_name']}**")
                            with col2:
                                st.link_button("View Details", rec['assessment_url'])
                            st.divider()
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built for SHL GenAI Assessment System")