import streamlit as st
import time
from puzzle_generator import generate_puzzle
from adaptive_engine import recommend_next_level
import uuid
from tracker import init_db, log_progress, get_progress

st.set_page_config(page_title="Math Adventures", page_icon="🧮", layout="centered")
st.title("🧮 Math Adventures — Adaptive Learning")


if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"session_{uuid.uuid4().hex[:8]}"
init_db()

if "difficulty" not in st.session_state:
    st.session_state["difficulty"] = "Easy"
if "question_start_time" not in st.session_state:
    st.session_state["question_start_time"] = None
if "current_puzzle" not in st.session_state:
    st.session_state["current_puzzle"] = None
if "show_answer" not in st.session_state:
    st.session_state["show_answer"] = False
if "recommended_level" not in st.session_state:
    st.session_state["recommended_level"] = "Easy"
if "streak" not in st.session_state:
    st.session_state["streak"] = 1


def new_puzzle(level):
    question, answer = generate_puzzle(level)
    st.session_state["current_puzzle"] = (question, answer)
    st.session_state["question_start_time"] = time.time()
    st.session_state["show_answer"] = False


if st.session_state["current_puzzle"] is None:
    new_puzzle(st.session_state["difficulty"])

question, correct_answer = st.session_state["current_puzzle"]


st.markdown(
    """
    <style>
    .card {
        background-color: var(--background-color-secondary);
        color: var(--text-color);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



st.markdown(f"""
<div class="card">
    <h4>Difficulty: {st.session_state['difficulty']}</h4>
    <p><strong>Question:</strong> {question}</p>
</div>
""", unsafe_allow_html=True)


user_answer = st.text_input("✏️ Enter your answer:", key=f"answer_{question}")


col1, col2 = st.columns([1, 1])
with col1:
    check_btn = st.button("✅ Check Answer")
with col2:
    next_btn = st.button("➡️ Next Question")


if check_btn and not st.session_state["show_answer"]:
    end_time = time.time()
    response_time = end_time - st.session_state["question_start_time"]

    try:
        user_answer_int = int(user_answer)
        correct = (user_answer_int == int(correct_answer))
    except:
        correct = False

    # Update difficulty and streak
    next_level, st.session_state['streak'] = recommend_next_level(
        st.session_state["difficulty"], correct, response_time, st.session_state['streak']
    )
    st.session_state["recommended_level"] = next_level
    st.session_state["show_answer"] = True

    # ✅ Save the result to DB
    log_progress(
        st.session_state["session_id"],
        st.session_state["difficulty"],
        correct,
        response_time,
        st.session_state["streak"]
    )

    # ✅ Retrieve updated progress
    df = get_progress(st.session_state["session_id"])

    # ✅ Display results
    if correct:
        st.success(f"Correct! Time: {response_time:.2f}s")
    else:
        st.error(f"Incorrect. Correct Answer: **{correct_answer}** (Time: {response_time:.2f}s)")

    st.info(f"**Next Recommended Level:** {next_level}")

  
if next_btn:
    st.session_state["difficulty"] = st.session_state["recommended_level"]
    new_puzzle(st.session_state["difficulty"])  
    st.rerun()
st.markdown("---")
df = get_progress(st.session_state["session_id"])
with st.sidebar:
    st.header("📊 Live Tracker")
    
    if not df.empty:
        accuracy = (df["correct"].sum() / len(df)) * 100
        avg_time = df["response_time"].mean()
        st.metric("Questions Attempted", len(df))
        st.metric("Accuracy", f"{accuracy:.1f}%")
        st.metric("Correct Answers", int(df["correct"].sum()))
        st.metric("Avg Time", f"{avg_time:.2f}s")
        st.metric("Current Streak", st.session_state["streak"])
    
    else:
        st.info("No progress yet — start answering questions!")
df["score"] = df["correct"].cumsum()      
st.subheader("📈 Your Progress Over Time")
st.line_chart(df[["score", "streak"]], use_container_width=True)