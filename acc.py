import streamlit as st
import tldextract
import re

# --- 1. التنسيق الجمالي المطور (UI Customization) ---
st.set_page_config(page_title="CyberShield Pro", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    /* تنسيق الخط والخلفية العامة */
    html, body, [class*="css"] { 
        font-family: 'Tajawal', sans-serif; 
        background-color: #f4f7f9; 
    }

    /* تصميم الهيدر العلوي - تقليل المسافات */
    .hero-section {
        text-align: center;
        padding: 20px 10px; /* تقليل الحشو */
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 15px; /* تقليل المسافة السفلية */
        border-bottom: 4px solid #38bdf8;
    }
    .hero-section h1 { margin: 0; font-size: 1.8em; }

    /* تصميم البطاقة المركزية */
    .main-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }

    /* إطار أزرق لمربع النص */
    .stTextArea textarea {
        border: 2px solid #38bdf8 !important; /* إطار أزرق دائم */
        border-radius: 12px !important;
        background-color: #ffffff !important;
        font-size: 1.05em !important;
    }
    
    /* تقليل المسافة بين العنوان والمدخلات */
    .stMarkdown { margin-bottom: -10px; }

    /* مؤشر الخطورة */
    .risk-indicator {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2em;
        margin: 10px 0;
    }
    
    /* تصميم الأزرار */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.2em;
        background: #004aad;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background: #38bdf8; color: #0f172a; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الحالة واللغات ---
if 'lang' not in st.session_state: st.session_state.lang = 'ar'
def toggle_lang(): st.session_state.lang = 'fr' if st.session_state.lang == 'ar' else 'ar'
def reset_callback():
    st.session_state.email_data = ""
    if 'triggered' in st.session_state: st.session_state.triggered = False

texts = {
    'ar': {
        'title': "درع الحماية من الاحتيال",
        'input_label': "ضع نص الرسالة هنا لتحليل مستوى الخطر:",
        'scan_btn': "تحليل الآن 🔍",
        'clear_btn': "مسح 🗑️",
        'lang_btn': "Switch to French 🇫🇷",
        'risk_title': "مستوى خطورة الرسالة:",
        'reasons': "📊 تفاصيل الفحص:",
        'levels': ["آمن (Safe)", "منخفض (Low)", "متوسط (Medium)", "مرتفع (High)", "خطير جداً (Critical)"]
    },
    'fr': {
        'title': "Bouclier Anti-Phishing",
        'input_label': "Collez le message ici pour l'analyse :",
        'scan_btn': "Analyser 🔍",
        'clear_btn': "Effacer 🗑️",
        'lang_btn': "التحويل للعربية 🇩🇿",
        'risk_title': "Niveau de risque :",
        'reasons': "📊 Détails de l'analyse :",
        'levels': ["Sûr (Safe)", "Faible (Low)", "Modéré (Medium)", "Élevé (High)", "Critique (Critical)"]
    }
}
L = texts[st.session_state.lang]

# --- 3. محرك تحليل الخطورة ---
class ThreatAnalyzer:
    def __init__(self, text):
        self.text = text.lower()
        self.score = 0
        self.logs = []

    def run(self):
        keywords = {
            "urgent": 20, "suspension": 25, "bancaire": 15, "sécurisé": 10,
            "عاجل": 20, "حسابك": 15, "تحديث": 15, "مغلق": 20, "البنك": 10
        }
        for word, pts in keywords.items():
            if word in self.text:
                self.score += pts
                self.logs.append(f"🚩 كلمة مشبوهة: ({word})")

        urls = re.findall(r'https?://\S+', self.text)
        for u in urls:
            ext = tldextract.extract(u)
            domain = f"{ext.domain}.{ext.suffix}"
            if "bna" in u and domain not in ["bna.dz", "bna.com.dz"]:
                self.score += 75
                self.logs.append(f"🚨 انتحال رابط رسمي: ({domain})")
        
        return min(self.score, 100)

# --- 4. الواجهة الرسومية ---
st.sidebar.button(L['lang_btn'], on_click=toggle_lang, use_container_width=True)

# العنوان (بدون فراغات زائدة)
st.markdown(f'<div class="hero-section"><h1>{L["title"]}</h1></div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # مربع النص بإطار أزرق
    data = st.text_area(L['input_label'], key="email_data", height=180)
    
    c1, c2 = st.columns([3, 1])
    with c1: 
        if st.button(L['scan_btn']): st.session_state.triggered = True
    with c2: 
        st.button(L['clear_btn'], on_click=reset_callback)
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get('triggered') and data:
    analyzer = ThreatAnalyzer(data)
    score = analyzer.run()
    
    if score < 20: level, color, bg = L['levels'][0], "#155724", "#d4edda"
    elif score < 40: level, color, bg = L['levels'][1], "#856404", "#fff3cd"
    elif score < 60: level, color, bg = L['levels'][2], "#856404", "#ffeeba"
    elif score < 85: level, color, bg = L['levels'][3], "#721c24", "#f8d7da"
    else: level, color, bg = L['levels'][4], "#ffffff", "#721c24"

    st.markdown(f"### {L['risk_title']}")
    st.markdown(f"""<div class="risk-indicator" style="color:{color}; background-color:{bg}; border: 1px solid {color};">
                {level} - {score}% </div>""", unsafe_allow_html=True)
    st.progress(score / 100)

    if analyzer.logs:
        with st.expander(L['reasons'], expanded=True):
            for log in analyzer.logs: st.info(log)
