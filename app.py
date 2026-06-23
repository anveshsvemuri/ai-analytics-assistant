import streamlit as st

st.set_page_config(
    page_title="AI Analytics Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Analytics Assistant")

st.subheader("Welcome!")

st.write("""
This application will allow users to:

- Upload CSV files
- Ask questions in natural language
- Generate SQL automatically
- Visualize KPIs
- Receive AI-powered business insights
""")

st.success("Day 1 setup completed!")