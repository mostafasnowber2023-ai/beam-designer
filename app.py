# هذا الكود جاهز للنشر 
# يحسب المومنت 
# تصميم 
# تحليل 


import streamlit as st
from supabase import create_client
import re, random, time, smtplib
from email.message import EmailMessage
import streamlit.components.v1 as components


# ===== مكتبات أساسية ======================================
import streamlit as st
import math
import pandas as pd
import uuid
# ===== مكتبات رسومات ومخططات =============================
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import numpy as np
# ===== مكتبات للتعامل مع الصور ===========================
from io import BytesIO
from PIL import Image



# ================= CONFIG =================
#SMTP_EMAIL = "mostafa.snowber.2023@gmail.com"
#SMTP_PASSWORD = "YOUR_APP_PASSWORD"
SMTP_EMAIL    = "mostafa.snowber.2023@gmail.com"
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
Lam Executive Director.
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
        resE  = supabase.table("users").select("*").eq("email", email).eq("password", password).eq("enable_disable", 'enable').execute()
        resD  = supabase.table("users").select("*").eq("email", email).eq("password", password).eq("enable_disable", 'disable').execute()
        resLO = supabase.table("users").select("*").eq("email", email).eq("password", password).eq("enable_disable", 'LO').execute()
        if resE.data:
            st.session_state.logged_in = True
            st.session_state.step = "welcome"
            st.session_state.email = email
            st.session_state.password = password
            st.rerun()

        elif resD.data:
            st.session_state.logged_in = False
            st.session_state.step = "disable"
            st.rerun()
        elif resLO.data:
            st.session_state.logged_in = False
            st.session_state.step = "LO"
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

    st.markdown("""
    ### 1️⃣ Educational Purpose Only
    This software is developed strictly for educational and learning purposes.  
    It is intended to help students understand structural design concepts including moment and shear calculations for reinforced concrete beams.

    ### 2️⃣ Explanation-Based Output
    The program provides:
    - Step-by-step solutions  
    - Calculation procedures  
    - Applied formulas  
    - Substitution of numerical values  
    - Final results  

    These outputs are intended for educational support only.

    ### 3️⃣ No Professional Liability
    This software does not guarantee error-free results.  
    The developer assumes no responsibility or liability for any damages, losses, or consequences resulting from the use of this program.

    ### 4️⃣ User Verification Responsibility
    All results must be independently reviewed and verified by a qualified engineer before being used in real construction projects.

    This tool must not be used as the sole basis for structural design decisions.

    ### 5️⃣ Error Reporting
    If a user discovers any error or malfunction, they are encouraged to report it to the developer for review and improvement.

    ### 6️⃣ Code Basis
    All calculations are performed based on ACI 318-19.

    Users must ensure they apply the correct code edition required in their country or project.

    ### 7️⃣ Scope Limitation
    This program:
    - Is limited to rectangular reinforced concrete beams only.
    - Does not support other beam geometries.
    - Can calculate moment capacity.

    ### 8️⃣ Acceptance of Terms
    By using this software, the user confirms that they have read and agreed to these terms and conditions.
    """)
    st.warning("By using this software, you agree to the Terms of Use.")


    #st.write("You must agree to continue.")

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
    st.markdown(
        '<p style="font-size:22px;">Your account will be activated within 24 hours at most. Kindly wait patiently.</p>',
        unsafe_allow_html=True
)
    if st.button("Logout"):
        st.session_state.step = "login"
        st.rerun()

if st.session_state.step == "LO":
    #st.markdown("Houston, we’ve detected a system anomaly.\nThe application is currently offline while our engineers work to restore full operational status.")
    st.markdown(
        '''
        <p style="font-size:22px; font-weight:bold; text-align:center;">
        Houston, we’ve detected a system anomaly.<br>
        The application is currently offline while our engineers work to restore full operational status.
        </p>
        ''',
        unsafe_allow_html=True
    )
    #st.subheader("Account Not Activated ❌")
    #st.warning("⛔ Your account is not activated. You must pay to activate it before using the application.")
    #st.write("💡 You can activate your account with the following options:")
    #st.markdown("""
    #- **$10** → for 1 month
    #- **$35** → for a full semester (16 weeks)
    #- **$100** → for 1 year
    #""")
    #st.write("---")
    #st.info("After payment, your account will be activated and you will be able to log in immediately.")
    

    if st.button("Logout"):
        st.session_state.step = "login"
        st.rerun()




# if st.session_state.step == "moment" :
    

#   streamlit run link4.py















    '''
    # ##############################################################################
    # ##############################################################################
    # ##############################################################################
    '''


# link5.py    moment calculator 



# ========== print with st.markdown function ================
def prin(
    x,
    m: int = 14,
    d: int = 18,
    p: int = 1  # 1=left, 2=center, 3=right
):
    unique_class = f"text-{uuid.uuid4().hex}"
    if   p == 1 or not p : text_align = "left"
    elif p == 2: text_align = "center"
    elif p == 3: text_align = "right"
    st.markdown(
        f"""
        <style>
            @media (max-width: 600px) {{
                .{unique_class} {{
                    font-size: {m}px !important;
                }}
            }}
            @media (min-width: 601px) {{
                .{unique_class} {{
                    font-size: {d}px !important;
                }}
            }}
        </style>
        <p class="{unique_class}"
           style="font-family: Times New Roman, serif;
                  font-weight: normal;
                  text-align: {text_align};">
            {x}
        </p>
        """,
        unsafe_allow_html=True
    )

