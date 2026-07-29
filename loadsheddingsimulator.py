import streamlit as st
import random
import time

st.set_page_config(page_title="Loadshedding Simulator", page_icon="⚡", layout="centered")

st.markdown("""<style>
.stApp {background: #000; color: white;}
.title {text-align: center; font-size: 32px; color: #FFB81C;}
.power-on {background: #FFB81C; color: #000; padding: 20px; border-radius: 12px; text-align: center;}
.power-off {background: #333; color: #888; padding: 20px; border-radius: 12px; text-align: center;}
</style>""", unsafe_allow_html=True)

st.markdown('<p class="title">⚡ LOADSHEDDING SIMULATOR ⚡</p>', unsafe_allow_html=True)

if 'power' not in st.session_state:
    st.session_state.power = True
    st.session_state.battery = 100
    st.session_state.day = 1

col1, col2 = st.columns(2)
with col1: st.metric("Day", st.session_state.day)
with col2: st.metric("Phone Battery", f"{st.session_state.battery}%")

if st.session_state.power:
    st.markdown('<div class="power-on">💡 POWER IS ON</div>', unsafe_allow_html=True)
    task = st.selectbox("What do you do?", ["Charge Phone", "Cook", "Watch Netflix", "Do Laundry"])
    if st.button("Do Task"):
        if task == "Charge Phone": st.session_state.battery = min(100, st.session_state.battery + 30)
        st.success(f"You did: {task}")
        if random.random() < 0.3: # 30% chance loadshedding hits
            st.session_state.power = False
            st.error("🚨 LOADSHEDDING! POWER OFF!")
            time.sleep(1); st.rerun()
else:
    st.markdown('<div class="power-off">🌑 POWER IS OFF</div>', unsafe_allow_html=True)
    st.warning("You can't do anything. Light a candle.")
    if st.button("Wait 2 Hours"):
        st.session_state.power = True
        st.session_state.day += 1
        st.session_state.battery -= 20
        st.rerun()

if st.session_state.battery <= 0:
    st.error("GAME OVER: Phone died. You missed all your messages.")