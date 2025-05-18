import streamlit as st
import pandas as pd
import random
import time
import plotly.express as px
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Yordamchi funksiyalar
def initialize_session_state():
    """Sessiya holatini boshlash."""
    defaults = {
        'testlar': None,
        'current_test': 0,
        'javoblar': [],
        'vaqt_boshlandi': None,
        'randomized_options': [],
        'test_soni': 0,
        'savol_vaqti': None,
        'umumiy_vaqt': 0,
        'tasodifiy_indekslar': [],
        'javob_ozgarish_soni': {},
        'vaqt_turi': "Barcha savollar uchun umumiy vaqt",
        'savol_vaqt_turi': 30,
        'ogohlantirish_korsatildi': False,
        'tanlangan_javoblar': {},
        'menu': "Fayl yuklash"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def calculate_time_remaining(start_time, limit=None):
    """Vaqtni hisoblash: limit bo‘lsa qolgan vaqt, bo‘lmasa o‘tgan vaqt."""
    elapsed = time.time() - start_time
    if limit is None:
        minutes, seconds = divmod(int(elapsed), 60)
        return f"{minutes:02d}:{seconds:02d}"
    remaining = max(0, limit - elapsed)
    return int(remaining)

def validate_csv(df):
    """CSV faylni validatsiya qilish."""
    required_columns = ['savol', 'to\'g\'ri_javob', 'noto\'g\'ri_javob_1', 'noto\'g\'ri_javob_2', 'noto\'g\'ri_javob_3', 'mavzu']
    if not all(col in df.columns for col in required_columns):
        return False, f"CSV faylda quyidagi ustunlar bo‘lishi kerak: {', '.join(required_columns)}"
    if df.empty:
        return False, "CSV fayl bo‘sh!"
    if 'taxminiy_vaqt' in df.columns and not df['taxminiy_vaqt'].apply(lambda x: isinstance(x, (int, float)) and x > 0).all():
        return False, "‘taxminiy_vaqt’ ustunida faqat musbat sonlar bo‘lishi kerak!"
    return True, ""

def export_results_to_pdf(javoblar, to_g_ri_javoblar, xato_ozgarish_savollar, umumiy_ball, umumiy_vaqt, noto_g_ri_mavzular):
    """Natijalarni PDF faylga eksport qilish (reportlab yordamida)."""
    try:
        # PDF faylni xotirada yaratish
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        elements = []

        # Shrifts va uslublar
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name='Title',
            fontName='Times-Bold',
            fontSize=12,
            leading=20,
            alignment=1,  # Markazga tekislash
            spaceAfter=20,
            textTransform='uppercase'  # Bosh harflarga o‘zgartirish
        )
        normal_style = ParagraphStyle(
            name='Normal',
            fontName='Times-Roman',
            fontSize=12,
            leading=18,
            spaceAfter=10
        )
        table_cell_style = ParagraphStyle(
            name='TableCell',
            fontName='Times-Roman',
            fontSize=12,
            leading=16,
            wordWrap='CJK'  # Matnni avtomatik sindirish
        )
        small_cell_style = ParagraphStyle(
            name='SmallCell',
            fontName='Times-Roman',
            fontSize=12,  # Kamaytirilgan shrift o‘lchami
            leading=14,
            wordWrap='CJK'  # Matnni avtomatik sindirish
        )

        # Sarlavha
        elements.append(Paragraph("Test natijalari", title_style))
        elements.append(Spacer(1, 5))

        # 1. Savollar bo‘yicha ma’lumotlar (jadval)
        elements.append(Paragraph("Savollar bo‘yicha ma’lumotlar", normal_style))
        savollar_data = [["Savol", "Tanlangan javob", "To‘g‘ri javob", "Mavzu", "O‘zgarish soni", "Ball kamayishi"]]
        for javob in javoblar:
            savollar_data.append([
                Paragraph(str(javob['savol'])[:100], table_cell_style) if javob['savol'] else "",
                Paragraph(str(javob['tanlangan_javob'])[:50], small_cell_style) if javob['tanlangan_javob'] else "",
                Paragraph(str(javob['to\'g\'ri_javob'])[:50], small_cell_style) if javob['to\'g\'ri_javob'] else "",
                Paragraph(str(javob['mavzu'])[:50], table_cell_style) if javob['mavzu'] else "",
                Paragraph(str(javob['ozgarish_soni']), small_cell_style),
                Paragraph(f"{javob['ball_kamayishi']:.2f}", small_cell_style)
            ])
        savollar_table = Table(savollar_data, colWidths=[110, 100, 80, 50, 100, 100])  # Ustun kengliklari aniq pt da
        savollar_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Times-Roman', 12),  # Sarlavha qatori 14 pt
            ('FONT', (0, 1), (0, -1), 'Times-Roman', 12),  # Savol ustuni 14 pt
            ('FONT', (1, 1), (1, -1), 'Times-Roman', 12),  # Tanlangan javob 12 pt
            ('FONT', (2, 1), (2, -1), 'Times-Roman', 12),  # To‘g‘ri javob 12 pt
            ('FONT', (3, 1), (3, -1), 'Times-Roman', 12),  # Mavzu ustuni 14 pt
            ('FONT', (4, 1), (4, -1), 'Times-Roman', 12),  # O‘zgarish soni 12 pt
            ('FONT', (5, 1), (5, -1), 'Times-Roman', 12),  # Ball kamayishi 12 pt
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(savollar_table)
        elements.append(Spacer(1, 5))

        # 2. Umumiy natijalar (ro‘yxat)
        elements.append(Paragraph("Umumiy natijalar", normal_style))
        umumiy_natijalar = [
            f"To‘g‘ri javoblar: {to_g_ri_javoblar}/{len(javoblar)}",
            f"Muvaffaqiyat foizi: {(to_g_ri_javoblar/len(javoblar))*100:.2f}%",
            f"Javob 3 martadan ko‘p o‘zgartirilgan savollar: {xato_ozgarish_savollar}",
            f"Umumiy ball: {umumiy_ball:.2f}",
            f"Sarflangan vaqt: {umumiy_vaqt}"
        ]
        for item in umumiy_natijalar:
            elements.append(Paragraph(item, normal_style))
        elements.append(Spacer(1, 20))

        # 3. Mavzular tahlili (jadval)
        elements.append(Paragraph("Mavzular tahlili", normal_style))
        mavzular_data = [["Mavzu", "Noto‘g‘ri javoblar soni"]]
        if noto_g_ri_mavzular:
            for mavzu, son in noto_g_ri_mavzular.items():
                mavzular_data.append([
                    Paragraph(str(mavzu)[:100], table_cell_style) if mavzu else "",
                    Paragraph(str(son), small_cell_style)
                ])
        else:
            mavzular_data.append([Paragraph("Barcha javoblar to‘g‘ri", table_cell_style), Paragraph("0", small_cell_style)])
        mavzular_table = Table(mavzular_data, colWidths=[300, 151])  # Ustun kengliklari aniq pt da
        mavzular_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Times-Roman', 12),  # Sarlavha qatori 14 pt
            ('FONT', (0, 1), (0, -1), 'Times-Roman', 12),  # Mavzu ustuni 14 pt
            ('FONT', (1, 1), (1, -1), 'Times-Roman', 12),  # Noto‘g‘ri javoblar soni 12 pt
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(mavzular_table)

        # PDF ni yaratish
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
    except Exception as e:
        st.error(f"PDF eksport qilishda xato: {str(e)}")
        return None
