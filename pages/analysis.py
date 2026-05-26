import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Quiz Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Quiz Analysis Dashboard")

RESULTS_PATH = "results.csv"

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_results():

    if not os.path.exists(RESULTS_PATH):
        return pd.DataFrame()

    df = pd.read_csv(RESULTS_PATH)

    if df.empty:
        return pd.DataFrame()

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
    df["Percent"] = pd.to_numeric(df["Percent"], errors="coerce")

    df = df.dropna(subset=["Name", "Subject", "Score", "Percent", "Timestamp"])

    return df


results_df = load_results()

# ---------------------------------------------------
# EMPTY CHECK
# ---------------------------------------------------

if results_df.empty:
    st.warning("No quiz results found.")
    st.stop()

# ---------------------------------------------------
# USER SELECTION (FIXED)
# ---------------------------------------------------

all_users = sorted(results_df["Name"].unique())

current_user = st.sidebar.selectbox(
    "Select User for Analysis",
    all_users
)

st.sidebar.success(f"Analyzing: {current_user}")

user_df = results_df[results_df["Name"] == current_user].sort_values("Timestamp")

# ---------------------------------------------------
# MENU
# ---------------------------------------------------

analysis_type = st.sidebar.radio(
    "Select Analysis",
    [
        "Self Analysis",
        "Compare With Others",
        "Leaderboard",
        "Overall Statistics"
    ]
)

# ===================================================
# SELF ANALYSIS
# ===================================================

if analysis_type == "Self Analysis":

    st.header(f"📈 Self Analysis - {current_user}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tests", len(user_df))
    col2.metric("Best Score", int(user_df["Score"].max()))
    col3.metric("Average %", round(user_df["Percent"].mean(), 2))
    col4.metric("Latest Score", int(user_df.iloc[-1]["Score"]))

    st.subheader("📚 Subject-wise Performance")

    subject_avg = user_df.groupby("Subject")["Percent"].mean()

    fig, ax = plt.subplots()
    subject_avg.plot(kind="bar", ax=ax)
    ax.set_ylabel("Average %")
    st.pyplot(fig)

    st.success(f"🏆 Strongest: {subject_avg.idxmax()}")
    st.warning(f"📌 Weakest: {subject_avg.idxmin()}")

# ===================================================
# COMPARE WITH OTHERS
# ===================================================

elif analysis_type == "Compare With Others":

    st.header(f"⚔ Comparison - {current_user}")

    st.info(
        f"""
        Your Average: {round(user_df['Percent'].mean(),2)}%
        Global Average: {round(results_df['Percent'].mean(),2)}%
        """
    )

    st.subheader("📚 Subject-wise Comparison")

    user_subject = user_df.groupby("Subject")["Percent"].mean()
    global_subject = results_df.groupby("Subject")["Percent"].mean()

    comparison_df = pd.DataFrame({
        "Your Score": user_subject,
        "Global Score": global_subject
    }).fillna(0)

    st.dataframe(comparison_df)

    fig, ax = plt.subplots(figsize=(10, 4))
    comparison_df.plot(kind="bar", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ===================================================
# LEADERBOARD
# ===================================================

elif analysis_type == "Leaderboard":

    st.header("🏆 Leaderboard")

    leaderboard = results_df.groupby("Name").agg({
        "Score": "sum",
        "Percent": "mean"
    }).sort_values("Percent", ascending=False).reset_index()

    leaderboard["Rank"] = leaderboard.index + 1

    leaderboard = leaderboard[[
        "Rank",
        "Name",
        "Score",
        "Percent"
    ]]

    st.dataframe(leaderboard, use_container_width=True)

    st.subheader("🏅 Top Performers")

    top = leaderboard.head(10)

    fig, ax = plt.subplots()

    ax.bar(top["Name"], top["Percent"])
    ax.set_ylabel("Average %")
    plt.xticks(rotation=45)

    st.pyplot(fig)

# ===================================================
# OVERALL STATISTICS
# ===================================================

elif analysis_type == "Overall Statistics":

    st.header("🌍 Overall Statistics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Users", results_df["Name"].nunique())
    col2.metric("Tests", len(results_df))
    col3.metric("Highest Score", int(results_df["Score"].max()))
    col4.metric("Global Avg %", round(results_df["Percent"].mean(), 2))

    st.subheader("📚 Subject Popularity")

    subject_count = results_df["Subject"].value_counts()

    fig, ax = plt.subplots()
    subject_count.plot(kind="bar", ax=ax)
    st.pyplot(fig)

    st.subheader("📊 Subject Performance")

    subject_perf = results_df.groupby("Subject")["Percent"].mean()

    fig, ax = plt.subplots()
    subject_perf.plot(kind="bar", ax=ax)
    st.pyplot(fig)



# ---------------------------------------------------
# DOWNLOAD CSV (USER-SPECIFIC FIX)
# ---------------------------------------------------

st.subheader("⬇ Download Results")

# ONLY SELECTED USER DATA
download_df = user_df[[
    "Name",
    "Subject",
    "Score",
    "Percent",
    "Timestamp"
]].copy()

download_df["Timestamp"] = pd.to_datetime(
    download_df["Timestamp"],
    errors="coerce"
).dt.strftime("%Y-%m-%d %H:%M:%S")

csv_data = download_df.to_csv(index=False)

st.download_button(
    label=f"⬇ Download {current_user}'s Results ",
    data=csv_data,
    file_name=f"{current_user}_quiz_results.csv",
    mime="text/csv"
)