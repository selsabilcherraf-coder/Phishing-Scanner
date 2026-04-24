import streamlit as st
import tldextract
import re
import requests

# --- 1. إعدادات الصفحة والتصميم مع إضافة الخلفية ---
st.set_page_config(page_title="CyberShield Pro", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    /* إضافة خلفية متدرجة للموقع بالكامل */
    .stApp {
        background: linear-gradient(180deg, #f0f4f8 0%, #d9e2ec 100%);
        background-attachment: fixed;
    }
    
    /* تصميم الهيدر (العنوان العلوي) */
    .main-header {
        text-align: center;
        padding: 40px;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        border-bottom: 4px solid #38bdf8;
    }
    
    .main-header h1 { font-size: 2.2em; margin: 0; font-weight: 700; }

    /* تحسين شكل منطقة الكتابة */
    .stTextArea textarea {
        border-radius: 15px;
        border: 2px solid #cbd5e1;
        background-color: rgba(255, 255, 255, 0.9); /* شفافية خفيفة */
    }

    /* تصميم الأزرار */
    .stButton>button {
        border-radius: 12px;
        height: 3.5em;
        background-color: #0f172a;
        color: white;
        border: 1px solid #38bdf8;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #38bdf8;
        color: #0f172a;
        transform: scale(1.02);
    }

    .footer { text-align: center; color: #475569; font-size: 0.9em; margin-top: 60px; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام اللغات والتحكم ---
if 'lang' not in st.session_state: st.session_state.lang = 'ar'

def toggle_lang():
    st.session_state.lang = 'fr' if st.session_state.lang == 'ar' else 'ar'

def reset_callback():
    st.session_state.email_data = "" 
    if 'triggered' in st.session_state:
        st.session_state.triggered = False

texts = {
    'ar': {
        'title': "كاشف الرسائل المشبوهة",
        'input_label': "انسخ نص الرسالة هنا للفحص:",
        'scan_btn': "افحص الرسالة الآن 🔍",
        'clear_btn': "مسح النص 🗑️",
        'lang_btn': "التحويل للفرنسية 🇫🇷",
        'evidence': "📊 لماذا اعتبرناها مشبوهة؟",
        'safe': "✅ الرسالة تبدو آمنة، لا داعي للقلق.",
        'danger': "🚨 احذر! هذه الرسالة محاولة احتيال واضحة.",
        'placeholder': "الصق الرسالة التي وصلتك هنا...",
        'tips_h': "💡 ماذا تفعل الآن؟",
        'tips': ["لا تضغط على أي رابط موجود في الرسالة.", "احذف الرسالة فوراً من بريدك.", "لا تعطي معلوماتك الشخصية لأي أحد."]
    },
    'fr': {
        'title': "Détecteur de Messages Suspects",
        'input_label': "Copiez le message ici pour l'analyser :",
        'scan_btn': "Analyser maintenant 🔍",
        'clear_btn': "Effacer le texte 🗑️",
        'lang_btn': "التحويل للعربية 🇩🇿",
        'evidence': "📊 Pourquoi est-ce suspect ?",
        'safe': "✅ Ce message semble sûr, aucun danger.",
        'danger': "🚨 Attention ! Ce message est une tentative de fraude.",
        'placeholder': "Collez le message reçu ici...",
        'tips_h': "💡 Que faire maintenant ?",
        'tips': ["Ne cliquez sur aucun lien dans le message.", "Supprimez le message immédiatement.", "Ne partagez jamais vos infos personnelles."]
    }
}
L = texts[st.session_state.lang]

# --- 3. محرك الفحص المبسط ---
class Scanner:
    def __init__(self, text):
        self.text = text
        self.score = 0
        self.reasons = []

    def check(self):
        words = ["عاجل", "حسابك", "تحديث", "مغلق", "urgent", "suspension", "bancaire", "sécurisé"]
        for w in words:
            if w in self.text.lower():
                self.score += 20
                self.reasons.append(f"🚩 تم العثور على كلمة مشبوهة: ({w})")

        urls = re.findall(r'https?://\S+', self.text)
        for u in urls:
            ext = tldextract.extract(u)
            domain = f"{ext.domain}.{ext.suffix}"
            if "bna" in u.lower() and domain not in ["bna.dz", "bna.com.dz"]:
                self.score += 100
                self.reasons.append(f"🚨 تنبيه: الرابط يدعي أنه للبنك الوطني الجزائري لكنه موقع مزيف.")

# --- 4. الواجهة ---
st.sidebar.button(L['lang_btn'], on_click=toggle_lang, use_container_width=True)

st.markdown(f'<div class="main-header"><h1>{L["title"]}</h1></div>', unsafe_allow_html=True)

input_data = st.text_area(L['input_label'], key="email_data", height=200, placeholder=L['placeholder'])

col1, col2 = st.columns(2)
with col1:
    if st.button(L['scan_btn'], use_container_width=True):
        st.session_state.triggered = True
with col2:
    st.button(L['clear_btn'], on_click=reset_callback, use_container_width=True)

if st.session_state.get('triggered') and input_data:
    engine = Scanner(input_data)
    engine.check()
    
    st.markdown("<br>", unsafe_allow_html=True)
    if engine.score >= 70:
        st.error(L['danger'])
        with st.expander(L['tips_h'], expanded=True):
            for t in L['tips']: st.write(f"- {t}")
    else:
        st.success(L['safe'])
            
    if engine.reasons:
        with st.expander(L['evidence']):
            for r in engine.reasons: st.write(r)

st.markdown(f'<div class="footer">© 2026 {L["title"]} | حماية بسيطة للجميع</div>', unsafe_allow_html=True)