def export_results_to_csv(javoblar, to_g_ri_javoblar, xato_ozgarish_savollar, umumiy_ball, umumiy_vaqt, noto_g_ri_mavzular):
    """Natijalarni CSV faylga eksport qilish."""
    try:
        output = StringIO()

        # 1. Savol bo‘yicha ma’lumotlar
        savollar_df = pd.DataFrame(javoblar)
        savollar_df.columns = ["Savol", "Tanlangan javob", "To‘g‘ri javob", "Mavzu", "Javob o‘zgarish soni", "Ball kamayishi"]
        output.write("Savollar bo‘limi\n")
        savollar_df.to_csv(output, index=False)
        output.write("\n")

        # 2. Umumiy natijalar
        umumiy_natijalar = pd.DataFrame({
            "Parametr": [
                "To‘g‘ri javoblar",
                "Muvaffaqiyat foizi",
                "Javob 3 martadan ko‘p o‘zgartirilgan savollar",
                "Umumiy ball",
                "Sarflangan vaqt"
            ],
            "Qiymat": [
                f"{to_g_ri_javoblar}/{len(javoblar)}",
                f"{(to_g_ri_javoblar/len(javoblar))*100:.2f}%",
                xato_ozgarish_savollar,
                f"{umumiy_ball:.2f}",
                umumiy_vaqt
            ]
        })
        output.write("Umumiy natijalar\n")
        umumiy_natijalar.to_csv(output, index=False)
        output.write("\n")

        # 3. Mavzular tahlili
        if noto_g_ri_mavzular:
            mavzular_df = pd.DataFrame(list(noto_g_ri_mavzular.items()), columns=["Mavzu", "Noto‘g‘ri javoblar soni"])
        else:
            mavzular_df = pd.DataFrame([["Barcha javoblar to‘g‘ri", 0]], columns=["Mavzu", "Noto‘g‘ri javoblar soni"])
        output.write("Mavzular tahlili\n")
        mavzular_df.to_csv(output, index=False)

        # CSV ma’lumotlarini bayt sifatida qaytarish
        csv_data = output.getvalue().encode('utf-8')
        output.close()
        return csv_data
    except Exception as e:
        st.error(f"Eksport qilishda xato: {str(e)}")
        return None

