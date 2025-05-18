import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import pandas as pd
import time
import random
import plotly.express as px



def export_results_to_pdf(javoblar, to_g_ri_javoblar, xato_ozgarish_savollar, umumiy_ball, umumiy_vaqt, noto_g_ri_mavzular):
    """Natijalarni PDF faylga eksport qilish (logotip bilan)."""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        elements = []

        styles = getSampleStyleSheet()
        logo_style = ParagraphStyle(
            name='Logo',
            fontName='Times-Bold',
            fontSize=16,
            leading=20,
            alignment=1,
            spaceAfter=12
        )
        title_style = ParagraphStyle(
            name='Title',
            fontName='Times-Bold',
            fontSize=14,
            leading=20,
            alignment=1,
            spaceAfter=20,
            textTransform='uppercase'
        )
        normal_style = ParagraphStyle(
            name='Normal',
            fontName='Times-Roman',
            fontSize=14,
            leading=18,
            spaceAfter=10
        )
        table_cell_style = ParagraphStyle(
            name='TableCell',
            fontName='Times-Roman',
            fontSize=14,
            leading=16,
            wordWrap='CJK'
        )
        small_cell_style = ParagraphStyle(
            name='SmallCell',
            fontName='Times-Roman',
            fontSize=12,
            leading=14,
            wordWrap='CJK'
        )

        elements.append(Paragraph("Test Tizimi", logo_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Test natijalari", title_style))
        elements.append(Spacer(1, 12))

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
        savollar_table = Table(savollar_data, colWidths=[110, 100, 100, 50, 100, 100])
        savollar_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Times-Roman', 14),
            ('FONT', (0, 1), (0, -1), 'Times-Roman', 14),
            ('FONT', (1, 1), (1, -1), 'Times-Roman', 12),
            ('FONT', (2, 1), (2, -1), 'Times-Roman', 12),
            ('FONT', (3, 1), (3, -1), 'Times-Roman', 14),
            ('FONT', (4, 1), (4, -1), 'Times-Roman', 12),
            ('FONT', (5, 1), (5, -1), 'Times-Roman', 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(savollar_table)
        elements.append(Spacer(1, 12))

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
        elements.append(Spacer(1, 12))

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
        mavzular_table = Table(mavzular_data, colWidths=[300, 151])
        mavzular_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Times-Roman', 14),
            ('FONT', (0, 1), (0, -1), 'Times-Roman', 14),
            ('FONT', (1, 1), (1, -1), 'Times-Roman', 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(mavzular_table)

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

        savollar_df = pd.DataFrame(javoblar)
        savollar_df.columns = ["Savol", "Tanlangan javob", "To‘g‘ri javob", "Mavzu", "Javob o‘zgarish soni", "Ball kamayishi"]
        output.write("Savollar bo‘limi\n")
        savollar_df.to_csv(output, index=False)
        output.write("\n")

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

        if noto_g_ri_mavzular:
            mavzular_df = pd.DataFrame(list(noto_g_ri_mavzular.items()), columns=["Mavzu", "Noto‘g‘ri javoblar soni"])
        else:
            mavzular_df = pd.DataFrame([["Barcha javoblar to‘g‘ri", 0]], columns=["Mavzu", "Noto‘g‘ri javoblar soni"])
        output.write("Mavzular tahlili\n")
        mavzular_df.to_csv(output, index=False)

        csv_data = output.getvalue().encode('utf-8')
        output.close()
        return csv_data
    except Exception as e:
        st.error(f"Eksport qilishda xato: {str(e)}")
        return None


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

def calculate_results(javoblar):
    """Umumiy natijalarni hisoblash va xato savollarni aniqlash."""
    to_g_ri_javoblar = 0
    xato_ozgarish_savollar = 0
    umumiy_ball = 0
    noto_g_ri_mavzular = {}
    xato_savollar = []

    for idx, javob in enumerate(javoblar):
        if javob['ozgarish_soni'] > 2:
            xato_ozgarish_savollar += 1
            umumiy_ball -= javob['ball_kamayishi']
            xato_savollar.append(idx)  # Xato savol indeksini qo‘shish
        elif javob['tanlangan_javob'] != javob['to\'g\'ri_javob'] and javob['tanlangan_javob'] != "Hech biri":
            xato_savollar.append(idx)  # Noto‘g‘ri javob berilgan savol
        if javob['ozgarish_soni'] > 2 or (javob['tanlangan_javob'] != javob['to\'g\'ri_javob'] and javob['tanlangan_javob'] != "Hech biri"):
            mavzu = javob['mavzu']
            noto_g_ri_mavzular[mavzu] = noto_g_ri_mavzular.get(mavzu, 0) + 1
        if javob['tanlangan_javob'] == javob['to\'g\'ri_javob']:
            to_g_ri_javoblar += 1
            umumiy_ball += 1

    # Xato savollar ro‘yxatini yangilash
    if xato_savollar:
        st.session_state.xato_savollar.extend(xato_savollar)

    return to_g_ri_javoblar, xato_ozgarish_savollar, umumiy_ball, noto_g_ri_mavzular


def fayl_yuklash():
    """CSV faylni yuklash va test sozlamalarini o‘rnatish."""
    st.markdown("### :blue[Test faylini yuklash]")
    st.markdown("**Qo‘llanma**: CSV faylni yuklang (ustunlar: savol, to'g'ri_javob, noto'g'ri_javob_1, noto'g'ri_javob_2, noto'g'ri_javob_3, mavzu, taxminiy_vaqt). Testlar sonini va vaqtni tanlang.")
    
    with st.form("fayl_yuklash_formasi"):
        uploaded_file = st.file_uploader("CSV faylni yuklang", type="csv", label_visibility='collapsed')
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
            
            st.session_state.tasodifiy_indekslar = random.sample(range(len(st.session_state.testlar)), st.session_state.test_soni)
            
            for i in st.session_state.tasodifiy_indekslar:
                test = st.session_state.testlar.iloc[i]
                javoblar = [test['to\'g\'ri_javob'], test['noto\'g\'ri_javob_1'], 
                            test['noto\'g\'ri_javob_2'], test['noto\'g\'ri_javob_3'], "Hech biri"]
                random.shuffle(javoblar)
                st.session_state.randomized_options.append(javoblar)
            
            st.session_state.savol_vaqti = time.time()
            st.session_state.menu = "Test ishlash"
            st.rerun()


def test_ishlash():
    """Test savollarini ko‘rsatish va javoblarni yig‘ish."""
    st.header("Test ishlash")
    if st.session_state.testlar is None:
        st.warning("Iltimos, avval CSV faylni yuklang va testni boshlang!")
        return

    if st.session_state.vaqt_turi == "Barcha savollar uchun umumiy vaqt":
        qolgan_umumiy_vaqt = calculate_time_remaining(st.session_state.vaqt_boshlandi, st.session_state.umumiy_vaqt)
        st.write(f"Umumiy qolgan vaqt: {qolgan_umumiy_vaqt} soniya")
        if qolgan_umumiy_vaqt <= 0:
            st.markdown('<div class="time-up-modal">⏰ Umumiy vaqt tugadi! Natijalarga o‘tmoqdasiz.</div>', unsafe_allow_html=True)
            time.sleep(2)
            st.session_state.menu = "Natijalar"
            st.rerun()
            return

    if st.session_state.current_test >= st.session_state.test_soni:
        st.session_state.menu = "Natijalar"
        st.rerun()
        return

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
    
    if st.session_state.current_test == 0 and not st.session_state.ogohlantirish_korsatildi:
        st.warning("Diqqat! Javobni 2 martadan ko‘p o‘zgartirish tavsiya etilmaydi.")
        st.session_state.ogohlantirish_korsatildi = True
    
    vaqt_limit = test.get('taxminiy_vaqt', st.session_state.savol_vaqt_turi)
    qolgan_vaqt = calculate_time_remaining(st.session_state.savol_vaqti, vaqt_limit)
    st.markdown(f"Savol uchun qolgan vaqt: :green[{qolgan_vaqt}] soniya")
    
    if qolgan_vaqt <= 0:
        st.markdown('<div class="time-up-modal">⏰ Savol uchun vaqt tugadi! Keyingi savolga o‘tmoqdasiz.</div>', unsafe_allow_html=True)
        time.sleep(2)
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
    
    if st.session_state.current_test not in st.session_state.javob_ozgarish_soni:
        st.session_state.javob_ozgarish_soni[st.session_state.current_test] = 0
    
    javoblar = st.session_state.randomized_options[st.session_state.current_test]
    default_javob = st.session_state.tanlangan_javoblar.get(st.session_state.current_test, "Hech biri")
    default_index = javoblar.index(default_javob) if default_javob in javoblar else 0
    tanlov = st.radio("Javobni tanlang:", javoblar, index=default_index, key=f"savol_{st.session_state.current_test}")
    
    if st.session_state.tanlangan_javoblar.get(st.session_state.current_test) != tanlov:
        if st.session_state.tanlangan_javoblar.get(st.session_state.current_test) is not None:
            st.session_state.javob_ozgarish_soni[st.session_state.current_test] += 1
        st.session_state.tanlangan_javoblar[st.session_state.current_test] = tanlov
        
        if st.session_state.javob_ozgarish_soni[st.session_state.current_test] > 2:
            st.warning("Javob 3 martadan ko‘p o‘zgartirildi! Har qo‘shimcha o‘zgarish uchun 0.5 ball kamayadi.")
    
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

def tahlil_ko_rsatis():
    """Test natijalarini ko‘rsatish va eksport qilish."""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### :rainbow[Test natijalari]")
        if not st.session_state.javoblar:
            st.warning("Hozircha natijalar yo‘q. Testni yakunlang!")
            return
        
        if st.session_state.vaqt_boshlandi is None:
            st.error("Test vaqti boshlanmagan. Iltimos, testni qaytadan boshlang.")
            return
        
        to_g_ri_javoblar, xato_ozgarish_savollar, umumiy_ball, noto_g_ri_mavzular = calculate_results(st.session_state.javoblar)
        
        st.markdown(f"To‘g‘ri javoblar: ♻️ :blue[{to_g_ri_javoblar}/{len(st.session_state.javoblar)}]")
        st.markdown(f"Muvaffaqiyat foizi: 🔋 :blue[{(to_g_ri_javoblar/len(st.session_state.javoblar))*100:.2f}%]")
        st.markdown(f"Javob 3 martadan ko‘p o‘zgarishga ega savollar: 🔨 :blue[{xato_ozgarish_savollar}] ta")
        st.markdown(f"Umumiy ball: 👜 :blue[{umumiy_ball:.2f}]")
        
        umumiy_vaqt = calculate_time_remaining(st.session_state.vaqt_boshlandi)
        st.markdown(f"Test uchun sarflangan vaqt: ⏰ :blue[{umumiy_vaqt}]")
    
    with col2:
        st.markdown("### :rainbow[Qayta o‘rganish kerak bo‘lgan mavzular]:")
        if noto_g_ri_mavzular:
            for mavzu, son in noto_g_ri_mavzular.items():
                st.markdown(f":green[{mavzu}]: :red[{son}] ta noto‘g‘ri javob")
        else:
            st.markdown(":blue[Barcha javoblar to‘g‘ri! 🎉]")
    
    tab1, tab2 = st.tabs(["Doiraviy diagramma", "Ustunli diagramma"])
    with tab1:
        fig1 = px.pie(
            names=['To‘g‘ri', 'Noto‘g‘ri', 'Ko‘p o‘zgartirilgan'],
            values=[to_g_ri_javoblar, len(st.session_state.javoblar) - to_g_ri_javoblar - xato_ozgarish_savollar, xato_ozgarish_savollar],
            title="Javoblar taqsimoti",
            color_discrete_sequence=['#00FF00', '#FF0000', '#FFFF00']
        )
        st.plotly_chart(fig1)
    with tab2:
        if noto_g_ri_mavzular:
            fig2 = px.bar(
                x=list(noto_g_ri_mavzular.keys()),
                y=list(noto_g_ri_mavzular.values()),
                labels={'x': 'Mavzular', 'y': "Noto‘g‘ri javoblar soni"},
                title="Mavzular bo‘yicha noto‘g‘ri javoblar",
                color=list(noto_g_ri_mavzular.keys()),
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig2)
    
    ustun1, ustun2 = st.columns(2)
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
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Testni yangidan boshlash", use_container_width=True):
            st.session_state.clear()
            st.session_state.menu = "Fayl yuklash"
            st.rerun()
    
    with col2:
        disabled = not bool(noto_g_ri_mavzular)
        if st.button("Xato savollar bo‘yicha testlar", use_container_width=True, disabled=disabled):
            if st.session_state.xato_savollar:
                xato_indekslar = list(set(st.session_state.xato_savollar))
                st.session_state.tasodifiy_indekslar = random.sample(xato_indekslar, min(len(xato_indekslar), st.session_state.test_soni))
                
                st.session_state.current_test = 0
                st.session_state.javoblar = []
                st.session_state.randomized_options = []
                st.session_state.javob_ozgarish_soni = {}
                st.session_state.tanlangan_javoblar = {}
                st.session_state.ogohlantirish_korsatildi = False
                st.session_state.vaqt_boshlandi = time.time()
                
                for i in st.session_state.tasodifiy_indekslar:
                    test = st.session_state.testlar.iloc[i]
                    javoblar = [test['to\'g\'ri_javob'], test['noto\'g\'ri_javob_1'], 
                                test['noto\'g\'ri_javob_2'], test['noto\'g\'ri_javob_3'], "Hech biri"]
                    random.shuffle(javoblar)
                    st.session_state.randomized_options.append(javoblar)
                
                st.session_state.savol_vaqti = time.time()
                st.session_state.test_soni = len(st.session_state.tasodifiy_indekslar)
                st.session_state.menu = "Test ishlash"
                st.rerun()
