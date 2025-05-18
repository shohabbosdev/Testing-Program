import streamlit as st
from tool import *

st.set_page_config("Testlash tizimi | TestingUI", "❇️", "wide",'expanded')
# Yordamchi funksiyalar
def initialize_session_state():
    """Sessiya holatini boshlash va standart qiymatlarni o‘rnatish."""
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
        'menu': "Fayl yuklash",
        'xato_savollar': []  # Xato berilgan savollar ro‘yxati
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #3b3951, #3b3950);
    }
    .stButton>button {
        background-color: #0288d1;
        color: white;
        border-radius: 5px;
        padding: 10px;
        width: 100%;
        font-size: 16px;
    }
    .stRadio>label {
        font-size: 16px;
        margin-top: 10px;
        color: #01579b;
    }
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 5px;
    padding: 10px;
    width: 100%;
    font-size: 16px;
}
.stRadio>label {
    font-size: 16px;
    margin-top: 10px;
}
.stNumberInput>label, .stSelectbox>label, .stFileUploader>label {
    font-weight: bold;
}
.stWarning {
    background-color: #FFF3CD;
    padding: 10px;
    border-radius: 5px;
}
.time-up-modal {
    background-color: #FFDDC1;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
}
@media (max-width: 600px) {
    .stButton>button {
        font-size: 14px;
        padding: 8px;
    }
    .stRadio>label {
        font-size: 14px;
    }
    .time-up-modal {
        font-size: 16px;
        padding: 15px;
    }
    .stMarkdown h3, .stMarkdown h5 {
        font-size: 18px !important;
    }
}
.custom-warning {
    background-color: #FFECB3;
    padding: 15px;
    border-radius: 8px;
    border-left: 5px solid #FFA000;
    font-size: 16px;
    color: #B71C1C;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# ⌛️ :red[Test tahlil tizimi]")
initialize_session_state()

menu = st.sidebar.selectbox("Menyuni tanlang", ["Fayl yuklash", "Test ishlash", "Natijalar"], 
                            index=["Fayl yuklash", "Test ishlash", "Natijalar"].index(st.session_state.menu))
st.session_state.menu = menu

st.sidebar.divider()
st.sidebar.link_button("Muallif haqida ma‘lumot", "https://t.me/shohabbosdev", icon="🧑‍💻", use_container_width=True)

if menu == "Fayl yuklash":
    fayl_yuklash()
elif menu == "Test ishlash":
    test_ishlash()
elif menu == "Natijalar":
    tahlil_ko_rsatis()