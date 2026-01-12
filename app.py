import streamlit as st
from supabase import create_client
import re, random, time, smtplib
from email.message import EmailMessage
import streamlit.components.v1 as components

# ================= CONFIG =================
#SMTP_EMAIL = "mostafa.snowber.2023@gmail.com"
#SMTP_PASSWORD = "YOUR_APP_PASSWORD"
SMTP_EMAIL = "mostafa.snowber.2023@gmail.com"
SMTP_PASSWORD = "n l m z h x r f k c u u y q u z"

#SUPABASE_URL = "https://utvubafvttzbuvlkchig.supabase.co"
#SUPABASE_KEY = "sb_publishable_..."
SUPABASE_URL = "https://utvubafvttzbuvlkchig.supabase.co"
SUPABASE_KEY = "sb_publishable_GOeCyF4B9YODOXDLNWu7HQ_JAib3deP"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PIN_EXPIRY = 60
# ================= HELPERS =================
def is_valid_email(email):
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", email)

def send_pin_email(receiver, pin):
    msg = EmailMessage()
    msg["Subject"] = "Beam Designer - Verification Code"
    msg["From"] = SMTP_EMAIL
    msg["To"] = receiver
    #msg.set_content(f"Your PIN: {pin} (valid 1 minute)")
    msg.set_content(f"""
Welcome to Beam Designer 👋

Your verification PIN is:

{pin}

⏱️ This code is valid for 1 minute only.

Mostafa Snowber.
Executive Director.
""")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)

# ================= SESSION INIT =================
def init():
    defaults = {
        "step": "login",
        "logged_in": False,
        "email": "",
        "password": "",
        "pin": "",
        "pin_deadline": 0,
        "user_pin": ""
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

init()

st.markdown("<h1 style='text-align:center;'>Beam Designer</h1>", unsafe_allow_html=True)

# ================= LOGIN =================
if st.session_state.step == "login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    msg = st.empty()

    if st.button("Login"):
        resE = supabase.table("users").select("*").eq("email", email).eq("password", password).eq("enable_disable", 'enable').execute()
        resD = supabase.table("users").select("*").eq("email", email).eq("password", password).eq("enable_disable", 'disable').execute()
        if resE.data:
            st.session_state.logged_in = True
            st.session_state.step = "welcome"
            st.rerun()
        elif resD.data:
            st.session_state.logged_in = False
            st.session_state.step = "disable"
            st.rerun()
        else:
            msg.error("❌ Incorrect email or password")

    if st.button("Create New Account"):
        st.session_state.step = "signup"
        st.rerun()

# ================= SIGNUP =================
if st.session_state.step == "signup":
    st.subheader("Create Account")

    # مدخلات (آمنة مع rerun)
    st.session_state.email = st.text_input("Email", value=st.session_state.email)
    st.session_state.password = st.text_input(
        "Password",
        type="password",
        value=st.session_state.password
    )

    msg = st.empty()

    # متغير حماية من إعادة الإرسال
    if "pin_sent" not in st.session_state:
        st.session_state.pin_sent = False

    if st.button("Send Verification Code"):

        # 🔒 منع التكرار بسبب rerun
        if st.session_state.pin_sent:
            msg.warning("⏳ Verification code already sent")
        
        elif not is_valid_email(st.session_state.email):
            msg.error("❌ Invalid email")

        elif not st.session_state.password:
            msg.error("❌ Password required")

        else:
            # 🔎 فحص وجود الإيميل مرة واحدة فقط
            res = supabase.table("users") \
                .select("id") \
                .eq("email", st.session_state.email) \
                .limit(1) \
                .execute()

            if res.data:
                msg.error("❌ This email is already registered. Please login.")
            
            else:
                # ✉️ إرسال PIN مرة واحدة فقط
                pin = str(random.randint(100000, 999999))
                send_pin_email(st.session_state.email, pin)

                st.session_state.pin = pin
                st.session_state.pin_deadline = time.time() + PIN_EXPIRY
                st.session_state.pin_sent = True   # 🔒 قفل الإرسال
                st.session_state.step = "verify"

                st.rerun()

    # زر الرجوع
    if st.button("Back"):
        st.session_state.pin_sent = False  # إعادة الضبط
        st.session_state.step = "login"
        st.rerun()
# ================= VERIFY =================
if st.session_state.step == "verify":
    st.subheader("Verify Email")

    # تثبيت وقت الانتهاء مرة واحدة فقط
    if "pin_deadline" not in st.session_state:
        st.session_state.pin_deadline = time.time() + PIN_EXPIRY

    remaining = int(st.session_state.pin_deadline - time.time())
    remaining = max(remaining, 0)

    # إدخال PIN (ثابت بدون وميض)
    st.session_state.user_pin = st.text_input("PIN", key="pin_input")

    st.write("⏱️ This code is valid for 1 minute only")

    # ===== JavaScript Countdown (UI فقط) =====
    st.components.v1.html(
        f"""
        <div id="timer" style="
            font-size:16px;
            font-weight:600;
            color:#1f77b4;
        ">
            ⏳ Time remaining: {remaining} seconds
        </div>

        <script>
        (function () {{
            let time = {remaining};
            const el = document.getElementById("timer");

            const interval = setInterval(() => {{
                if (!el) return;

                if (time <= 0) {{
                    el.innerHTML = "⛔ PIN expired";
                    clearInterval(interval);
                }} else {{
                    el.innerHTML = "⏳ Time remaining: " + time + " seconds";
                    time--;
                }}
            }}, 1000);
        }})();
        </script>
        """,
        height=60
    )

    # ===== منطق الانتهاء (Python) =====
    if remaining <= 0:
        st.error("⛔ PIN expired")

        if st.button("Back"):
            # إعادة ضبط
            del st.session_state.pin_deadline
            st.session_state.step = "signup"
            st.rerun()

    # ===== زر التحقق =====
    if st.button("Verify"):
        if remaining <= 0:
            st.error("⛔ PIN expired")
        elif st.session_state.user_pin == st.session_state.pin:
            st.session_state.step = "terms"
            st.rerun()
        else:
            st.error("❌ Wrong PIN")

# ================= TERMS =================
if st.session_state.step == "terms":
    st.subheader("Terms of Use")
    st.write("You must agree to continue.")

    if st.button("I Agree"):
        supabase.table("users").insert({
            "email": st.session_state.email,
            "password": st.session_state.password,
            "enable_disable": 'disable'
        }).execute()

        st.session_state.logged_in = False
        st.session_state.step = "disable"
        st.rerun()

    if st.button("I Disagree"):
        st.session_state.step = "login"
        st.rerun()

# ================= disable PAGE ===================
if st.session_state.step == "disable":
    st.subheader("Account Not Activated ❌")
    
    st.warning("⛔ Your account is not activated. You must pay to activate it before using the application.")

    st.write("💡 You can activate your account with the following options:")

    st.markdown("""
    - **$10** → for 1 month
    - **$35** → for a full semester (16 weeks)
    - **$100** → for 1 year
    """)

    st.write("---")
    st.info("After payment, your account will be activated and you will be able to log in immediately.")

    if st.button("Logout"):
        st.session_state.step = "login"
        st.rerun()

# ================= WELCOME =================
if st.session_state.step == "welcome" and st.session_state.logged_in:
    st.success(f"Welcome {st.session_state.email}")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()


#   streamlit run 24.py
