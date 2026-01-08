import streamlit as st

# --- قائمة المستخدمين وكلمات المرور ---
users = {
    "user1": "pass123",
    "user2": "mypassword",
    "admin": "admin123"
}

# --- حالة تسجيل الدخول ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- تسجيل الدخول ---
if not st.session_state.logged_in:
    # --- عرض العنوان في وسط الشاشة ---
    st.markdown("""
    <h1 style='text-align: center; margin-top: 50px;'>Beam designer</h1>
    """, unsafe_allow_html=True)

    username = st.text_input("User name")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("❌ Username or Password is incorrect")


# --- صفحة بعد تسجيل الدخول ---
if st.session_state.logged_in:
    # --- عرض العنوان في وسط الشاشة من الأعلى ---
    st.markdown("""
    <h1 style='text-align: center; margin-top: 20px;'>Beam designer</h1>
    """, unsafe_allow_html=True)

    # --- شريط جانبي مع قائمة منسدلة عند الضغط على File ---
    st.sidebar.title("Menu")

    # قائمة File منسدلة باستخدام expander
    with st.sidebar.expander("Beam section", expanded=False):
        if st.button("rectangle"):
            st.write("📄 تم إنشاء ملف جديد!")
        if st.button("T shape"):
            st.write("📂 تم فتح ملف موجود!")
        if st.button("L shape"):
            st.write("📂 تم فتح ملف موجود!")
        if st.button("Trapezoid"):
            st.write("📂 تم فتح ملف موجود!")
        if st.button("Triangle"):
            st.write("📂 تم فتح ملف !")
    # قائمة Edit منسدلة باستخدام expander
    with st.sidebar.expander("Edit", expanded=False):
        if st.button("Undo"):
            st.write("↩️ تم التراجع")
        if st.button("Redo"):
            st.write("↪️ إعادة تنفيذ")

    # زر تسجيل الخروج
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
