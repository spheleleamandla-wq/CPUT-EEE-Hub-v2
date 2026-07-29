import streamlit as st
import sqlite3
import hashlib
import hmac
import re
import random
import pandas as pd
import requests
import time
from datetime import datetime, timedelta

# --- COMPREHENSIVE PERSISTENT DATABASE LAYER ---
def init_db():
    conn = sqlite3.connect("betway_replica.db")
    cursor = conn.cursor()
    # 1. User Profiles Master Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            id_num TEXT NOT NULL,
            wallet_balance REAL DEFAULT 0.0,
            exclusion_end_date TEXT DEFAULT NULL
        )
    """)
    # 2. Auditable Transaction Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            email TEXT NOT NULL,
            type TEXT NOT NULL, 
            amount REAL NOT NULL,
            previous_balance REAL NOT NULL,
            new_balance REAL NOT NULL,
            description TEXT NOT NULL,
            performed_by TEXT NOT NULL 
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- DATABASE INTERACTION UTILITIES ---
def get_user_profile(email):
    conn = sqlite3.connect("betway_replica.db")
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name, wallet_balance, exclusion_end_date FROM users WHERE email = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"first_name": row, "last_name": row, "balance": row, "exclusion": row}
    return None

def register_new_user(email, password, first, last, mobile, id_num):
    conn = sqlite3.connect("betway_replica.db")
    cursor = conn.cursor()
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, mobile, id_num, wallet_balance)
            VALUES (?, ?, ?, ?, ?, ?, 0.0)
        """, (email.lower().strip(), hashed, first, last, mobile, id_num))
        conn.commit()
        record_transaction(email.lower().strip(), "DEPOSIT", 0.0, 0.0, 0.0, "Account initialized with zero balance", "USER")
        return True, "Success"
    except sqlite3.IntegrityError:
        return False, "❌ Profile anomaly: This email is already registered."
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect("betway_replica.db")
    cursor = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT email FROM users WHERE email = ? AND password_hash = ?", (email.lower().strip(), hashed))
    row = cursor.fetchone()
    conn.close()
    return True if row else False

