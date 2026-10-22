import json
import re
import uuid
from pathlib import Path

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

APP_DIR = Path(__file__).parent
FAQ_PATH = APP_DIR / "approved_faq.json"
TICKETS_PATH = APP_DIR / "support_tickets.json"

st.set_page_config(page_title="EdTech AI Support Assistant", page_icon="🎓", layout="centered")

st.title("🎓 EdTech AI Support Assistant")
st.caption("Local prototype • English + Tamil • Answers from approved FAQ only")

# Sensitive topics are escalated before any FAQ retrieval.
ESCALATION_TERMS = [
    "refund", "money back", "billing", "payment", "charged", "invoice",
    "account hacked", "hacked", "password stolen", "security", "unauthorized",
    "பணம் திரும்ப", "பணத்தை திரும்ப", "ரீஃபண்ட்", "கட்டணம்", "பணம் செலுத்த",
    "கணக்கு திருட", "கடவுச்சொல்", "பாதுகாப்பு", "அனுமதியற்ற"
]

def load_faq():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ticket(ticket):
    tickets = []
    if TICKETS_PATH.exists():
        try:
            tickets = json.loads(TICKETS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            tickets = []
    tickets.append(ticket)
    TICKETS_PATH.write_text(
        json.dumps(tickets, ensure_ascii=False, indent=2), encoding="utf-8"
    )

def is_sensitive(question):
    q = question.lower()
    return any(term in q for term in ESCALATION_TERMS)

def build_search_index(faq):
    # Character n-grams work better than word-only matching for mixed-language text.
    corpus = []
    for item in faq:
        corpus.append(item["question"] + " " + " ".join(item.get("keywords", [])))
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), lowercase=True)
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix

faq = load_faq()
vectorizer, faq_matrix = build_search_index(faq)

with st.sidebar:
    st.subheader("Settings")
    language = st.radio("Response language / பதில் மொழி", ["English", "தமிழ்"], horizontal=False)
    st.info("This prototype uses only the local approved_faq.json file. It does not connect to real student accounts.")

st.markdown("Ask about course access, certificates, live classes, or technical issues.")
question = st.chat_input("Type your question / உங்கள் கேள்வியை உள்ளிடவும்")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if is_sensitive(question):
            ticket_id = "SUP-" + uuid.uuid4().hex[:8].upper()
            ticket = {
                "ticket_id": ticket_id,
                "category": "Sensitive request - human review required",
                "question": question,
                "status": "Open",
                "note": "Demo ticket only. Connect a real help-desk system before production."
            }
            save_ticket(ticket)
            if language == "தமிழ்":
                answer = (
                    f"இந்தக் கோரிக்கைக்கு மனித ஆதரவுக் குழுவின் உதவி தேவை. "
                    f"உங்கள் கோரிக்கை உள்ளூர் டெமோ டிக்கெட்டாக பதிவு செய்யப்பட்டது. "
                    f"குறிப்பு எண்: **{ticket_id}**. இது டெமோ மட்டுமே; உண்மையான ஆதரவு குழுவிற்கு இன்னும் அனுப்பப்படவில்லை."
                )
            else:
                answer = (
                    f"This request needs review by a human support agent. "
                    f"A local demo ticket was created: **{ticket_id}**. "
                    "This is only stored on this computer; it has not been sent to a real support team."
                )
            st.warning(answer)
        else:
            q_vec = vectorizer.transform([question])
            scores = cosine_similarity(q_vec, faq_matrix).flatten()
            best_idx = int(scores.argmax())
            best_score = float(scores[best_idx])
            threshold = 0.12

            if best_score < threshold:
                if language == "தமிழ்":
                    answer = "அங்கீகரிக்கப்பட்ட உதவி ஆவணங்களில் இதற்கான உறுதியான பதில் கிடைக்கவில்லை. தயவுசெய்து ஆதரவு குழுவைத் தொடர்புகொள்ளவும்."
                else:
                    answer = "I couldn't find a reliable answer in the approved help documents. Please contact the support team."
                st.info(answer)
            else:
                item = faq[best_idx]
                answer = item["answer_ta"] if language == "தமிழ்" else item["answer_en"]
                st.markdown(answer)
                st.caption(f"Source: {item['source']} • Retrieval match: {best_score:.2f}")
        st.session_state.messages.append({"role": "assistant", "content": answer})

st.divider()
st.caption("Student privacy demo: this app does not retrieve student records. Do not enter passwords, card numbers, or other sensitive personal data.")
