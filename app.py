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
def Poto_Singly(b, h, d, fig_width=2.2, fig_height=3.2):
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
    ax.text(v/2, steel_y + 0.07, "As", color=main_color, ha='center', va='bottom', fontsize=10)
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
def Poto_doubly(b, h, dc, dt, fig_width=2.2, fig_height=3.2):
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
    ax.text(v/2, steel_y - 0.12, "As'", color=main_color, ha='center', va='bottom', fontsize=10)
    ax.text(v/2, steel_yt + 0.07, "As", color=main_color, ha='center', va='bottom', fontsize=10)

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
def Strain_Diagram(d , c , ds):
    main_color = "white"
    fig, ax = plt.subplots(figsize=(2.2, 3.4))

    A , B , C , D , E , F = 0.25 , 0.6 , 0.2 , 0.35 , 0.25 , 0.1

    ax.plot( [A, A+C          ], [B, B          ], color=main_color, linewidth=1.6 ) # خط سترين الباطون
    ax.plot( [A, (B-F)*(A+C)/B], [B-F, B-F      ], color=main_color, linewidth=1.6 ) # خط سترين الحديد العلوي
    ax.plot( [0, A            ], [0, 0          ], color=main_color, linewidth=1.6 ) # خط سترين الحديد السفلي
    ax.plot( [A, A            ], [B, 0          ], color=main_color, linewidth=1.6 ) # الخط السترين العمودي ليس خط بعد
    ax.plot( [A+C, 0          ], [B, 0          ], color=main_color, linewidth=1.6 ) # الخط المائل
    ax.plot( [A+D, A+D        ], [B, 0          ], color=main_color, linewidth=1.6 ) # خط البعد الطويل
    ax.plot( [A+E, A+E        ], [B, (A*B)/(A+C)], color=main_color, linewidth=1.6 ) # خط البعد المتوسط
    ax.plot( [A-0.15 , A-0.15 ], [B, B-F        ], color=main_color, linewidth=1.6 ) # خط البعد القصير

    ax.text(A+0.1,B+0.05,r"$\varepsilon_{c}=0.003$",color=main_color,ha='center',fontsize=10)
    ax.text(A-0.1, B-F  ,r"$\varepsilon_s'$"       ,color=main_color            ,fontsize=10)
    ax.text(0, -0.08    ,r"$\varepsilon_s =0.005$" ,color=main_color            ,fontsize=10)

    ax.text( A+D+0.05 , B/2                  , f"d = {d} mm"     , rotation=90, color=main_color,  fontsize=7, va='center' )
    ax.text( A+E+0.025, (B+(A*B)/(A+C))/2    , f"C = {c} mm"     , rotation=90, color=main_color,  fontsize=7, va='center' )
    ax.text( A-0.21   , (B+(A*B)/(A+C))/2+0.1, f"d' = {ds} mm", rotation=90, color=main_color,  fontsize=7, va='center' )

    ax.set_xlim(0, 0.7)
    ax.set_ylim(0, 0.7)
    ax.set_aspect('equal')
    ax.axis('off')

    fig.patch.set_facecolor('#2b2b2b')
    ax.set_facecolor('#2b2b2b')

    plt.tight_layout(pad=0)
    plt.show()

# =================== Moment_Beam() =====================
def Moment_Beam(Mu , b , h , fc , fy ,nd) :
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
  T_cover = 60
  C_cover = 60
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
    TS(b,side_cover,k1)
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
    TS(b,side_cover,As2)
    AsT = round(As1 + As2,2)
    st.latex(rf"\text{{Tension Steel = }} A_s = {AsT} \:\: \text{{mm}}^2")
    TS(b,side_cover,AsT)
  else :
    st.latex(r"\qquad \rho \text{ \: < \: } \rho_{max,\; singly,\; f_y = 420 \; \text{MPa}} \text{ \: ➔ \: OK}")
    st.latex(r"\text{Our assumption is correct that it is singly reinforced, so we do not need compression steel}")
    st.latex(r"\text{➔ Let’s calculate the area of steel } A_s \text{ using the following equation}")
    As0 = round (p * b * d_T,2)
    st.latex(rf"\qquad A_s = \rho\, b\, d \text{{ \: = \: }} {As0}\:\:\: \text{{mm}}^2")
    TS(b,side_cover,As0)


Moment_Beam(1100,350,700,30,420,7)
#Moment_Beam(Mu , b , h , fc , fy, nd)
