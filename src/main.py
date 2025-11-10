import streamlit as st
import time
import uuid
from puzzle_generator import PuzzleGenerator
from adaptive_engine import AdaptiveEngine
from tracker import ProgressTracker
from logger import logger 

from exception import MathsException

# -------------------------------------------------------------------------
# Initialize Logger
# -------------------------------------------------------------------------

logger.info("✅ Math Adventures app started.")

# -------------------------------------------------------------------------
# Streamlit page setup
# -------------------------------------------------------------------------
st.set_page_config(page_title="Math Adventures", page_icon="🧮", layout="centered")
st.title("🧮 Math Adventures — Adaptive Learning")

# -------------------------------------------------------------------------
# Initialize database and session
# -------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"session_{uuid.uuid4().hex[:8]}"
    st.session_state['confidence'] = 50.0
    logger.info(f"New session started: {st.session_state['session_id']}")

tracker= ProgressTracker()
engine = AdaptiveEngine()
generator = PuzzleGenerator()

defaults = {
    "difficulty": "Easy",
    "question_start_time": None,
    "current_puzzle": None,
    "show_answer": False,
    "recommended_level": "Easy",
    "streak": 1,
    "expected_time": None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -------------------------------------------------------------------------
# Helper to generate new puzzle
# -------------------------------------------------------------------------
def new_puzzle(level: str ):
    question, answer, expected_time = generator.generate_puzzle(level, st.session_state["streak"],st.session_state['confidence'])
    st.session_state["current_puzzle"] = (question, answer)
    st.session_state["question_start_time"] = time.time()
    st.session_state["expected_time"] = expected_time
    st.session_state["show_answer"] = False
    logger.info(f"🧮 New puzzle generated | Level: {level} | Expected time: {expected_time:.2f}s")

# -------------------------------------------------------------------------
# First puzzle
# -------------------------------------------------------------------------
if st.session_state["current_puzzle"] is None:
    new_puzzle(st.session_state["difficulty"])

question, correct_answer = st.session_state["current_puzzle"]

# -------------------------------------------------------------------------
# UI: Puzzle Card
# -------------------------------------------------------------------------
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

st.markdown(
    f"""
<div class="card">
    <h4>Difficulty: {st.session_state['difficulty']}</h4>
    <p><strong>Question:</strong> {question}</p>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------------
# User Answer Input
# -------------------------------------------------------------------------
user_answer = st.text_input("✏️ Enter your answer:", key=f"answer_{question}")

col1, col2 = st.columns([1, 1])
with col1:
    check_btn = st.button("✅ Check Answer")
with col2:
    next_btn = st.button("➡️ Next Question")

# -------------------------------------------------------------------------
# Check Answer
# -------------------------------------------------------------------------
if check_btn and not st.session_state["show_answer"]:
    try:
        end_time = time.time()
        response_time = end_time - st.session_state["question_start_time"]

        try:
            user_answer_int = int(user_answer)
            correct = (user_answer_int == int(correct_answer))
        except ValueError:
            correct = False
            logger.warning(f"Wrong input format: {user_answer}")
            st.warning("⚠️ Please enter a valid number.")


        confidence_score = tracker.calculate_confidence(
            correct,
            st.session_state["difficulty"],
            response_time,
            st.session_state["streak"],
            st.session_state["expected_time"],
        )
        st.session_state['confidence'] = confidence_score


        next_level, st.session_state["streak"] = engine.recommend_next_level(
            st.session_state["difficulty"],
            correct,
            response_time,
            st.session_state["streak"],
            confidence_score,
        )
        st.session_state["recommended_level"] = next_level
        st.session_state["show_answer"] = True

        
        tracker.log_progress(
            st.session_state["session_id"],
            st.session_state["difficulty"],
            correct,
            response_time,
            st.session_state["streak"],
            confidence_score,
        )

        
        if correct:
            st.success(f"✅ Correct! Time: {response_time:.2f}s")
        else:
            st.error(f"❌ Incorrect. Correct Answer: **{correct_answer}**")

        logger.info("Answer processed successfully")

    except MathsException as me:
        logger.error(f"Maths Exception: {str(me)}")
        st.error("⚠️ A math-related error occurred. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        st.error("⚠️ Something went wrong! Try again.")

    

# -------------------------------------------------------------------------
# Next Question Button
# -------------------------------------------------------------------------
if next_btn:
    st.session_state["difficulty"] = st.session_state["recommended_level"]
    new_puzzle(st.session_state["difficulty"])
    st.rerun()

# -------------------------------------------------------------------------
# Sidebar Tracker
# -------------------------------------------------------------------------
st.markdown("---")
df = tracker.get_progress(st.session_state["session_id"])

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
        st.metric("Confidence", f"{st.session_state['confidence']:.2f}%")

    else:
        st.info("No progress yet — start answering questions!")

# -------------------------------------------------------------------------
# Progress Graph
# -------------------------------------------------------------------------
if not df.empty:
    df["score"] = df["correct"].cumsum()
    st.subheader("📈 Your Progress Over Time")
    st.line_chart(df[["score", "streak"]], width="stretch")
