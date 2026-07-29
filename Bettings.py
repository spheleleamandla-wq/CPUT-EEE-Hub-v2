import streamlit as st
import sqlite3
import hashlib
import random
import pandas as pd
from datetime import datetime
import time
import math

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect("betway_replica.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password_hash TEXT, first_name TEXT, wallet_balance REAL DEFAULT 1000.0)")
    c.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, timestamp TEXT, email TEXT, type TEXT, amount REAL, prev REAL, new REAL, desc TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS rooms (room_id TEXT PRIMARY KEY, players TEXT, pot REAL DEFAULT 0, jackpot REAL DEFAULT 1000)")
    c.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, room_id TEXT, user TEXT, msg TEXT, time TEXT)")
    conn.commit(); conn.close()

init_db()

def get_user(email):
    conn = sqlite3.connect("betway_replica.db"); c=conn.cursor()
    c.execute("SELECT first_name, wallet_balance FROM users WHERE email=?", (email,)); row=c.fetchone(); conn.close()
    return {"name":row[0],"balance":row[1]} if row else None

def register(email, pw, first):
    conn=sqlite3.connect("betway_replica.db"); c=conn.cursor()
    try: c.execute("INSERT INTO users VALUES (?,?,?,1000.0)", (email, hashlib.sha256(pw.encode()).hexdigest(), first)); conn.commit(); return True
    except: return False
    finally: conn.close()

def auth(email,pw):
    conn=sqlite3.connect("betway_replica.db"); c=conn.cursor()
    c.execute("SELECT email FROM users WHERE email=? AND password_hash=?", (email, hashlib.sha256(pw.encode()).hexdigest())); r=c.fetchone(); conn.close()
    return r

def update_balance(email,delta,desc):
    conn=sqlite3.connect("betway_replica.db"); c=conn.cursor()
    c.execute("SELECT wallet_balance FROM users WHERE email=?", (email,)); prev=c.fetchone()[0]
    new=prev+delta
    if new<0: conn.close(); return False
    c.execute("UPDATE users SET wallet_balance=? WHERE email=?", (new,email))
    c.execute("INSERT INTO transactions VALUES (NULL,?,?,?,?,?,?,?)",(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),email,"GAME",delta,prev,new,desc))
    conn.commit(); conn.close(); return True

def get_leaderboard():
    conn=sqlite3.connect("betway_replica.db"); df=pd.read_sql_query("SELECT first_name as Name, wallet_balance as Coins FROM users ORDER BY wallet_balance DESC LIMIT 10", conn); conn.close(); return df

def add_chat(room,user,msg):
    conn=sqlite3.connect("betway_replica.db"); c=conn.cursor()
    c.execute("INSERT INTO chat VALUES (NULL,?,?,?,?)",(room,user,msg,datetime.now().strftime("%H:%M:%S")))
    conn.commit(); conn.close()

def get_chat(room):
    conn=sqlite3.connect("betway_replica.db"); df=pd.read_sql_query("SELECT time,user,msg FROM chat WHERE room_id=? ORDER BY id DESC LIMIT 20", conn, params=(room,)); conn.close()
    return df[::-1]

def update_jackpot(room,amount):
    conn=sqlite3.connect("betway_replica.db"); c=conn.cursor()
    c.execute("UPDATE rooms SET jackpot = jackpot +? WHERE room_id=?", (amount,room)); conn.commit(); conn.close()

def get_jackpot(room):
    conn=sqlite3.connect("betway_replica.db"); c=conn.cursor()
    c.execute("SELECT jackpot FROM rooms WHERE room_id=?", (room,)); r=c.fetchone(); conn.close()
    return r[0] if r else 1000

