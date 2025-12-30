import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/recommend"
 

st.set_page_config(
    page_title="SHL Assessment Recommendation Engine",
    layout="centered"
)

st.title("SHL Assessment Recommendation Engine")
st.markdown(
    """
This tool recommends the most relevant **SHL assessments** based on a hiring query.
It uses semantic search and retrieval-augmented generation techniques.
"""
)

query = st.text_area(
    "Describe the role you are hiring for",
    placeholder="Example: Python developer with 4 years experience in AI automation",
    height=120
)

top_k = st.slider("Number of recommendations", 3, 10, 5)

submit = st.button("Get Recommendations")

if submit:
    if not query.strip():
        st.warning("Please enter a job description.")
    else:
        with st.spinner("Finding best assessments..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"query": query, "top_k": top_k},
                    timeout=60
                )

                if response.status_code != 200:
                    st.error("Backend error. Please try again later.")
                else:
                    results = response.json()

                    if not results:
                        st.info("No matching assessments found.")
                    else:
                        st.success("Top Recommended Assessments")

                        for idx, r in enumerate(results, start=1):
                            with st.container():
                                st.markdown(f"### {idx}. {r['name']}")
                                st.markdown(f"**Match Score:** `{round(r['match_score'], 2)}`")

                                st.markdown(
                                    f"""
                                    - **Assessment ID:** `{r['assessment_id']}`
                                    - **Job Levels:** {", ".join(r.get("job_levels", []))}
                                    - **Test Types:** {", ".join(r.get("test_types", []))}
                                    - **Duration (mins):** {r.get("duration_minutes", "N/A")}
                                    """
                                )
                                st.divider()

            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