# ============== Disable scrolling/slider in LaTeX ==============
st.markdown(
    """
    <style>
    .katex-display {
        overflow-x: hidden !important;
        overflow-y: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# ================= لتحديد مكان الكتابة في lat() ========================
def lat(a=1, b=3, t=""):
    c = st.columns([a,b])
    with c[0] :
        st.latex(t)
la = lambda a=1, b=3, t="": [st.latex(t) for c in [st.columns([a,b])] for _ in [c[0]]]

# =================== Poto_Singly() =======================
def Poto_Singly(b, h, d, fig_width=2.2, fig_height=3.2, As=0):
    v , c = 0.5 , 0.8
    main_color = "white"
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    # المستطيل
    rect = patches.Rectangle((0, 0), v, c, linewidth=1.8, edgecolor=main_color, facecolor='none')
    ax.add_patch(rect)
    # مستوى التسليح
    steel_y = 0.15
    num_bars = 4
    x_positions = np.linspace(0.1, v - 0.1, num_bars)
    for x in x_positions:
        ax.add_patch(patches.Circle((x, steel_y), 0.03, edgecolor=main_color, facecolor='none', linewidth=1.3))
    # كتابة As
    if As == 0 :
        ax.text(v/2, steel_y + 0.07, "As", color=main_color, ha='center', va='bottom', fontsize=10)
    else :
        ax.text(v/2, steel_y + 0.07, f'As = {As}', color=main_color, ha='center', va='bottom', fontsize=10)

    # خط قياس d خارج المستطيل
    offset = 0.1
    x_d = v + offset
    ax.add_patch(FancyArrowPatch((x_d, steel_y),(x_d, c), arrowstyle='<->', linewidth=1.5, color=main_color))
    # الأبعاد
    ax.text(v/2, c + 0.02, f'b = {b} mm', color=main_color, ha='center', va='bottom', fontsize=9)
    ax.text(-0.06, c/2, f"h = {h} mm", color=main_color, rotation=90, ha='right', va='center', fontsize=9)
    ax.text(x_d + 0.02, (c + steel_y)/2, f"d = {d} mm", color=main_color, rotation=90, ha='left', va='center', fontsize=9)
    # ضبط الإطار لتقليل المساحات الفارغة
    ax.set_xlim(-0.15, v + 0.21)
    ax.set_ylim(-0.005, c)
    ax.set_aspect('equal')
    ax.axis('off')
    # خلفية داكنة
    fig.patch.set_facecolor('#2b2b2b')
    ax.set_facecolor('#2b2b2b')
    # تحويل الشكل إلى صورة في الذاكرة مع إزالة أي padding إضافي
    buf = BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.06)
    buf.seek(0)
    # تحويل BytesIO إلى صورة PIL
    img = Image.open(buf)
    # عرض الصورة في Streamlit
    #st.image(img, caption="Singley Reinforced Beam Section", width=250)
    w = st.columns([1,2.9,1])
    with w[1]:st.image(img, caption="Singley Reinforced Beam Section", width=250)

# ========================= Poto_doubly() ========================
def Poto_doubly(b, h, dc, dt, fig_width=2.2, fig_height=3.2, As_T=0 , As_C=0):
    v, c = 0.5, 0.8
    main_color = "white"
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # المستطيل
    rect = patches.Rectangle((0, 0), v, c, linewidth=1.8, edgecolor=main_color, facecolor='none')
    ax.add_patch(rect)

    # مستوى التسليح
    steel_y = 0.67  # compression steel
    steel_yt = 0.15 # tension steel
    num_bars = 4
    x_positions = np.linspace(0.1, v - 0.1, num_bars)

    # دوائر التسليح
    for x in x_positions:
        ax.add_patch(patches.Circle((x, steel_y), 0.03, edgecolor=main_color, facecolor='none', linewidth=1.3))
        ax.add_patch(patches.Circle((x, steel_yt), 0.03, edgecolor=main_color, facecolor='none', linewidth=1.3))

    # كتابة As و As'
    if As_T ==0 and As_C ==0 :
        ax.text(v/2, steel_y - 0.12, "As'", color=main_color, ha='center', va='bottom', fontsize=10)
        ax.text(v/2, steel_yt + 0.07, "As", color=main_color, ha='center', va='bottom', fontsize=10)
    else :
        ax.text(v/2, steel_y - 0.12, f"As' = {As_C}", color=main_color, ha='center', va='bottom', fontsize=10)
        ax.text(v/2, steel_yt + 0.07, f'As = {As_T}', color=main_color, ha='center', va='bottom', fontsize=10)

    # خطوط القياس d و d'
    offset = 0.05
    x_d = v + offset
    x_dt = x_d + 0.1
    ax.add_patch(FancyArrowPatch((x_d, steel_y), (x_d, c), arrowstyle='<->', linewidth=1.5, color=main_color))
    ax.add_patch(FancyArrowPatch((x_dt, steel_yt), (x_dt, c), arrowstyle='<->', linewidth=1.5, color=main_color))

    # الأبعاد
    ax.text(v/2, c + 0.04, f'b = {b} mm', color=main_color, ha='center', va='bottom', fontsize=9)
    ax.text(-0.06, c/2, f"h = {h} mm", color=main_color, rotation=90, ha='right', va='center', fontsize=9)
    ax.text(x_d + 0.03, (c + steel_y)/2, f"d' = {dc} mm", color=main_color, rotation=90, ha='left', va='center', fontsize=9)
    ax.text(x_d + 0.15, (c + steel_yt)/2, f"d  = {dt} mm", color=main_color, rotation=90, ha='left', va='center', fontsize=9)

    # ضبط الإطار
    ax.set_xlim(-0.15, v + 0.28)
    ax.set_ylim(-0.12, c + 0.12)
    ax.set_aspect('equal')
    ax.axis('off')

    # خلفية داكنة
    fig.patch.set_facecolor('#2b2b2b')
    ax.set_facecolor('#2b2b2b')

    # تحويل الشكل إلى صورة في الذاكرة
    buf = BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.06)
    buf.seek(0)
    img = Image.open(buf)
    e = st.columns([1,1.2,1])
    with e[1]:st.image(img, caption="Doubly Reinforced Beam Section", width=250)


# ========================== diameter() =======================
def diameter(d):
    std = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32]
    if d > 32 : return 10000
    return min(std, key=lambda x: abs(x - d-1))

#                                 دالة انشاء الجدول

def table (data):
    print ()
    # عناوين الأعمدة بالصيغة الرياضية
    columns = [  r"$\#\;\phi\;D$",  r"$spacing\ (mm)$",  r"$A_s\ provided\ (mm^2)$",  r"$A_{s,required} \,/\, A_{s,provided}$"  ]
    # إنشاء الشكل
    fig, ax = plt.subplots(figsize=(8, 1.0))
    ax.axis('off')  # إخفاء المحاور
    table = ax.table(cellText=data, colLabels=columns, loc='center', cellLoc='center' )
    # 🔹 حجم الخط
    header_fontsize = 15   # عناوين الأعمدة
    body_fontsize   = 11   # بيانات الجدول
    # تعيين حجم خط العناوين
    for col in range(len(columns)):
        table[(0, col)].set_fontsize(header_fontsize)
        table[(0, col)].set_text_props(weight='bold')
    # تنسيق الجدول
    table.scale(1, 1.8)
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    # تنسيق الحدود مثل الوورد
    for (row, col), cell in table.get_celld().items():
        cell.set_linewidth(1.2)
    plt.show()
    print ()

# ================= table disply function ==================
def Table(L):
    columns = ['Bars', 'spacing (mm)', 'As provided (mm²)', 'As required / As provided']
    df = pd.DataFrame(L, columns=columns)
    table_html = df.to_html(index=False)
    table_html = f"""
    <style>
        table {{
            width: auto;
            border-collapse: collapse;
        }}
        th, td {{
            text-align: center;  /* توسيط كل محتوى الخلايا */
            padding: 6px;
            border: 1px solid black;
        }}
    </style>
    {table_html}
    """
    st.markdown(table_html, unsafe_allow_html=True)

#                          دالة توزيع الحديد
def TS(b,side_cover,As) :
    n_max = ((b-2*side_cover)/65  + 1)
    n_min = ((b-2*side_cover)/150 + 1)
    n_max0 = math.floor(n_max)
    n_min0 = math.floor(n_min) + 1
    if As > (math.pi / 4) * 32*32 * n_max0:
        prin(r'The steel is more than what the section can accommodate in a single layer',p=2)
        return
    L = []
    for i in range(n_min0, n_max0 + 1):
        D = diameter(((4*As)/(math.pi*i))**0.5)
        s = round((b-2*side_cover)/(i-1),2)
        As00 = round((math.pi /4)*(D**2) * i,2)
        z = round (As / As00,3)
        if D != diameter(((4*As)/(math.pi*(i-1)))**0.5) and D <= 32 :
            L.append([ str(i)+' φ '+ str(D) , str(s) , str(As00) ,str(z) ])
    if len(L) == 0 :
        prin('➔ The required area of steel As very small, Use small section dimensions')
    elif len(L) == 1 :
        prin('➔ The required area of steel As can be achieved only by this singl option')
        q = st.columns([1,8,1])
        with q[1]: Table(L)
    else :
        prin('➔ The required area of steel As can be achieved by these options',p=2)
        q = st.columns([1,8,1])
        with q[1]: Table(L)
        prin('➔ You can choose only one option with its corresponding spacing ',p=2)

# =================== Strain Diagram function =====================
def Strain_Diagram(d , c , ds , D_A = 0):
    main_color = "white"
    fig, ax = plt.subplots(figsize=(2.2, 3.4))

    A , B , C , D , E , F = 0.25 , 0.6 , 0.2 , 0.35 , 0.25 , 0.1

    ax.plot( [A, A+C          ], [B, B          ], color=main_color, linewidth=1.6 ) # خط سترين الباطون
    if D_A == 1:
        pass
    else :
        ax.plot( [A, (B-F)*(A+C)/B], [B-F, B-F      ], color=main_color, linewidth=1.6 ) # خط سترين الحديد العلوي
        ax.plot( [A-0.15 , A-0.15 ], [B, B-F        ], color=main_color, linewidth=1.6 ) # خط البعد القصير

    ax.plot( [0, A            ], [0, 0          ], color=main_color, linewidth=1.6 ) # خط سترين الحديد السفلي
    ax.plot( [A, A            ], [B, 0          ], color=main_color, linewidth=1.6 ) # الخط السترين العمودي ليس خط بعد
    ax.plot( [A+C, 0          ], [B, 0          ], color=main_color, linewidth=1.6 ) # الخط المائل
    ax.plot( [A+D, A+D        ], [B, 0          ], color=main_color, linewidth=1.6 ) # خط البعد الطويل
    ax.plot( [A+E, A+E        ], [B, (A*B)/(A+C)], color=main_color, linewidth=1.6 ) # خط البعد المتوسط
    #ax.plot( [A-0.15 , A-0.15 ], [B, B-F        ], color=main_color, linewidth=1.6 ) # خط البعد القصير

    ax.text(A+0.1,B+0.05,r"$\varepsilon_{c}=0.003$",color=main_color,ha='center',fontsize=10)
    if D_A == 1 :
        pass
    else :
        ax.text(A-0.1, B-F  ,r"$\varepsilon_s'$"       ,color=main_color            ,fontsize=10)

    if D_A == 0 or D_A == 1:
        ax.text(0, -0.08    ,r"$\varepsilon_s =0.005$" ,color=main_color            ,fontsize=10)
    else : 
        ax.text(0.1, -0.04    ,r"$\varepsilon_s$" ,color=main_color            ,fontsize=10)

    ax.text( A+D+0.05 , B/2                  , f"d = {d} mm"     , rotation=90, color=main_color,  fontsize=7, va='center' )
    ax.text( A+E+0.025, (B+(A*B)/(A+C))/2    , f"C = {c} mm"     , rotation=90, color=main_color,  fontsize=7, va='center' )
    if D_A == 1 :
        pass
    else :
        ax.text( A-0.21   , (B+(A*B)/(A+C))/2+0.1, f"d' = {ds} mm", rotation=90, color=main_color,  fontsize=7, va='center' )

    ax.set_xlim(0, 0.7)
    ax.set_ylim(0, 0.7)
    ax.set_aspect('equal')
    ax.axis('off')

    fig.patch.set_facecolor('#2b2b2b')
    ax.set_facecolor('#2b2b2b')

    plt.tight_layout(pad=0)
    plt.show()

    # ############################ اضافة من عندي وزبطة ########################
    # حلت مشكلة عدم ظهور رسمة السترين
    # تحويل الشكل إلى صورة في الذاكرة مع إزالة أي padding إضافي
    buf = BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.06)
    buf.seek(0)
    # تحويل BytesIO إلى صورة PIL
    img = Image.open(buf)
    # عرض الصورة في Streamlit
    #st.image(img, caption="Singley Reinforced Beam Section", width=250)
    w = st.columns([1,2.9,1])
    with w[1]:st.image(img, caption="Singley Reinforced Beam Section", width=250)
    # #################################################################

# =================== Moment_Beam() =====================
def Moment_Beam(Mu , b , h , fc , fy , nd , T_cover , C_cover) :
    prin("Beam Design for Moment",p=2,m=18,d=25)
    prin("The given data are as follows",p=2)
    st.latex(rf"""
    \begin{{aligned}}
    \qquad M_{{u}} &= {Mu} \text{{ KN.M}} \\
    \qquad f'_{{c}} &= {fc} \text{{ MPa}} \\
    \qquad f_{{y}} &= {fy} \text{{ MPa}}
    \end{{aligned}}
    """)
    if fc < 17 :
        st.latex(r"""
            f'_c < 17 \;\; \text{MPa}
            \;\;\Rightarrow\;\;
            \text{concrete cannot be used according to ACI}
            """) 
        return
    #space_lyaer = 40
    #T_cover = 60
    #C_cover = 60
    side_cover = 40
    d_T = h - T_cover
    d_C = C_cover
    prin("➔ Assume it is a Rectangular section, Singly reinforce with this dimentions",p=2)
    k = st.columns([1,2,1])
    with k[1] : Poto_Singly(b, h, d_T)
    if 1-((2.61*Mu*1000000)/(b*d_T*d_T*fc)) < 0 :
        prin('The dimensions are not sufficient; you need larger dimensions')
        return
    prin(r"➔ First, Calculat ρ using the following formula ",p=2)
    p = round (((0.85*fc)/fy)*(1-(1-((2.61*Mu*1000000)/(b*d_T*d_T*fc)))**0.5),nd)
    st.latex(r"\qquad \rho = \frac{0.85 f'_c}{f_y} \left( 1 - \sqrt{1 - \frac{2.61 M_u}{b d^2 f'_c}} \right) = " + str(p))
    prin("➔ Calculate ρ<sub>min</sub> using the following formula",p=2)
    if (1.4/fy)>((0.25*(fc**0.5))/fy) : p_min = round(1.4/fy,nd)
    else :p_min =round((0.25*(fc**0.5))/fy,nd)
    st.latex(r"\qquad \rho_{\min} = \max\left[\frac{1.4}{f_y}, \frac{0.25 \sqrt{f'_c}}{f_y}\right] = " + str(p_min))
    if p >  p_min :
        st.latex(r"\qquad \rho \text{ \: > \: } \rho_{\min} \text{ \: ➔ \: OK }")
        p = p
    else :
        st.latex(r"\qquad \rho \text{ \: < \: } \rho_{\min} \text{ \: ➔ \: So use \: } A_s \, \text{min}")
        if p_min * b*  d_T < p*b* d_T*(4/3) :k1 = round(p_min * b*  d_T,2)
        else :k1 = round(p*b* d_T*(4/3),2)
        st.latex(rf"\qquad A_{{s,\min}} = \min \left[ \frac{{4}}{{3}} A_{{s,\text{{calculated}}}},\, \rho_{{\min}} b d \right] = {k1}\:\: \text{{mm}}^2")
        #TS(b,side_cover,k1)
        ###################################################
        ###################################################
        ###################################################
        ###################################################
        return
        p = p_min
    prin(r"➔ Let’s calculate β₁",p=2)
    if fc >= 56 :
        st.latex(rf"\qquad f_c = {fc} \ge 56 \; Mpa \;\Rightarrow\; \beta_1 = 0.65")
        beta_1 = 0.65
    elif fc >= 17 and fc <= 28 :
        st.latex(rf"\qquad 17 \le fc = {fc} \le 28\; Mpa \;\; \Rightarrow \; \beta_1 = 0.85")
        beta_1 = 0.85
    else :
        st.latex(r"\qquad 28 < f_c = %s < 56\;Mpa \;\;\Rightarrow\;\; \text{Linear Interpolation, use this formula to find } \beta_1" % fc)
        beta_1 =  round(0.85-0.05*((fc-28)/7),4)
        st.latex(rf"\qquad \beta_1 = 0.85 - 0.05 \left( \frac{{f'_c - 28}}{{7}} \right) = {beta_1}")
    st.latex(r"\text{➔ After that, Calculate \: } \rho_{max,\; singly,\; f_y = 420 \; \text{MPa}}")
    p_max_singly = round (0.375 * beta_1*0.85*fc*(1/fy),nd)
    st.latex(
        rf"\qquad \rho_{{max,\; singly,\; f_y = 420 \; \text{{MPa}}}}"
        rf" = 0.375\,\beta_1 \frac{{0.85 f'_c}}{{f_y}} = {p_max_singly}"
    )
    if p >  p_max_singly :
        st.latex(r"\qquad \rho \text{ \: > \: } \rho_{max,\; singly,\; f_y = 420 \; \text{MPa}}")
        prin(r"➔ So, We need doubly reinforcement section, Assuming that it is singly reinforced is incorrect",p=2)
        Poto_doubly (b,h,d_C,d_T)
        As1 = round(p_max_singly * d_T * b,2)
        a = round((As1 * fy)/(0.85*fc*b),2)
        M1 = round( (0.9*As1 * fy*(d_T-0.5*a))/1000000,2)
        M2 = round (Mu - M1,2)
        C = round(a /0.85,3 )
        strain_C =round(0.003-0.003*d_C*(1/C),8)
        if strain_C > 0.0021 : fy_c = 420
        else : fy_c = 200000 * strain_C
        As2 = round ((1000000*M2) /(0.9*fy_c*(d_T-d_C)),2)
        st.markdown(rf"""
        $$
        \begin{{aligned}}
        A_s & = \rho_{{max}}\, b\, d = {As1} \:\text{{mm}}^2 \\[3mm]
        a & = \frac{{A_s f_y}}{{0.85 f'_c \: b}} = {a} \:\text{{mm}} \\[3mm]
        \phi M_{{n1}} & = \phi A_s f_y \left(d - \frac{{a}} {{2}}\right) = {M1} \:\text{{kN.m}} \\[3mm]
        \phi M_{{n2}} & = M_u - \phi M_{{n1}} = {M2} \:\text{{kN.m}}
        \end{{aligned}}
        $$
        """)
        st.latex(rf"\text{{The depth of neutral axis \:}} C = \frac{{a}}{{0.85}} = {C}\:\: \text{{mm}}\\[1mm]")
        st.markdown(r"$$\text{From the Strain Diagram, we can find the strain in the compression steel, as shown in the following figure}$$")
        Strain_Diagram(d_T , C ,d_C)
        st.latex(rf"\text{{Compression steel = }} A'_s = {As2} \:\: \text{{mm}}^2")
        #TS(b,side_cover,As2)
        AsT = round(As1 + As2,2)
        st.latex(rf"\text{{Tension Steel = }} A_s = {AsT} \:\: \text{{mm}}^2")
        #TS(b,side_cover,AsT)
    else :
        st.latex(r"\qquad \rho \text{ \: < \: } \rho_{max,\; singly,\; f_y = 420 \; \text{MPa}} \text{ \: ➔ \: OK}")
        st.latex(r"\text{Our assumption is correct that it is singly reinforced, so we do not need compression steel}")
        st.latex(r"\text{➔ Let’s calculate the area of steel } A_s \text{ using the following equation}")
        As0 = round (p * b * d_T,2)
        st.latex(rf"\qquad A_s = \rho\, b\, d \text{{ \: = \: }} {As0}\:\:\: \text{{mm}}^2")
        #TS(b,side_cover,As0)

#Moment_Beam(1100,350,700,30,420,7)
#Moment_Beam(Mu , b , h , fc , fy, nd)

def asd ( a,As_C_A , As_T_A , b , h , fc , fy , T_cover , C_cover ,d_C,d_T, pr='print'):
    if pr == 'print':
        st.latex(rf"""
        a = \frac{{(A_s - A'_s)\, f_y}}{{0.85\, f'_c\, b}}
        = {a:.1f} mm
        """)
        prin(r"➔ Let’s calculate β₁",p=2)
    if fc >= 56 :
        if pr == 'print':
            st.latex(rf"\qquad f_c = {fc} \ge 56 \; Mpa \;\Rightarrow\; \beta_1 = 0.65")
        beta_1 = 0.65
    elif fc >= 17 and fc <= 28 :
        if pr == 'print':
            st.latex(rf"\qquad 17 \le fc = {fc} \le 28\; Mpa \;\; \Rightarrow \; \beta_1 = 0.85")
        beta_1 = 0.85
    else :
        if pr == 'print':
            st.latex(r"\qquad 28 < f_c = %s < 56\;Mpa \;\;\Rightarrow\;\; \text{Linear Interpolation, use this formula to find } \beta_1" % fc)
        beta_1 =  round(0.85-0.05*((fc-28)/7),4)
        if pr == 'print':
            st.latex(rf"\qquad \beta_1 = 0.85 - 0.05 \left( \frac{{f'_c - 28}}{{7}} \right) = {beta_1}")
    C = round (a / beta_1,1)
    if pr == 'print':
        st.latex(rf"""
        c = \frac{{a}}{{\beta_1}}
        = {C:.1f} mm
        """)
    k = st.columns([0.7,2,1])
    with k[1] : 
        if pr == 'print':
            Strain_Diagram(d_T , C ,d_C , D_A = 0)
    epsilon_s_bar = round ((0.003/C)*(C-C_cover),5)
    if As_C_A == 0:
        epsilon_s_bar = 0
    epsilon_s = round ((0.003/C)*(d_T-C),5)
    if pr == 'print':
        if As_C_A != 0:
            st.latex(rf"\varepsilon_s' = {epsilon_s_bar:.5f}")
        st.latex(rf"\varepsilon_s = {epsilon_s:.5f}")
    f_s = round(epsilon_s * 200000,0)
    if f_s > fy :
        if pr == 'print':
            st.latex(rf"f_s = \varepsilon_s E_s = {f_s:.0f} \; Mpa > f_y= {fy:.0f} \; Mpa\;\; \Rightarrow \; use \;\; f_s = f_y= {fy:.0f} Mpa")
        f_s = fy
    else :
        if pr == 'print':
            st.latex(rf"f_s = \varepsilon_s E_s = {f_s:.0f} Mpa")
    f_s_bar = round(epsilon_s_bar * 200000,0)
    if pr == 'print':
        if As_C_A != 0:
            st.latex(rf"f_s' = \varepsilon_s' E_s = {f_s_bar:.0f} Mpa")
    Cc = round(0.85 * fc * b * a * 0.001,1)
    if pr == 'print':
        st.latex(rf"compression \; in\; concrete, C_c = 0.85 f'_c b a = {Cc:.1f}\; KN")
    Cs = round(As_C_A * f_s_bar * 0.001,1)
    if pr == 'print':
        if As_C_A != 0:
            st.latex(rf"compression \; in\; steel, C_s = A'_s f'_s = {Cs:.1f}\; KN")
    T = round(As_T_A * f_s * 0.001,1)
    if pr == 'print':
        st.latex(rf"tension \; in\; steel, T = A_s f_s = {T:.1f}\; KN")
    total_compression = Cs+ Cc
    if pr == 'print':
        if As_C_A != 0:
            st.latex(rf"Total \; compression \; force = C_s + C_c = {total_compression:.1f}\; KN")
    E = T / total_compression 
    Error_ = round(abs(E-1) * 100,0)
    if pr == 'print':
        if As_C_A != 0 :
            st.latex(rf"""\frac{{T = {T:.1f}}}{{C = {total_compression:.1f}}}= {E:.2f} \Rightarrow Error = {Error_:.0f}\; \% """)
            st.markdown("---")
            st.latex(rf"Try\; a\; new\; value\; of, a:")
    if pr == 'values' :
        st.latex(rf"\varepsilon_s' = {epsilon_s_bar:.5f} \Rightarrow f'_s = {f_s_bar:.1f} \; Mpa")
        st.latex(rf"\varepsilon_s = {epsilon_s:.5f} \Rightarrow f_s = {f_s:.1f} \; Mpa")
        st.latex(rf""" C_c = {Cc:.1f}\; KN \;\; , \;\; C_s = {Cs:.1f}\; KN \Rightarrow  C = C_c+C_s  \; = \; {total_compression:.1f}\; KN """)
        #st.latex(rf""" C_s = {Cs:.1f}\; KN """)
        st.latex(rf""" \Rightarrow\;\; C = {total_compression:.1f}\; KN \;\; , \;\;  T = {T:.1f}\; KN """)
        E = T / total_compression 
        Error_ = round(abs(E-1) * 100,0)
        if As_C_A != 0 :
            st.latex(rf"""\frac{{T = {T:.1f}}}{{C = {total_compression:.1f}}}= {E:.2f} \Rightarrow Error = {Error_:.0f}\; \% """)
            prin("""You can recalculate a new value for a to achieve a lower error %, but this is sufficient for now.""")
        M_by_phi = (Cc*(d_T-0.5*a)+Cs*(d_T-d_C))/1000
        return epsilon_s , M_by_phi
    if As_C_A != 0 : pass
        #st.latex(rf"""\frac{{T = {T:.1f}}}{{C = {total_compression:.1f}}}= {E:.2f} \Rightarrow Error = {Error_:.0f}\; \% """)
    M_by_phi = (Cc*(d_T-0.5*a)+Cs*(d_T-d_C))/1000
    return T , Cs ,epsilon_s , M_by_phi


def Moment_Beam_A( As_C_A , As_T_A , b , h , fc , fy , nd , T_cover , C_cover) :
    prin("Beam Design for Moment",p=2,m=18,d=25)
    prin("The given data are as follows",p=2)
    if As_C_A == 0:
        st.latex(rf"""
        \begin{{aligned}}
        \qquad f'_{{c}} &= {fc} \text{{ MPa}} \\
        \qquad f_{{y}} &= {fy} \text{{ MPa}} \\
        \qquad A_{{s}}T &= {As_T_A} \text{{ mm}}^2

        \end{{aligned}}
        """)
    else :
        st.latex(rf"""
        \begin{{aligned}}
        \qquad f'_{{c}} &= {fc} \text{{ MPa}} \\
        \qquad f_{{y}} &= {fy} \text{{ MPa}} \\
        \qquad A_{{s}}C &= {As_C_A} \text{{ mm}}^2 \\
        \qquad A_{{s}}T &= {As_T_A} \text{{ mm}}^2

        \end{{aligned}}
        """)

    if fc < 17 :
        st.latex(r"""
            f'_c < 17 \;\; \text{MPa}
            \;\;\Rightarrow\;\;
            \text{concrete cannot be used according to ACI}
            """) 
        return
    #space_lyaer = 40
    #T_cover = 60
    #C_cover = 60
    side_cover = 40
    d_T = h - T_cover
    d_C = C_cover
    #prin("➔ Assume it is a Rectangular section, Singly reinforce with this dimentions",p=2)
    k = st.columns([0.45,2,1])
    if As_C_A == 0 :
        with k[1] : Poto_Singly(b, h, d_T,As =As_T_A )
    else: 
        with k[1] : Poto_doubly (b,h,d_C,d_T, As_T=As_T_A , As_C=As_C_A)
        prin("➔ Assume that both steel yield, so1",p=2)
    if As_C_A == 0: 
        a = ((As_T_A - As_C_A)*fy)/(0.85*fc*b)
        st.latex(rf"""T = C \Rightarrow a = \frac{{A_s f_y}}{{0.85\, f'_c\, b}}= {a:.1f} mm""")
        if fc >= 56 :
            st.latex(rf"\qquad f_c = {fc} \ge 56 \; Mpa \;\Rightarrow\; \beta_1 = 0.65")
            beta_1 = 0.65
        elif fc >= 17 and fc <= 28 :
            st.latex(rf"\qquad 17 \le fc = {fc} \le 28\; Mpa \;\; \Rightarrow \; \beta_1 = 0.85")
            beta_1 = 0.85
        else :
            st.latex(r"\qquad 28 < f_c = %s < 56\;Mpa \;\;\Rightarrow\;\; \text{Linear Interpolation, use this formula to find } \beta_1" % fc)
            beta_1 =  round(0.85-0.05*((fc-28)/7),4)
            st.latex(rf"\qquad \beta_1 = 0.85 - 0.05 \left( \frac{{f'_c - 28}}{{7}} \right) = {beta_1}")
        C = round (a / beta_1,1)
        st.latex(rf"""
        c = \frac{{a}}{{\beta_1}}
        = {C:.1f} mm
        """)
        Strain_Diagram(d_T , C ,d_C , D_A = 1)
        epsilon_t = round ((0.003/C)*(d_T-C),5)
        st.latex(rf"\varepsilon_t = {epsilon_t}")

        if epsilon_t < 0.002 or epsilon_t == 0.002 :
            phi = 0.65
            st.latex(rf"\varepsilon_t \le 0.002 \Rightarrow \phi = {phi:.2f}")
        elif epsilon_t < 0.005 :
            phi = ((0.9-0.65)*(epsilon_t-0.002))/(0.005-0.002)+0.65
            st.latex(rf"0.002 < \varepsilon_t < 0.005 \; Interpolation \Rightarrow \phi = {phi:.3f}")
        elif epsilon_t > 0.005 or epsilon_t == 0.005 :
            phi = 0.9
            st.latex(rf"0.005 \le \varepsilon_t \Rightarrow \phi = {phi:.2f}")
        M_ = round (phi * As_T_A * fy *(d_T-(a/2)) *0.000001,2)
        st.latex(rf"""\phi M_n = \phi A_s f_y (d - \frac{{a}}{{2}})\;= {M_:.2f} \; KN.M""")


        return 
    a = ((As_T_A - As_C_A)*fy)/(0.85*fc*b)
    T , Cs , epsilon_s , M_by_phi =  asd (a, As_C_A , As_T_A , b , h , fc , fy , T_cover , C_cover ,d_C,d_T, pr='print')
    if As_C_A != 0 :
        a_new = round (1000*(T-Cs)/(0.85 * fc * b),1)
        st.latex(rf"""a = \frac{{T-C_s}}{{0.85f'_c b}}= {a_new:.1f} \; mm""")
        st.latex(rf"""Resolve\; for\; a = {a_new:.1f} \; mm""")
        if As_C_A != 0 :
            epsilon_s , M_by_phi =  asd (a_new, As_C_A , As_T_A , b , h , fc , fy , T_cover , C_cover ,d_C,d_T, pr='values')
    if epsilon_s < 0.002 or epsilon_s == 0.002 :
        phi = 0.65
        st.latex(rf"\varepsilon_s \le 0.002 \Rightarrow \phi = {phi:.2f}")
    elif epsilon_s < 0.005 :
        phi = ((0.9-0.65)*(epsilon_s-0.002))/(0.005-0.002)+0.65
        st.latex(rf"0.002 < \varepsilon_s < 0.005 \; Interpolation \Rightarrow \phi = {phi:.3f}")
    elif epsilon_s > 0.005 or epsilon_s == 0.005 :
        phi = 0.9
        st.latex(rf"0.005 \le \varepsilon_s \Rightarrow \phi = {phi:.2f}")
    M = M_by_phi *phi
    st.latex(rf"""\phi M_n = \phi \left[ C_c \left( d - \frac{{a}}{{2}} \right) + C_s (d - d') \right] = {M:.2f} \;KNM""")


# ================= WELCOME =================
if st.session_state.step == "welcome" and st.session_state.logged_in:
    #st.success(f"Welcome {st.session_state.email}")
    #st.success(f"Beam Designer")
    L , m , R = st.columns([1.5,1,1])
    with L:
        fc = st.text_input("fc' = Concrete compressive strength (Mpa)")
        fy = st.text_input("fy = (Mpa)")
    with m:
        h  = st.text_input("h = Beam height (mm)")
        b  = st.text_input("b = Beam width (mm)")
    with R:
        Covre_C = st.text_input("Compression steel cover (mm)")
        Covre_T = st.text_input("tension steel cover (mm)")
    A = st.columns([1.5,2])
    with A[0]:
        M  = st.text_input("Mu = Ultimate Moment (KN.M)")
    with A[1]:
        As_C_A = st.text_input("As' = area of Compression steel (mm^2)")
        As_T_A = st.text_input("As = area of tension steel (mm^2)")
    #A2 = st.columns([1,1])
    #with A2[0]:
    if st.button("Design"):
        Moment_Beam (float(M), float(b), float(h), float(fc), float(fy), 7, float(Covre_T) , float(Covre_C))
        # Moment_Beam(Mu , b , h , fc , fy , nd , T_cover , C_cover)
    #with A2[1]:
    if st.button("Analyze"):
        Moment_Beam_A (float(As_C_A), float(As_T_A), float(b), float(h), float(fc), float(fy), 7, float(Covre_T) , float(Covre_C))
        # Moment_Beam(Mu , b , h , fc , fy , nd , T_cover , C_cover)


    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    if st.sidebar.button("terms"):
        st.session_state.step = "terms0"
        st.rerun()
    if st.sidebar.button("password"):
        st.session_state.step = "password"
        st.rerun()

if st.session_state.step == "password":
    #st.subheader("password")

    email = st.session_state.email
    #password = st.session_state.password
    response = supabase.table("users") \
    .select("password") \
    .eq("email", email) \
    .single() \
    .execute()
    password = response.data["password"]

    st.markdown(
        f"""
        <p style="font-size:22px; font-weight:bold; color:#1E90FF;">
        Password :   {password}
        </p>
        """,
        unsafe_allow_html=True
    )
    # Email    :   {email}<br>

    Q = st.columns([1.6,1])

    with Q[0]:
        N_password = st.text_input("New password")
        msg = st.empty()
    with Q[1]:
        # استخدام HTML + CSS لتعديل ارتفاع الزر
        st.markdown(
            """
            <style>
            div.stButton > button:first-child {
                margin-top: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button("Save"):
            if N_password :
                response = supabase.table("users").update({
                    "password": N_password
                }).eq("email", email).execute()
                #st.rerun()
                msg.success("✅ New password has been saved successfully!")

    if st.button("Back"):
        st.session_state.step = "welcome"
        st.rerun()









if st.session_state.step == "terms0":
    st.subheader("Terms of Use")

    st.markdown("""
    ### 1️⃣ Educational Purpose Only
    This software is developed strictly for educational and learning purposes.  
    It is intended to help students understand structural design concepts including moment and shear calculations for reinforced concrete beams.

    ### 2️⃣ Explanation-Based Output
    The program provides:
    - Step-by-step solutions  
    - Calculation procedures  
    - Applied formulas  
    - Substitution of numerical values  
    - Final results  

    These outputs are intended for educational support only.

    ### 3️⃣ No Professional Liability
    This software does not guarantee error-free results.  
    The developer assumes no responsibility or liability for any damages, losses, or consequences resulting from the use of this program.

    ### 4️⃣ User Verification Responsibility
    All results must be independently reviewed and verified by a qualified engineer before being used in real construction projects.

    This tool must not be used as the sole basis for structural design decisions.

    ### 5️⃣ Error Reporting
    If a user discovers any error or malfunction, they are encouraged to report it to the developer for review and improvement.

    ### 6️⃣ Code Basis
    All calculations are performed based on ACI 318-19.

    Users must ensure they apply the correct code edition required in their country or project.

    ### 7️⃣ Scope Limitation
    This program:
    - Is limited to rectangular reinforced concrete beams only.
    - Does not support other beam geometries.
    - Can calculate moment capacity.

    ### 8️⃣ Acceptance of Terms
    By using this software, the user confirms that they have read and agreed to these terms and conditions.
    """)
    st.warning("By using this software, you agree to the Terms of Use.")

    if st.button("Back"):
        st.session_state.step = "welcome"
        st.rerun()