# --- SOUND + ANIMATION ---
def play_sound(sound_type, speed=1.0):
    sounds = {
        "win": "https://www.soundjay.com/mechanical/sounds/cash-register-1.mp3",
        "lose": "https://www.soundjay.com/misc/sounds/buzzer-1.mp3",
        "jackpot": "https://www.soundjay.com/misc/sounds/air-horn-1.mp3",
        "spin": "https://www.soundjay.com/mechanical/sounds/roulette-wheel-1.mp3"
    }
    # speed control for wheel
    st.markdown(f"""<audio id="spinAudio" autoplay playbackRate="{speed}"><source src="{sounds[sound_type]}" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

SUITS = {"Hearts":"♥️","Diamonds":"♦️","Clubs":"♣️","Spades":"♠️"}
RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

# --- LUCKY WHEEL GAME ---
def spinning_wheel_game(user_email, balance, current_room):
    st.subheader("🎡 Lucky Wheel - Press to Stop!")

    # 12 sections, 2 winners
    wheel_options = [
        {"num": 1, "color": "red", "win": False}, {"num": 2, "color": "black", "win": True},
        {"num": 3, "color": "red", "win": False}, {"num": 4, "color": "black", "win": False},
        {"num": 5, "color": "red", "win": False}, {"num": 6, "color": "black", "win": False},
        {"num": 7, "color": "red", "win": False}, {"num": 8, "color": "black", "win": False},
        {"num": 9, "color": "red", "win": False}, {"num": 10, "color": "black", "win": True},
        {"num": 11, "color": "red", "win": False}, {"num": 12, "color": "black", "win": False},
    ]

    if "wheel_spinning" not in st.session_state: st.session_state.wheel_spinning = False
    if "wheel_result" not in st.session_state: st.session_state.wheel_result = None
    if "wheel_angle" not in st.session_state: st.session_state.wheel_angle = 0
    if "spin_speed" not in st.session_state: st.session_state.spin_speed = 30

    col1, col2 = st.columns([1,1])

    with col1:
        bet_amount = st.number_input("Bet Amount", 1, int(balance), 50, key="wheel_bet")
        color_bet = st.radio("Bet on Color", ["Red", "Black"], horizontal=True)

        if st.button("▶️ PRESS TO PLAY", disabled=st.session_state.wheel_spinning):
            jackpot_contrib = max(1, int(bet_amount*0.01))
            if current_room: update_jackpot(current_room, jackpot_contrib)
            if update_balance(user_email, -bet_amount, "WHEEL_BET", "Wheel spin bet"):
                st.session_state.wheel_spinning = True
                st.session_state.wheel_result = None
                st.session_state.spin_speed = 30
                play_sound("spin")
                st.rerun()
            else: st.error("Not enough coins")

        if st.button("⏹️ PRESS TO STOP", disabled=not st.session_state.wheel_spinning):
            st.session_state.wheel_spinning = False
            result = random.choice(wheel_options)
            st.session_state.wheel_result = result
            play_sound("win" if result["win"] else "lose")
            st.rerun()

    with col2:
        angle_per_section = 360 / len(wheel_options)

        # ANIMATION + SPEED SOUND
        if st.session_state.wheel_spinning:
            st.session_state.wheel_angle = (st.session_state.wheel_angle + st.session_state.spin_speed) % 360
            st.session_state.spin_speed = max(5, st.session_state.spin_speed - 0.5) # slows down
            play_sound("spin", speed=st.session_state.spin_speed/10)
            time.sleep(0.08)
            st.rerun()

        # SVG WHEEL RED/BLACK
        wheel_html = f"""<div style="position:relative;width:300px;height:300px;margin:auto">
            <div style="width:300px;height:300px;border-radius:50%;border:8px solid gold;transform:rotate({st.session_state.wheel_angle}deg);transition:transform 0.08s linear;position:relative;overflow:hidden">"""

        for i, option in enumerate(wheel_options):
            start_angle = i * angle_per_section
            bg = "#d32f2f" if option["color"] == "red" else "#121212"
            star = "⭐" if option["win"] else ""
            wheel_html += f"""<div style="position:absolute;width:50%;height:50%;background:{bg};color:white;font-weight:bold;
            transform-origin:100% 100%;transform:rotate({start_angle}deg) skewY({90-angle_per_section}deg);
            display:flex;align-items:center;justify-content:center;border:1px solid #333">
                <div style="transform:skewY({-(90-angle_per_section)}deg) rotate({angle_per_section/2}deg)">{option['num']}{star}</div>
            </div>"""

        wheel_html += """</div><div style="position:absolute;top:-10px;left:50%;transform:translateX(-50%);font-size:40px;color:gold">▼</div></div>"""
        st.markdown(wheel_html, unsafe_allow_html=True)

    if st.session_state.wheel_result:
        result = st.session_state.wheel_result
        st.markdown("---")
        st.write(f"### Wheel stopped on: **{result['num']}** - **{result['color'].upper()}** {'⭐ WINNER SECTION' if result['win'] else ''}")

        payout = 0
        if result["win"]: payout += bet_amount * 5; st.success(f"🎉 WINNER SECTION! +{bet_amount * 5}")
        if result["color"] == color_bet.lower(): payout += bet_amount * 2; st.success(f"🎨 Correct Color! +{bet_amount * 2}")
        if payout == 0: st.error("No win this spin")
        if payout > 0: update_balance(user_email, payout, "WHEEL_WIN", f"Wheel win on {result['num']}")
        if st.button("Play Again"): st.session_state.wheel_result = None; st.rerun()

# --- APP ---
st.set_page_config(page_title="PlayHub PRO MAX", page_icon="🎰", layout="wide")
st.markdown("""<style>
.stApp{background:#0b0c10;color:#ecf0f1}
@keyframes flip{from{transform:rotateY(180deg)}to{transform:rotateY(0deg)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
.spinning{animation:spin 1s linear}
.jackpot{font-size:40px;color:gold;text-shadow:0 0 10px gold;animation:pulse 1s infinite}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}
.chat-box{height:250px;overflow-y:auto;background:#1f2833;padding:10px;border-radius:10px}
</style>""", unsafe_allow_html=True)

if "current_user" not in st.session_state: st.session_state.current_user=None
if "current_room" not in st.session_state: st.session_state.current_room=None

# LOGIN
if st.session_state.current_user is None:
    st.title("🎰 PlayHub PRO MAX")
    tab1,tab2 = st.tabs(["Login","Register"])
    with tab1:
        e=st.text_input("Email"); p=st.text_input("Password",type="password")
        if st.button("Login") and auth(e,p): st.session_state.current_user=e; st.rerun()
    with tab2:
        e=st.text_input("Email "); f=st.text_input("Name"); p=st.text_input("Password ",type="password")
        if st.button("Register") and register(e,p,f): st.success("1000 coins given!"); st.rerun()

# DASHBOARD
else:
    profile=get_user(st.session_state.current_user)
    st.title(f"Welcome {profile['name']}")
    c1,c2,c3 = st.columns(3)
    c1.metric("Coins", f"{profile['balance']:.0f}")
    if c2.button("Free 500"): update_balance(st.session_state.current_user,500,"DAILY"); st.rerun()
    if c3.button("Logout"): st.session_state.current_user=None; st.session_state.current_room=None; st.rerun()

    tabs = st.tabs(["🎲 Games","👥 Multiplayer + Chat","🏆 Leaderboard","💰 Jackpot","📜 History"])

    # GAMES
    with tabs[0]:
        game=st.selectbox("Choose", ["Animated Dice","Roulette Wheel","Baccarat","Lucky Wheel"])
        bet=st.number_input("Bet",1,int(profile['balance']),20)

        if game=="Animated Dice":
            if st.button("ROLL"):
                play_sound("spin")
                wheel = st.empty()
                for i in range(10): wheel.markdown("<div class='spinning' style='font-size:100px;text-align:center'>🎲</div>", unsafe_allow_html=True); time.sleep(0.1)
                roll=random.randint(1,6); wheel.markdown(f"<div style='font-size:100px;text-align:center'>{['⚀','⚁','⚂','⚃','⚄','⚅'][roll-1]}</div>", unsafe_allow_html=True)
                win=roll>=4; payout=bet if win else -bet; update_balance(st.session_state.current_user,payout,"DICE"); play_sound("win" if win else "lose"); st.rerun()

        if game=="Lucky Wheel":
            spinning_wheel_game(st.session_state.current_user, profile['balance'], st.session_state.current_room)

    # MULTIPLAYER + CHAT
    with tabs[1]:
        st.subheader("👥 Multiplayer Rooms")
        room_name=st.text_input("Room Name")
        if st.button("Join/Create Room"):
            conn=sqlite3.connect("betway_replica.db"); c=conn.cursor()
            c.execute("SELECT players FROM rooms WHERE room_id=?", (room_name,)); r=c.fetchone()
            if r: players=list(set(r[0].split(",")+ [profile['name']]))
            else: players=[profile['name']]; c.execute("INSERT INTO rooms VALUES (?,?,0,1000)", (room_name,profile['name']))
            c.execute("UPDATE rooms SET players=? WHERE room_id=?", (",".join(players),room_name))
            conn.commit(); conn.close()
            st.session_state.current_room=room_name; st.success(f"Joined {room_name}")

        if st.session_state.current_room:
            st.write(f"### Room: {st.session_state.current_room}")
            col1,col2 = st.columns([2,1])
            with col1:
                st.write("💬 Live Chat")
                st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
                chat_df = get_chat(st.session_state.current_room)
                for _,row in chat_df.iterrows(): st.markdown(f"**{row['time']} {row['user']}**: {row['msg']}")
                st.markdown("</div>", unsafe_allow_html=True)
                msg=st.text_input("Send message", key="chat")
                if st.button("Send"): add_chat(st.session_state.current_room, profile['name'], msg); st.rerun()
            with col2:
                st.write("🎲 Room Dice Battle")
                if st.button("Roll For All"):
                    conn=sqlite3.connect("betway_replica.db"); c=conn.cursor()
                    c.execute("SELECT players FROM rooms WHERE room_id=?", (st.session_state.current_room,)); players=c.fetchone()[0].split(",")
                    rolls={p:random.randint(1,6) for p in players}
                    for p,r in rolls.items(): st.write(f"{p}: {r} {['⚀','⚁','⚂','⚃','⚄','⚅'][r-1]}")
                    winner=max(rolls,key=rolls.get); st.success(f"🏆 {winner} wins!")

    # LEADERBOARD
    with tabs[2]: st.subheader("🏆 Top Players"); st.dataframe(get_leaderboard(), use_container_width=True)

    # JACKPOT
    with tabs[3]:
        st.subheader("💰 PROGRESSIVE JACKPOT")
        if st.session_state.current_room:
            jackpot = get_jackpot(st.session_state.current_room)
            st.markdown(f"<div class='jackpot'>JACKPOT: {jackpot:.0f} COINS</div>", unsafe_allow_html=True)
            if st.button("SPIN FOR JACKPOT - 100 Coins"):
                if update_balance(st.session_state.current_user,-100,"JACKPOT_SPIN"):
                    update_jackpot(st.session_state.current_room, 100)
                    if random.randint(1,100)==77:
                        update_balance(st.session_state.current_user,jackpot,"JACKPOT_WIN"); play_sound("jackpot"); st.balloons(); st.success(f"JACKPOT!!! {jackpot} COINS!!!")
                        conn=sqlite3.connect("betway_replica.db"); c=conn.cursor(); c.execute("UPDATE rooms SET jackpot=1000 WHERE room_id=?", (st.session_state.current_room,)); conn.commit(); conn.close()
                    else: st.error("No Jackpot this time")
                    st.rerun()
        else: st.warning("Join a room first to play for the jackpot!")

    # HISTORY
    with tabs[4]:
        conn=sqlite3.connect("betway_replica.db")
        df=pd.read_sql_query("SELECT timestamp,type,amount,new FROM transactions WHERE email=? ORDER BY id DESC LIMIT 20", conn, params=(st.session_state.current_user,))
        conn.close(); st.dataframe(df, use_container_width=True)