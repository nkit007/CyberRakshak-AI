import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="CyberRakshak AI", page_icon="🛡️", layout="wide")

CATEGORY_RULES = {
    "Cyber Fraud / UPI": ["upi", "fraud", "scam", "otp", "bank", "transaction", "account hacked", "debit", "credit card"],
    "Cyber Bullying / Harassment": ["bullying", "harassment", "threat", "blackmail", "abuse", "morphed photo", "stalking"],
    "Social Media Complaint": ["instagram", "facebook", "whatsapp", "fake profile", "social media", "impersonation"],
    "Malware / Hacking": ["malware", "virus", "hacked", "hacking", "ransomware", "unauthorized access", "computer locked"],
    "Identity Theft": ["identity theft", "aadhaar", "pan card", "personal data", "stolen identity"],
    "Other": []
}

POSITIVE_WORDS = ["thank", "resolved", "good", "helpful", "happy", "appreciate", "safe"]
NEGATIVE_WORDS = ["fraud", "scam", "stolen", "threat", "blackmail", "urgent", "lost", "hacked", "angry", "fear", "harassment"]

def classify_complaint(text):
    cleaned = re.sub(r"\s+", " ", str(text).lower()).strip()
    scores = {
        category: sum(1 for keyword in keywords if keyword in cleaned)
        for category, keywords in CATEGORY_RULES.items()
    }
    category = max(scores, key=scores.get)
    if scores[category] == 0:
        category = "Other"

    negative = sum(1 for word in NEGATIVE_WORDS if word in cleaned)
    positive = sum(1 for word in POSITIVE_WORDS if word in cleaned)
    if negative > positive:
        sentiment = "Negative"
    elif positive > negative:
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    urgent_terms = ["urgent", "large amount", "money stolen", "blackmail", "threat", "account hacked", "ransomware"]
    high_priority = any(term in cleaned for term in urgent_terms)
    priority = "High" if high_priority else ("Medium" if category != "Other" else "Low")

    departments = {
        "Cyber Fraud / UPI": "Cyber Crime / Financial Fraud Cell",
        "Cyber Bullying / Harassment": "Cyber Crime / Women & Child Safety Cell",
        "Social Media Complaint": "Cyber Crime / Social Media Cell",
        "Malware / Hacking": "Cyber Security / Digital Forensics Team",
        "Identity Theft": "Cyber Crime / Identity Theft Cell",
        "Other": "General Help Desk"
    }

    return {
        "Category": category,
        "Sentiment": sentiment,
        "Priority": priority,
        "Suggested Department": departments[category]
    }

st.title("🛡️ CyberRakshak AI")
st.caption("Cyber complaint intelligence demo • Prototype for hackathon")

with st.sidebar:
    st.header("About")
    st.write("This prototype uses transparent keyword rules to categorize complaint text.")
    st.warning("Demo only: it is not a trained AI model and does not replace official cybercrime reporting.")
    st.write("Do not enter passwords, OTPs, bank PINs, or other sensitive information.")

tab1, tab2 = st.tabs(["Analyze Complaint", "Dashboard / CSV"])

with tab1:
    st.subheader("Analyze a complaint")
    complaint = st.text_area(
        "Complaint text",
        placeholder="Example: Someone called me and took money from my UPI account...",
        height=150
    )
    if st.button("Analyze", type="primary"):
        if not complaint.strip():
            st.error("Please enter a complaint first.")
        else:
            result = classify_complaint(complaint)
            st.success("Analysis complete")
            c1, c2, c3 = st.columns(3)
            c1.metric("Category", result["Category"])
            c2.metric("Sentiment", result["Sentiment"])
            c3.metric("Priority", result["Priority"])
            st.info("Suggested Department: " + result["Suggested Department"])
            st.caption("This is an automated suggestion. A human reviewer should verify it.")

with tab2:
    st.subheader("Analyze a list of complaints")
    uploaded = st.file_uploader("Upload CSV with a 'complaint' column", type=["csv"])
    if uploaded is not None:
        try:
            data = pd.read_csv(uploaded)
            if "complaint" not in data.columns:
                st.error("CSV must contain a column named 'complaint'.")
            else:
                results = data["complaint"].fillna("").apply(classify_complaint).apply(pd.Series)
                output = pd.concat([data, results], axis=1)
                st.dataframe(output, use_container_width=True)
                st.subheader("Summary")
                st.bar_chart(output["Category"].value_counts())
                st.write("Priority counts")
                st.bar_chart(output["Priority"].value_counts())
                csv_bytes = output.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download analyzed CSV",
                    data=csv_bytes,
                    file_name="cyberrakshak_analyzed_complaints.csv",
                    mime="text/csv"
                )
        except Exception as exc:
            st.error(f"Could not read this CSV: {exc}")
    else:
        st.write("Upload a CSV to see category and priority summaries.")

st.divider()
st.caption("CyberRakshak AI • Built as an educational hackathon prototype • " + datetime.now().strftime("%d %b %Y"))
