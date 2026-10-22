import re
import fitz
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Resume Screening System", page_icon="📄", layout="wide")
st.title("📄 AI-Powered Resume Screening System")
st.write("Upload PDF resumes and compare them with a job description. Scores are indicators for human review, not hiring decisions.")

with st.sidebar:
    st.header("How it works")
    st.markdown("1. Enter a job description.\n2. Add required skills.\n3. Upload PDF resumes.\n4. Review results and export CSV.")
    st.warning("Only process resumes you are authorized to use. Review all results manually.")

job_description = st.text_area("Paste the job description", height=160, placeholder="Example: Seeking a Python developer with SQL, APIs, Git, data analysis, and communication skills.")
skills_text = st.text_input("Required skills (comma-separated)", "Python, SQL, Machine Learning, Data Analysis, Pandas, NumPy, Git, REST API, Communication")
skills = [s.strip() for s in skills_text.split(",") if s.strip()]
files = st.file_uploader("Upload candidate resumes (PDF)", type=["pdf"], accept_multiple_files=True)

def extract_text(uploaded):
    doc = fitz.open(stream=uploaded.getvalue(), filetype="pdf")
    text = "\n".join(page.get_text("text") for page in doc).strip()
    doc.close()
    return text

def norm(text):
    return re.sub(r"\s+", " ", text.lower()).strip()

def skills_found(text, skill_list):
    t = norm(text)
    found = []
    for skill in skill_list:
        s = norm(skill)
        if s and re.search(r"(?<!\w)" + re.escape(s) + r"(?!\w)", t):
            found.append(skill)
    return found

if st.button("🔍 Analyze resumes", type="primary", use_container_width=True):
    if not job_description.strip():
        st.error("Please enter a job description.")
    elif not files:
        st.error("Please upload at least one PDF resume.")
    else:
        readable, errors = [], []
        for f in files:
            try:
                text = extract_text(f)
                if len(text) < 20:
                    errors.append(f"{f.name}: No selectable text found; this may be a scanned PDF.")
                else:
                    readable.append((f.name, text))
            except Exception as e:
                errors.append(f"{f.name}: Could not read PDF ({e}).")
        for e in errors:
            st.warning(e)

        if readable:
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=20000)
            matrix = vectorizer.fit_transform([job_description] + [t for _, t in readable])
            similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
            rows = []
            for (filename, text), sim in zip(readable, similarities):
                found = skills_found(text, skills)
                missing = [s for s in skills if s not in found]
                coverage = len(found) / len(skills) if skills else 0
                score = round((float(sim) * 0.60 + coverage * 0.40) * 100, 1)
                rows.append({
                    "Resume": filename,
                    "Match score (%)": min(100, score),
                    "Skills found": ", ".join(found) if found else "None detected",
                    "Skills to check": ", ".join(missing) if missing else "None from list",
                    "Text similarity (%)": round(float(sim) * 100, 1),
                    "Skill coverage (%)": round(coverage * 100, 1),
                })
            results = pd.DataFrame(rows).sort_values("Match score (%)", ascending=False).reset_index(drop=True)
            st.subheader("Screening results")
            st.caption("Heuristic score based on TF-IDF text similarity and exact skill phrases. It is not a probability of job success or a recommendation to hire/reject.")
            a, b, c = st.columns(3)
            a.metric("Resumes analyzed", len(results))
            b.metric("Skills listed", len(skills))
            c.metric("Highest score", f"{results['Match score (%)'].max():.1f}%")
            st.dataframe(results, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download CSV report", results.to_csv(index=False).encode("utf-8-sig"), "resume_screening_results.csv", "text/csv", use_container_width=True)
            st.subheader("Candidate details")
            for _, row in results.iterrows():
                with st.expander(f"{row['Resume']} — {row['Match score (%)']}% heuristic match"):
                    st.write("**Skills detected:**", row["Skills found"])
                    st.write("**Skills to check manually:**", row["Skills to check"])
                    st.write("**Text similarity:**", f"{row['Text similarity (%)']}%")
                    st.write("**Skill coverage:**", f"{row['Skill coverage (%)']}%")

st.divider()
st.caption("Privacy: this code does not intentionally save uploaded resumes. For production, add authentication, access controls, retention rules, security testing, and consent. Never use this prototype as the sole basis for employment decisions.")
