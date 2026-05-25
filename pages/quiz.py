import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import re

# PAGE CONFIG

st.set_page_config(
    page_title="Quiz",
    page_icon="📝"
)

st.title("📝 Take a Quiz")

# FILE PATHS

BASE_DIR = os.path.dirname(__file__)

PROJECT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

QUESTIONS_PATH = os.path.join(
    PROJECT_DIR,
    "questions.csv"
)

RESULTS_PATH = os.path.join(
    PROJECT_DIR,
    "results.csv"
)

# LOAD QUESTIONS

questions_df = pd.read_csv(
    QUESTIONS_PATH
)

# CLEAN SUBJECTS

questions_df["Subject"] = (
    questions_df["Subject"]
    .astype(str)
    .str.strip()
    .str.title()
)

# SESSION STATES

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None

if "current_subject" not in st.session_state:
    st.session_state.current_subject = None

if "used_questions" not in st.session_state:
    st.session_state.used_questions = {}

# USER DETAILS

st.subheader("Enter Your Details")

user_name = st.text_input(
    "Enter your name:"
).strip()

if not user_name:

    st.info(
        "Please enter your name."
    )

    st.stop()

elif not re.fullmatch(
    r"[A-Za-z ]+",
    user_name
):

    st.error(
        "❌ Name should contain only letters."
    )

    st.stop()

elif len(user_name) < 3:

    st.warning(
        "⚠ Name should contain at least 3 letters."
    )

    st.stop()

# SUBJECTS

available_subjects = sorted(
    questions_df["Subject"]
    .unique()
    .tolist()
)

selected_subject = st.selectbox(
    "Select Subject:",
    ["-- Select Subject --"]
    + available_subjects
)

if (
    selected_subject
    == "-- Select Subject --"
):

    st.info(
        "Please select a subject."
    )

    st.stop()

# LOAD QUESTIONS

if (
    st.session_state.current_subject
    != selected_subject
):

    st.session_state.current_subject = (
        selected_subject
    )

    st.session_state.submitted = False

    st.session_state.start_time = (
        datetime.now()
    )

    # CLEAR OLD WIDGET STATES

    for key in list(st.session_state.keys()):

        if key.startswith("q"):

            del st.session_state[key]

    # FILTER SUBJECT QUESTIONS

    subject_questions = questions_df[
        questions_df["Subject"]
        == selected_subject
    ]

    # REMOVE DUPLICATES

    subject_questions = (
        subject_questions
        .drop_duplicates(
            subset=["Question"]
        )
        .reset_index(drop=True)
    )

    # USED QUESTIONS

    if (
        selected_subject
        not in st.session_state.used_questions
    ):

        st.session_state.used_questions[
            selected_subject
        ] = []

    remaining_questions = (
        subject_questions[
            ~subject_questions["QID"].isin(
                st.session_state
                .used_questions[
                    selected_subject
                ]
            )
        ]
    )

    # RESET USED QUESTIONS

    if len(remaining_questions) < 10:

        st.session_state.used_questions[
            selected_subject
        ] = []

        remaining_questions = (
            subject_questions
        )

    # RANDOM QUESTIONS

    quiz_questions = (
        remaining_questions.sample(
            n=min(10, len(remaining_questions)),
            random_state=None
        ).reset_index(drop=True)
    )

    # SAVE USED IDS

    st.session_state.used_questions[
        selected_subject
    ].extend(
        quiz_questions["QID"].tolist()
    )

    st.session_state.quiz_questions = (
        quiz_questions
    )

# FETCH QUESTIONS

quiz_questions = (
    st.session_state.quiz_questions
)

total_questions = len(
    quiz_questions
)

# TIMER

TOTAL_TIME_SECONDS = 5 * 60

elapsed = (
    datetime.now()
    - st.session_state.start_time
).seconds

remaining = max(
    TOTAL_TIME_SECONDS - elapsed,
    0
)

mins, secs = divmod(
    remaining,
    60
)

st.info(
    f"⏱ Time Left: {mins:02d}:{secs:02d}"
)

# AUTO SUBMIT

if (
    remaining == 0
    and not st.session_state.submitted
):

    st.session_state.submitted = True

# DISPLAY QUESTIONS

for i, row in quiz_questions.iterrows():

    st.markdown(
        f"### Q{i+1}. {row['Question']}"
    )

    options = [
        str(row["Option1"]).strip(),
        str(row["Option2"]).strip(),
        str(row["Option3"]).strip(),
        str(row["Option4"]).strip()
    ]

    # STABLE WIDGET

    st.selectbox(
        "Choose your answer:",
        ["Select Answer"] + options,
        key=f"q{i}"
    )

    # AFTER SUBMIT

    if st.session_state.submitted:

        user_ans = st.session_state.get(
            f"q{i}"
        )

        if user_ans == "Select Answer":
            user_ans = ""

        correct_ans = str(
            row["Answer"]
        ).strip()

        # CORRECT

        if user_ans == correct_ans:

            st.success(
                f"✔ Correct\n\n"
                f"Your Answer: {user_ans}"
            )

        # NOT ANSWERED

        elif user_ans == "":

            st.warning(
                f"⚠ Not Answered\n\n"
                f"Correct Answer: {correct_ans}"
            )

        # WRONG

        else:

            st.error(
                f"✘ Wrong Answer\n\n"
                f"Your Answer: {user_ans}\n\n"
                f"Correct Answer: {correct_ans}"
            )

# SUBMIT BUTTON

if not st.session_state.submitted:

    if st.button("Submit Quiz"):

        st.session_state.submitted = True

        st.rerun()

# RESULT SECTION

if st.session_state.submitted:

    score = 0

    for i, row in quiz_questions.iterrows():

        user_ans = st.session_state.get(
            f"q{i}"
        )

        if user_ans == "Select Answer":
            user_ans = ""

        correct_ans = str(
            row["Answer"]
        ).strip()

        if user_ans == correct_ans:

            score += 1

    percent = round(
        (score / total_questions) * 100,
        2
    )

    st.success(
        f"🎯 Score: {score}/{total_questions}"
    )

    st.info(
        f"📊 Percentage: {percent}%"
    )

    # SAVE RESULTS

    result_row = {

        "Name": user_name,

        "Subject": selected_subject,

        "Score": score,

        "Total": total_questions,

        "Percent": percent,

        "Timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    try:

        if os.path.exists(
            RESULTS_PATH
        ):

            results_df = pd.read_csv(
                RESULTS_PATH
            )

            results_df = pd.concat(
                [
                    results_df,
                    pd.DataFrame(
                        [result_row]
                    )
                ],
                ignore_index=True
            )

        else:

            results_df = pd.DataFrame(
                [result_row]
            )

        results_df.to_csv(
            RESULTS_PATH,
            index=False
        )

    except Exception as e:

        st.error(
            f"Error saving result: {e}"
        )