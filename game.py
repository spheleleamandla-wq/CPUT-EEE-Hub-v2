mode = st.sidebar.radio("Choose Mode", ["📚 Study Mode", "🎮 Game Mode"])

if mode == "🎮 Game Mode":
import streamlit as st
import random

st.set_page_config(page_title="CPUT Game Hub", page_icon="🎮", layout="centered")

CPUT_BLUE = "#003366"; CPUT_GOLD = "#FFB81C"
st.markdown(f"""<style>
.stApp {{background: #F0F2F6;}}
.stButton>button {{background: {CPUT_BLUE}; color: white; border-radius: 12px; font-size: 18px; padding: 12px;}}
.title {{text-align: center; color: {CPUT_BLUE}; font-size: 32px; font-weight: bold;}}
</style>""", unsafe_allow_html=True)

st.markdown('<p class="title">🎮 Guess The Number</p>', unsafe_allow_html=True)
st.write("I'm thinking of a number between 1 and 100. Can you guess it?")

# Keep score in session
if 'number' not in st.session_state:
    st.session_state.number = random.randint(1, 100)
    st.session_state.attempts = 0

guess = st.number_input("Enter your guess:", min_value=1, max_value=100, step=1)

col1, col2 = st.columns(2)
with col1:
if st.button("Submit Guess"):
st.session_state.attempts += 1
if guess < st.session_state.number:
st.warning("📈 Too LOW! Go Higher")
elif guess > st.session_state.number:
st.warning("📉 Too HIGH! Go Lower")
else:
st.success(f"🎉 CORRECT! You got it in {st.session_state.attempts} attempts!")
st.balloons()

with col2:
if st.button("New Game"):
st.session_state.number = random.randint(1, 100)
st.session_state.attempts = 0
st.rerun()

st.info(f"Attempts: {st.session_state.attempts}")
.stop() #
