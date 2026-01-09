import streamlit as st
from supabase import create_client

# ---------------- Supabase ----------------
SUPABASE_URL = "https://utvubafvttzbuvlkchig.supabase.co"
SUPABASE_KEY = "sb_publishable_GOeCyF4B9YODOXDLNWu7HQ_JAib3deP"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ---------------- عنوان التطبيق ----------------
st.markdown("""
<h1 style='text-align:center;margin-top:50px;font-size:clamp(26px,4vw,42px);font-weight:600;'>
Beam Designer
</h1>
""", unsafe_allow_html=True)

# ---------------- تسجيل الدخول أو إنشاء حساب ----------------
if not st.session_state.logged_in:

    if st.session_state.show_signup:
        # ---------- شاشة إنشاء حساب ----------
        st.subheader("Create New Account")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Create Account", key="create_acc"):
            if new_email and new_password:
                try:
                    supabase.table("users").insert({
                        "email": new_email,
                        "password": new_password
                    }).execute()
                    st.success("✅ Account created successfully!")
                    st.session_state.logged_in = True
                    st.session_state.user_email = new_email
                    st.session_state.show_signup = False
                    st.experimental_rerun()
                except Exception:
                    st.error("❌ Email already exists")
            else:
                st.error("❌ Please fill all fields")

        if st.button("Back to Login", key="back_login"):
            st.session_state.show_signup = False
            st.experimental_rerun()

    else:
        # ---------- شاشة تسجيل الدخول ----------
        st.subheader("Login")
        login_email = st.text_input("Email", key="login_email")
        login_pass = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn"):
            result = supabase.table("users").select("*").eq("email", login_email).eq("password", login_pass).execute()
            if result.data:
                st.session_state.logged_in = True
                st.session_state.user_email = login_email
                st.experimental_rerun()
            else:
                st.error("❌ Email or Password is incorrect")

    # زر إنشاء حساب جديد يظهر دائمًا
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("➕ Create New Account", key="show_signup_btn"):
        st.session_state.show_signup = True
        st.experimental_rerun()

# ---------------- بعد تسجيل الدخول ----------------
if st.session_state.logged_in:
    st.markdown(f"""
    <h1 style='text-align:center;margin-top:-60px;font-size:clamp(26px,4vw,42px);font-weight:600;'>
    Beam Designer
    </h1>
    <p style='text-align:center;'>Welcome {st.session_state.user_email}</p>
    """, unsafe_allow_html=True)

    st.sidebar.title("Menu")
    with st.sidebar.expander("Beam section"):
        st.button("Rectangle")
        st.button("T shape")
        st.button("L shape")
        st.button("Trapezoid")
        st.button("Triangle")

    with st.sidebar.expander("Edit"):
        st.button("Undo")
        st.button("Redo")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.experimental_rerun()