# Interfeys uslublari
st.markdown("""
    <style>
    .stButton>button {background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px;}
    .stRadio>label {font-size: 16px; margin-top: 10px;}
    .stNumberInput>label {font-weight: bold;}
    .stSelectbox>label {font-weight: bold;}
    .stFileUploader>label {font-weight: bold;}
    .stWarning {background-color: #FFF3CD; padding: 10px; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# Birinchi oyna: CSV faylni yuklash
def fayl_yuklash():
    st.markdown("### :blue[Test faylini yuklash]")
    st.markdown("**Qo‘llanma**: CSV faylni yuklang (ustunlar: savol, to'g'ri_javob, noto'g'ri_javob_1, noto'g'ri_javob_2, noto'g'ri_javob_3, mavzu, taxminiy_vaqt). Testlar sonini va vaqtni tanlang.")
    
    with st.form("fayl_yuklash_formasi"):
        uploaded_file = st.file_uploader("CSV faylni yuklang", type="csv")
        submitted = st.form_submit_button("Faylni tekshirish")
        
        if submitted and uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, usecols=['savol', 'to\'g\'ri_javob', 'noto\'g\'ri_javob_1', 'noto\'g\'ri_javob_2', 'noto\'g\'ri_javob_3', 'mavzu', 'taxminiy_vaqt'])
                is_valid, error_message = validate_csv(df)
                if not is_valid:
                    st.error(error_message)
                    return
                
                st.session_state.testlar = df
                st.write("Yuklangan testlar soni:", len(df))
                st.write("Mavzular:", df['mavzu'].unique())
            except Exception as e:
                st.error(f"Faylni o‘qishda xato: {str(e)}")
                return

    # Sidebar: Test sozlamalari
    st.sidebar.subheader("Test sozlamalari")
    if st.session_state.testlar is not None:
        max_testlar = len(st.session_state.testlar)
        st.session_state.test_soni = st.sidebar.number_input(
            "Testlar sonini tanlang", min_value=1, max_value=max_testlar, value=max_testlar
        )
        
        st.session_state.vaqt_turi = st.sidebar.radio("Vaqt turini tanlang:", ["Barcha savollar uchun umumiy vaqt", "Har bir savol uchun vaqt"])
        if st.session_state.vaqt_turi == "Barcha savollar uchun umumiy vaqt":
            st.session_state.umumiy_vaqt = st.sidebar.number_input(
                "Umumiy vaqt (daqiqa)", min_value=1, value=10
            ) * 60
        else:
            st.session_state.savol_vaqt_turi = st.sidebar.number_input(
                "Har bir savol uchun vaqt (soniya)", min_value=10, value=30
            )
        
        if st.sidebar.button("Testni boshlash", use_container_width=True):
            st.session_state.vaqt_boshlandi = time.time()
            st.session_state.current_test = 0
            st.session_state.javoblar = []
            st.session_state.randomized_options = []
            st.session_state.javob_ozgarish_soni = {}
            st.session_state.tanlangan_javoblar = {}
            st.session_state.ogohlantirish_korsatildi = False
            
            # Tasodifiy indekslar
            st.session_state.tasodifiy_indekslar = random.sample(range(len(st.session_state.testlar)), st.session_state.test_soni)
            
            # Javob variantlarini tasodifiy tartibda saqlash
            for i in st.session_state.tasodifiy_indekslar:
                test = st.session_state.testlar.iloc[i]
                javoblar = [test['to\'g\'ri_javob'], test['noto\'g\'ri_javob_1'], 
                            test['noto\'g\'ri_javob_2'], test['noto\'g\'ri_javob_3']]
                random.shuffle(javoblar)
                st.session_state.randomized_options.append(javoblar)
            
            st.session_state.savol_vaqti = time.time()
            st.session_state.menu = "Test ishlash"
            st.rerun()

# Ikkinchi oyna: Test ishlash
def test_ishlash():
    st.header("Test ishlash")
    if st.session_state.testlar is None:
        st.warning("Iltimos, avval CSV faylni yuklang va testni boshlang!")
        return

    # Umumiy vaqtni tekshirish
    if st.session_state.vaqt_turi == "Barcha savollar uchun umumiy vaqt":
        qolgan_umumiy_vaqt = calculate_time_remaining(st.session_state.vaqt_boshlandi, st.session_state.umumiy_vaqt)
        st.write(f"Umumiy qolgan vaqt: {qolgan_umumiy_vaqt} soniya")
        if qolgan_umumiy_vaqt <= 0:
            st.warning("Umumiy vaqt tugadi! Natijalarga o‘tmoqdasiz.")
            st.session_state.menu = "Natijalar"
            st.rerun()
            return

    # Test yakunlanganligini tekshirish
    if st.session_state.current_test >= st.session_state.test_soni:
        st.session_state.menu = "Natijalar"
        st.rerun()
        return

    # Savol tanlash
    savol_tanlash = st.sidebar.selectbox("Savolni tanlang...", [f"Savol {i+1}" for i in range(st.session_state.test_soni)], 
                                 index=st.session_state.current_test)
    new_index = int(savol_tanlash.split()[-1]) - 1
    if new_index != st.session_state.current_test:
        st.session_state.current_test = new_index
        st.session_state.savol_vaqti = time.time()
        st.rerun()
    
    test_index = st.session_state.tasodifiy_indekslar[st.session_state.current_test]
    test = st.session_state.testlar.iloc[test_index]
    st.markdown(f"### :rainbow[Savol {st.session_state.current_test + 1}/{st.session_state.test_soni}]")
    st.markdown(f"##### :blue[{test['savol']}]")
    
    # Ogohlantirish xabari
    if st.session_state.current_test == 0 and not st.session_state.ogohlantirish_korsatildi:
        st.warning("Diqqat! Javobni 2 martadan ko‘p o‘zgartirish tavsiya etilmaydi.")
        st.session_state.ogohlantirish_korsatildi = True
    
    # Vaqtni ko‘rsatish
    vaqt_limit = test.get('taxminiy_vaqt', st.session_state.savol_vaqt_turi)
    qolgan_vaqt = calculate_time_remaining(st.session_state.savol_vaqti, vaqt_limit)
    st.markdown(f"Savol uchun qolgan vaqt: :green[{qolgan_vaqt}] soniya")
    
    if qolgan_vaqt <= 0:
        st.warning("Savol uchun vaqt tugadi! Keyingi savolga o‘tmoqdasiz.")
        st.session_state.javoblar.append({
            'savol': test['savol'],
            'tanlangan_javob': None,
            'to\'g\'ri_javob': test['to\'g\'ri_javob'],
            'mavzu': test['mavzu'],
            'ozgarish_soni': st.session_state.javob_ozgarish_soni.get(st.session_state.current_test, 0),
            'ball_kamayishi': 0
        })
        st.session_state.current_test += 1
        st.session_state.savol_vaqti = time.time()
        st.rerun()
        return
    
    # Javob o‘zgarishlarini kuzatish
    if st.session_state.current_test not in st.session_state.javob_ozgarish_soni:
        st.session_state.javob_ozgarish_soni[st.session_state.current_test] = 0
    
    # Javob variantlari
    javoblar = st.session_state.randomized_options[st.session_state.current_test]
    default_javob = st.session_state.tanlangan_javoblar.get(st.session_state.current_test, None)
    default_index = javoblar.index(default_javob) if default_javob in javoblar else 0
    tanlov = st.radio("Javobni tanlang:", javoblar, index=default_index, key=f"savol_{st.session_state.current_test}")
    
    # Javob o‘zgarishlarini hisoblash
    if st.session_state.tanlangan_javoblar.get(st.session_state.current_test) != tanlov:
        if st.session_state.tanlangan_javoblar.get(st.session_state.current_test) is not None:
            st.session_state.javob_ozgarish_soni[st.session_state.current_test] += 1
        st.session_state.tanlangan_javoblar[st.session_state.current_test] = tanlov
        
        if st.session_state.javob_ozgarish_soni[st.session_state.current_test] > 2:
            st.warning("Javob 3 martadan ko‘p o‘zgartirildi! Har qo‘shimcha o‘zgarish uchun 0.5 ball kamayadi.")
    
    # Tugmalar
    col1, col2 = st.columns(2)
    with col1:
        button_label = "Testni tugatish" if st.session_state.current_test == st.session_state.test_soni - 1 else "Keyingi savol"
        if st.button(button_label, key="next_button", use_container_width=True):
            ball_kamayishi = (st.session_state.javob_ozgarish_soni[st.session_state.current_test] - 2) * 0.5 if st.session_state.javob_ozgarish_soni[st.session_state.current_test] > 2 else 0
            st.session_state.javoblar.append({
                'savol': test['savol'],
                'tanlangan_javob': tanlov,
                'to\'g\'ri_javob': test['to\'g\'ri_javob'],
                'mavzu': test['mavzu'],
                'ozgarish_soni': st.session_state.javob_ozgarish_soni.get(st.session_state.current_test, 0),
                'ball_kamayishi': ball_kamayishi
            })
            st.session_state.current_test += 1
            st.session_state.savol_vaqti = time.time()
            st.rerun()

# Tahlil jarayoni

def tahlil_ko_rsatis():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### :rainbow[Test natijalari]")
        if not st.session_state.javoblar:
            st.warning("Hozircha natijalar yo‘q. Testni yakunlang!")
            return
        
        if st.session_state.vaqt_boshlandi is None:
            st.error("Test vaqti boshlanmagan. Iltimos, testni qaytadan boshlang.")
            return
        
        to_g_ri_javoblar = 0
        xato_ozgarish_savollar = 0
        umumiy_ball = 0
        
        for javob in st.session_state.javoblar:
            if javob['ozgarish_soni'] > 2:
                xato_ozgarish_savollar += 1
                umumiy_ball -= javob['ball_kamayishi']
            elif javob['tanlangan_javob'] == javob['to\'g\'ri_javob']:
                to_g_ri_javoblar += 1
                umumiy_ball += 1
        
        st.markdown(f"To‘g‘ri javoblar: ♻️ :blue[{to_g_ri_javoblar}/{len(st.session_state.javoblar)}]")
        st.markdown(f"Muvaffaqiyat foizi: 🔋 :blue[{(to_g_ri_javoblar/len(st.session_state.javoblar))*100:.2f}%]")
        st.markdown(f"Javob 3 martadan ko‘p o‘zgarishga ega savollar: 🔨 :blue[{xato_ozgarish_savollar}] ta")
        st.markdown(f"Umumiy ball: 👜 :blue[{umumiy_ball:.2f}]")
        
        umumiy_vaqt = calculate_time_remaining(st.session_state.vaqt_boshlandi)
        st.markdown(f"Test uchun sarflangan vaqt: ⏰ :blue[{umumiy_vaqt}]")
    
    # Noto‘g‘ri javoblar bo‘yicha mavzular
    with col2:
        noto_g_ri_mavzular = {}
        for javob in st.session_state.javoblar:
            if javob['ozgarish_soni'] > 2 or javob['tanlangan_javob'] != javob['to\'g\'ri_javob']:
                mavzu = javob['mavzu']
                noto_g_ri_mavzular[mavzu] = noto_g_ri_mavzular.get(mavzu, 0) + 1
        
        st.markdown("### :rainbow[Qayta o‘rganish kerak bo‘lgan mavzular]:")
        if noto_g_ri_mavzular:
            for mavzu, son in noto_g_ri_mavzular.items():
                st.markdown(f":green[{mavzu}]: :red[{son}] ta noto‘g‘ri javob")
        else:
            st.markdown(":blue[Barcha javoblar to‘g‘ri! 🎉]")
    
    # Vizualizatsiya
    tab1,tab2 = st.tabs(["Doiraviy diagramma", "Usutnli diagramma"])
    with tab1:
        fig1 = px.pie(names=['To‘g‘ri', 'Noto‘g‘ri', 'Ko‘p o‘zgartirilgan'], 
                    values=[to_g_ri_javoblar, len(st.session_state.javoblar) - to_g_ri_javoblar - xato_ozgarish_savollar, xato_ozgarish_savollar],
                    title="Javoblar taqsimoti")
        st.plotly_chart(fig1)
    with tab2:
        if noto_g_ri_mavzular:
            fig2 = px.bar(x=list(noto_g_ri_mavzular.keys()), y=list(noto_g_ri_mavzular.values()), 
                        labels={'x': 'Mavzular', 'y': "Noto‘g‘ri javoblar soni"}, title="Mavzular bo‘yicha noto‘g‘ri javoblar")
            st.plotly_chart(fig2)
    
    ustun1,ustun2 = st.columns(2)
    # Natijalarni eksport qilish (CSV)
    if st.session_state.javoblar:
        csv_data = export_results_to_csv(
            st.session_state.javoblar,
            to_g_ri_javoblar,
            xato_ozgarish_savollar,
            umumiy_ball,
            umumiy_vaqt,
            noto_g_ri_mavzular
        )
        if csv_data:
            ustun1.success("CSV fayl tayyor! Yuklab olishingiz mumkin.")
            ustun1.download_button(
                label="Natijalarni CSV sifatida eksport qilish",
                data=csv_data,
                file_name="test_natijalari.csv",
                mime="text/csv",
                key="export_csv_button"
            )
    
    # Natijalarni eksport qilish (PDF)
    if st.session_state.javoblar:
        pdf_data = export_results_to_pdf(
            st.session_state.javoblar,
            to_g_ri_javoblar,
            xato_ozgarish_savollar,
            umumiy_ball,
            umumiy_vaqt,
            noto_g_ri_mavzular
        )
        if pdf_data:
            ustun2.success("PDF fayl tayyor! Yuklab olishingiz mumkin.")
            ustun2.download_button(
                label="Natijalarni PDF sifatida eksport qilish",
                data=pdf_data,
                file_name="test_natijalari.pdf",
                mime="application/pdf",
                key="export_pdf_button"
            )
    
    if st.button("Testni yangidan boshlash", use_container_width=True):
        st.session_state.clear()
        st.session_state.menu = "Fayl yuklash"
        st.rerun()

# Asosiy interfeys
st.markdown("# ⌛️ :red[Test tahlil tizimi]")
initialize_session_state()

# Sidebar: Navigatsiya va muallif
st.sidebar.subheader("Navigatsiya")
menu = st.sidebar.selectbox("Menyuni tanlang", ["Fayl yuklash", "Test ishlash", "Natijalar"], 
                            index=["Fayl yuklash", "Test ishlash", "Natijalar"].index(st.session_state.menu))
st.session_state.menu = menu

st.sidebar.divider()
st.sidebar.link_button("Muallif haqida ma‘lumot", "https://t.me/shohabbosdev", icon="🧑‍💻", use_container_width=True)

# Menyuni ko‘rsatish
if menu == "Fayl yuklash":
    fayl_yuklash()
elif menu == "Test ishlash":
    test_ishlash()
elif menu == "Natijalar":
    tahlil_ko_rsatis()