def record_transaction(email, tx_type, amount, prev_bal, new_bal, description, performed_by):
    conn = sqlite3.connect("betway_replica.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO transactions (timestamp, email, type, amount, previous_balance, new_balance, description, performed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, email, tx_type, amount, prev_bal, new_bal, description, performed_by))
    conn.commit()
    conn.close()

def update_wallet_balance(email, changing_offset, tx_type="ADMIN_ADJUSTMENT", description="Manual override operation", performed_by="ADMIN"):
    conn = sqlite3.connect("betway_replica.db")
    cursor = conn.cursor()
    cursor.execute("SELECT wallet_balance FROM users WHERE email = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    prev_bal = row
    new_bal = prev_bal + changing_offset
    cursor.execute("UPDATE users SET wallet_balance = ? WHERE email = ?", (new_bal, email.lower().strip()))
    conn.commit()
    conn.close()
    record_transaction(email.lower().strip(), tx_type, changing_offset, prev_bal, new_bal, description, performed_by)

def apply_self_exclusion(email, days):
    conn = sqlite3.connect("betway_replica.db")
    cursor = conn.cursor()
    if days == 0:
        end_date = None
    else:
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET exclusion_end_date = ? WHERE email = ?", (end_date, email.lower().strip()))
    conn.commit()
    conn.close()

# --- ADMIN SYSTEM QUERY ENGINE CALLS ---
def admin_get_all_users():
    conn = sqlite3.connect("betway_replica.db")
    df = pd.read_sql_query("SELECT email, first_name, last_name, mobile, id_num, wallet_balance, exclusion_end_date FROM users", conn)
    conn.close()
    return df

def admin_get_all_transactions():
    conn = sqlite3.connect("betway_replica.db")
    df = pd.read_sql_query("SELECT id, timestamp, email, type, amount, previous_balance, new_balance, description, performed_by FROM transactions ORDER BY id DESC", conn)
    conn.close()
    return df

# --- AUTOMATED REGULATORY GEOFENCING ---
def verify_geofence_access():
    try:
        geo_response = requests.get("https://ipapi.co", timeout=4)
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            country_iso = geo_data.get("country_code", "ZA")
            return country_iso == "ZA", country_iso, geo_data.get("country_name", "Localhost Network")
        return True, "ZA", "Fallback Mode"
    except Exception:
        return True, "ZA", "Secure Network Mesh Timeout"

# --- VISUAL RENDERING UI METHODS ---
def render_styled_card(card_string):
    color = "#d32f2f" if any(suite in card_string for suite in ["♥️", "♦️"]) else "#121212"
    return f"""
    <div style="display: inline-block; background-color: white; color: {color}; border-radius: 8px; padding: 15px; width: 65px; height: 95px; font-size: 22px; font-weight: bold; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin: 5px; border: 2px solid #e0e0e0; line-height: 65px;">
        {card_string}
    </div>
    """

def generate_fair_random(server_seed, client_seed, nonce, max_range):
    msg = f"{client_seed}:{nonce}".encode()
    hash_result = hmac.new(server_seed.encode(), msg, hashlib.sha256).hexdigest()
    return int(hash_result[:8], 16) % max_range

# --- INITIALIZE SIMULATED LIVE FIXTURES IN MEMORY RUNTIME ---
if "sports_fixtures" not in st.session_state:
    st.session_state.sports_fixtures = [
        {"id": 101, "sport": "Soccer", "home": "Mamelodi Sundowns", "away": "Orlando Pirates", "home_odds": 1.85, "draw_odds": 3.20, "away_odds": 4.10, "status": "LIVE - 2nd Half"},
        {"id": 102, "sport": "Soccer", "home": "Kaizer Chiefs", "away": "Cape Town City", "home_odds": 2.10, "draw_odds": 3.00, "away_odds": 3.40, "status": "LIVE - 1st Half"},
        {"id": 103, "sport": "Rugby", "home": "Stormers", "away": "Bulls", "home_odds": 1.50, "draw_odds": 21.00, "away_odds": 2.65, "status": "Upcoming"},
        {"id": 104, "sport": "Cricket", "home": "Proteas", "away": "Australia", "home_odds": 1.95, "draw_odds": 45.00, "away_odds": 1.85, "status": "Upcoming"}
    ]

# --- RUNTIME APP INITIALIZATION ---
st.set_page_config(page_title="Betway Clone Dashboard", page_icon="🎰", layout="wide")

if "current_user" not in st.session_state: st.session_state.current_user = None
if "admin_logged_in" not in st.session_state: st.session_state.admin_logged_in = False
if "nonce" not in st.session_state: st.session_state.nonce = 0
if "wheel_spinning" not in st.session_state: st.session_state.wheel_spinning = False

st.markdown("""
    <style>
    .stApp { background-color: #0b0c10; color: #ecf0f1; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] { background-color: #1f2833; border-radius: 6px; padding: 12px 24px; color: #c5a059; }
    .stTabs [aria-selected="true"] { background-color: #00a826 !important; color: white !important; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #00a826 !important; }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .spinning-wheel-ui { width: 180px; height: 180px; border-radius: 50%; border: 6px solid #c5a059; background: conic-gradient(#d32f2f 0deg 32.7deg, #121212 32.7deg 65.4deg, #d32f2f 65.4deg 98.1deg, #121212 98.1deg 130.8deg, #d32f2f 130.8deg 163.5deg, #7f8c8d 163.5deg 196.2deg, #121212 196.2deg 228.9deg, #d32f2f 228.9deg 261.6deg, #121212 261.6deg 294.3deg, #d32f2f 294.3deg 327deg, #121212 327deg 360deg); animation: spin 0.8s linear infinite; margin-bottom: 15px; }
    </style>
""", unsafe_allowed_html=True)

is_allowed_zone, country_code, country_title = verify_geofence_access()

if not is_allowed_zone:
    st.title("🚫 Territorial Regulatory Lockout")
    st.error(f"Access Denied. Your detected IP origin ({country_title}) is restricted.")
else:
    # --- ADMIN WORKSPACE PORTAL (WITH NEW EXCEL & CSV EXPORT UTILITIES) ---
    if st.session_state.admin_logged_in:
        st.title("⚙️ Internal Admin Management Dashboard")
        if st.button("⬅️ Exit Admin Workspace & Log Out"):
            st.session_state.admin_logged_in = False
            st.rerun()
        st.markdown("---")
        adm_tab1, adm_tab2 = st.tabs(["📊 Accounts Ledger & Controls", "📜 Immutable System Audit Logs & Data Export"])
        
        with adm_tab1:
            st.subheader("👥 Registered System Accounts Ledger")
            all_users_df = admin_get_all_users()
            st.dataframe(all_users_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🛠️ Balance & Account Management Hub")
            if not all_users_df.empty:
                target_user = st.selectbox("Select Target User Account profile", all_users_df["email"].tolist())
