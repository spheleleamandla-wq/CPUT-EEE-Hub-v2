mode = st.sidebar.radio("Choose Mode", ["Study Mode", "Game Mode"])

if mode == "Game Mode":
(
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
.stop()
)
if mode  == "Study Mode":
(
import streamlit as st
import math
import cmath

st.set_page_config(page_title="CPUT EE Student Hub", page_icon="⚡", layout="wide")

# BRANDING
CPUT_BLUE = "#003366"; CPUT_GOLD = "#FFB81C"
APP_NAME = "CPUT EE Student Hub"
APP_SUB = "Electrical & Electronic Engineering - Student Tools"

st.markdown(f"""<style>
.stApp {{background: #F0F2F6;}}
.stButton>button {{background: {CPUT_BLUE}; color: white; border-radius: 8px; border: none; padding: 10px 20px; font-weight: bold;}}
.header {{display: flex; align-items: center; background: linear-gradient(90deg, {CPUT_BLUE}, #004a99); padding: 15px; border-radius: 12px;}}
.header h1 {{color: white; margin-left: 20px; font-size: 26px; margin-bottom: 0;}}
.header p {{color: {CPUT_GOLD}; margin-left: 20px; margin-top: 0;}}
</style>""", unsafe_allow_html=True)

st.markdown(f"""<div class="header"><div><h1>{APP_NAME}</h1><p>{APP_SUB}</p></div></div>""", unsafe_allow_html=True)

# MAIN MENU WITH OPTION BUTTONS
menu = st.sidebar.selectbox(
    "Select a Tool",
    ["🏠 Home", "📊 GPA Calculator", "⚡ Electrical Engineering", "📐 Mathematics", "🔌 Electronics", "🔬 Physics"]
)

# 1. HOME
if menu == "🏠 Home":
    st.title("Welcome to CPUT EE Hub")
    st.write("Pick a tool from the sidebar. Everything is from Level 1 basics → Level 4 advanced.")

# 2. GPA CALCULATOR
elif menu == "📊 GPA Calculator":
    st.header("GPA Calculator")
    # Your existing GPA code goes here

# 3. ELECTRICAL ENGINEERING - LOW TO HIGH LEVEL
elif menu == "⚡ Electrical Engineering":
    st.header("Electrical Engineering Calculators")
    ee_level = st.radio("Choose Level:", ["Level 1: Basics", "Level 2: AC & Power", "Level 3: Machines", "Level 4: Advanced"], horizontal=True)
    
    if ee_level == "Level 1: Basics":
        calc = st.selectbox("Pick Calculation", ["Ohm's Law", "Power P=VI", "Resistors in Series/Parallel"])
        if calc == "Ohm's Law":
            V = st.number_input("Voltage V", value=0.0)
            I = st.number_input("Current A", value=0.0)
            R = st.number_input("Resistance Ω", value=0.0)
            if st.button("Calculate"):
                if V == 0: st.success(f"V = I*R = {I*R} V")
                elif I == 0: st.success(f"I = V/R = {V/R} A")
                elif R == 0: st.success(f"R = V/I = {V/I} Ω")
    
    elif ee_level == "Level 2: AC & Power":
        calc = st.selectbox("Pick Calculation", ["3-Phase Power", "Power Factor Correction", "Voltage Drop"])
        if calc == "3-Phase Power":
            Vl = st.number_input("Line Voltage VL")
            Il = st.number_input("Line Current IL")
            pf = st.number_input("Power Factor", max_value=1.0)
            if st.button("Calculate"):
                P = math.sqrt(3) * Vl * Il * pf
                st.success(f"3-Phase Power = {P/1000:.2f} kW")

    elif ee_level == "Level 3: Machines":
        calc = st.selectbox("Pick Calculation", ["Transformer Efficiency", "DC Motor Speed", "Induction Motor Slip"])
    
    elif ee_level == "Level 4: Advanced":
        calc = st.selectbox("Pick Calculation", ["Fault Analysis", "Load Flow", "Protection Relay Settings"])

# 4. MATHEMATICS - LOW TO HIGH LEVEL
elif menu == "📐 Mathematics":
    st.header("Mathematics Calculators")
    maths_level = st.radio("Choose Level:", ["Level 1: Algebra", "Level 2: Trig & Complex", "Level 3: Calculus", "Level 4: Engineering Maths"], horizontal=True)
    
    if maths_level == "Level 1: Algebra":
        calc = st.selectbox("Pick Calculation", ["Quadratic Equation", "Simultaneous Equations", "Matrix 2x2"])
        if calc == "Quadratic Equation":
            a = st.number_input("a"); b = st.number_input("b"); c = st.number_input("c")
            if st.button("Solve"):
                d = b**2 - 4*a*c
                x1 = (-b + math.sqrt(d))/(2*a); x2 = (-b - math.sqrt(d))/(2*a)
                st.success(f"x1 = {x1:.2f}, x2 = {x2:.2f}")
    
    elif maths_level == "Level 2: Trig & Complex":
        calc = st.selectbox("Pick Calculation", ["Complex to Polar", "Phasor Addition"])
        if calc == "Complex to Polar":
            real = st.number_input("Real part"); imag = st.number_input("Imag part")
            if st.button("Convert"):
                mag = abs(complex(real, imag)); ang = math.degrees(cmath.phase(complex(real, imag)))
                st.success(f"Magnitude = {mag:.2f}, Angle = {ang:.2f}°")

# 5. ELECTRONICS - LOW TO HIGH LEVEL
elif menu == "🔌 Electronics":
    st.header("Electronics Calculators")
    elec_level = st.radio("Choose Level:", ["Level 1: Components", "Level 2: Analog", "Level 3: Digital", "Level 4: Microcontrollers"], horizontal=True)
    
    if elec_level == "Level 1: Components":
        calc = st.selectbox("Pick Calculation", ["Resistor Color Code", "Voltage Divider", "Capacitor Reactance"])
        if calc == "Voltage Divider":
            Vin = st.number_input("Vin"); R1 = st.number_input("R1"); R2 = st.number_input("R2")
            if st.button("Calculate"):
                Vout = Vin * R2 / (R1 + R2)
                st.success(f"Vout = {Vout:.2f} V")

# 6. PHYSICS - LOW TO HIGH LEVEL
elif menu == "🔬 Physics":
    st.header("Physics Calculators")
    phy_level = st.radio("Choose Level:", ["Level 1: Mechanics", "Level 2: Electricity", "Level 3: Waves & Light", "Level 4: Modern Physics"], horizontal=True)
    
    if phy_level == "Level 1: Mechanics":
        calc = st.selectbox("Pick Calculation", ["Kinematics", "Force F=ma", "Work & Energy"])
        if calc == "Kinematics":
            u = st.number_input("Initial velocity u"); a = st.number_input("Acceleration a"); t = st.number_input("Time t")
            if st.button("Calculate"):
                v = u + a*t; s = u*t + 0.5*a*t**2
                st.success(f"Final velocity v = {v:.2f} m/s, Distance s = {s:.2f} m")