
import streamlit as st
import json
import random

# Load all questions from single file
@st.cache_data
def load_all_questions():
    with open("HR_ALL_Cleaned_Questions.json", "r") as f:
        return json.load(f)

# Load scenarios
@st.cache_data
def load_scenarios():
    with open("HR_Scenarios.json", "r") as f:
        return json.load(f)

questions = load_all_questions()
scenarios = load_scenarios()

# UI Title
st.title("📘 Human Resources Quiz App")

# Extract available chapters from question data
chapter_options = sorted(set(q.get("chapter", "Unknown") for q in questions if "chapter" in q))
selected = st.sidebar.multiselect("📚 Select Chapters", chapter_options, default=chapter_options)

# Sidebar: Scenario Viewer
st.sidebar.markdown("---")
st.sidebar.subheader("🔎 Scenario Lookup")
scenario_keys = sorted(scenarios.keys())
selected_scenario = st.sidebar.selectbox("View Scenario", [""] + scenario_keys)
if selected_scenario:
    st.sidebar.info(scenarios[selected_scenario])

# Filter and load selected chapter questions
if selected:
    filtered_questions = [q for q in questions if q.get("chapter") in selected]

    if "questions" not in st.session_state or st.session_state.get("loaded_chapters") != selected:
        random.shuffle(filtered_questions)
        st.session_state.questions = filtered_questions
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.total = len(filtered_questions)
        st.session_state.feedback = ""
        st.session_state.show_next = False
        st.session_state.quiz_over = False
        st.session_state.loaded_chapters = selected

# Main quiz logic
if selected and not st.session_state.quiz_over:
    q = st.session_state.questions[st.session_state.q_index]
    st.subheader(f"Question {st.session_state.q_index + 1} of {st.session_state.total}")
    if "scenario_id" in q:
        st.markdown(f"**Refer to: `{q['scenario_id']}`**")
    st.write(q["question"])
    choice = st.radio("Select an answer:", q["choices"], key=st.session_state.q_index)

    if not st.session_state.show_next and st.button("Submit Answer"):
        correct_answer = q["choices"][ord(q["answer"]) - ord("A")]
        if choice == correct_answer:
            st.session_state.feedback = "✅ Correct!"
            st.session_state.score += 1
        else:
            st.session_state.feedback = f"❌ Incorrect. Correct answer: {correct_answer}"
        st.session_state.show_next = True

    if st.session_state.show_next:
        st.info(st.session_state.feedback)
        if st.button("Next Question"):
            st.session_state.q_index += 1
            st.session_state.show_next = False
            st.session_state.feedback = ""
            if st.session_state.q_index >= st.session_state.total:
                st.session_state.quiz_over = True
            st.rerun()

elif selected and st.session_state.get("quiz_over", False):
    st.subheader("🎉 Quiz Complete!")
    st.write(f"Final Score: **{st.session_state.score} / {st.session_state.total}**")
    if st.button("Restart Quiz"):
        for key in ["questions", "q_index", "score", "total", "feedback", "show_next", "quiz_over", "loaded_chapters"]:
            st.session_state.pop(key, None)
        st.rerun()
