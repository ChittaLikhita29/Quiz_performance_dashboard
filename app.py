import streamlit as st
from PIL import Image

# Page configuration
st.set_page_config(page_title="Quiz App", layout="wide")



# Title
st.markdown("## 🎓 Welcome to the Online Quiz Platform")

# Load local banner image
banner = Image.open("quiz_bg.png")
banner_resized = banner.resize((700, 300))  # width=300, height=200

st.image(banner_resized)

# Features in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.success("📚 Multiple Quiz Sets")
    st.info("⏱ Timer-Based Questions")

with col2:
    st.success("✅ Auto Score Evaluation")
    st.info("💾 Results Stored Automatically")

with col3:
    st.success("📊 Performance Dashboard")
    st.info("📈 Detailed Analysis")

# Info box
st.info("📌 Use the menu on the **left sidebar** to start the quiz or view the analysis.")
