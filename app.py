import hashlib, io, json, re
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent
WA = "https://wa.me/962787355555"
PT = "https://webportals.ju.edu.jo/housing/"
FALLBACK = (
    "ما لقيت هاي المعلومة في دليل الصندوق، فبنصحك تتواصل مع الإدارة مباشرة أو تراجع البوابة الإلكترونية:"
    f'<div class="btns"><a class="btn wa" target="_blank" href="{WA}">واتساب الإدارة 0787355555</a>'
    f'<a class="btn pt" target="_blank" href="{PT}">بوابة الصندوق</a></div>'
)
WELCOME = "أهلًا فيك! أنا المساعد الصوتي لصندوق إسكان العاملين في الجامعة الأردنية. اضغط على الميكروفون وتحدث، أو اكتب سؤالك."
QUICK = ["كيف اشترك بالصندوق؟", "كم أقصى قيمة للقرض؟", "شو نسبة الاقتطاع الشهري؟",
         "كيف بنصرف دفعات البناء؟", "بقدر أأجل الأقساط؟", "كيف بفك الرهن؟"]

st.set_page_config(page_title="المساعد الصوتي – صندوق إسكان العاملين", page_icon=str(BASE / "logo.png"), layout="centered")

st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"]{direction:rtl}
[data-testid="stChatMessage"]{direction:rtl;text-align:right}
.block-container{padding-top:1.5rem;max-width:820px}
h1{color:#f3d98a!important;text-align:center}
.sub{text-align:center;color:#a9b8d8;margin-bottom:.5rem}
small{display:block;color:#f3d98a;margin-top:4px;font-size:.8rem}
.btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.btn{padding:7px 14px;border-radius:999px;text-decoration:none!important;font-weight:700;font-size:.9rem}
.wa{background:#25d366;color:#05260f!important}.pt{background:#e0b84f;color:#1b1503!important}
div.stButton>button{border:1px solid #c9a24a88;color:#f3d98a;border-radius:999px;background:transparent}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load_kb():
    def norm(s):
        s = re.sub(r"[\u064B-\u065F\u0640]", "", s)
        s = re.sub("[أإآ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
        return s.lower()
    kb = json.loads((BASE / "kb.json").read_text(encoding="utf-8"))
    for e in kb:
        e["n"] = [norm(k) for k in e["k"]]
    return kb


def norm(s):
    s = re.sub(r"[\u064B-\u065F\u0640]", "", s)
    s = re.sub("[أإآ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    return s.lower()


def answer(text):
    t, best, score = norm(text), None, 0
    for e in load_kb():
        s = sum(len(k) for k in e["n"] if k in t)
        if s > score:
            best, score = e, s
    return best["a"] if best and score >= 4 else FALLBACK


def plain(html):
    html = re.sub(r"<small>.*?</small>", "", html, flags=re.S)
    html = re.sub(r"<div class=\"btns\">.*?</div>", "", html, flags=re.S)
    html = html.replace("</li>", ". ")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def transcribe(wav_bytes):
    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav_bytes)) as src:
        audio = r.record(src)
    return r.recognize_google(audio, language="ar-JO")


def speak(text):
    from gtts import gTTS
    buf = io.BytesIO()
    gTTS(text=text, lang="ar").write_to_fp(buf)
    return buf.getvalue()


ss = st.session_state
ss.setdefault("msgs", [("assistant", WELCOME)])
ss.setdefault("last_audio", None)
ss.setdefault("speech", None)

c = st.columns([1, 1, 1])[1]
c.image(str(BASE / "logo.png"), use_container_width=True)
st.title("مساعد الصندوق الصوتي")
st.markdown('<div class="sub">اسأل بصوتك أو اكتب سؤالك عن صندوق إسكان العاملين في الجامعة الأردنية</div>', unsafe_allow_html=True)


def handle(q):
    a = answer(q)
    ss.msgs += [("user", q), ("assistant", a)]
    ss.speech = plain(a) if ss.get("speak_on", True) else None


cols = st.columns(3)
for i, q in enumerate(QUICK):
    if cols[i % 3].button(q, key=f"q{i}", use_container_width=True):
        handle(q)

for role, text in ss.msgs:
    with st.chat_message(role, avatar=str(BASE / "logo.png") if role == "assistant" else None):
        st.markdown(text, unsafe_allow_html=True)

if ss.speech:
    try:
        st.audio(speak(ss.speech), format="audio/mp3", autoplay=True)
    except Exception:
        st.caption("تعذّر تشغيل الصوت حاليًا.")
    ss.speech = None

st.toggle("قراءة الإجابة بصوت عالٍ", value=True, key="speak_on")
audio = st.audio_input("🎤 اضغط وتحدث بالعربية ثم أوقف التسجيل")
if audio is not None:
    data = audio.getvalue()
    h = hashlib.md5(data).hexdigest()
    if h != ss.last_audio:
        ss.last_audio = h
        try:
            with st.spinner("عم بسمعك…"):
                handle(transcribe(data))
            st.rerun()
        except Exception:
            st.warning("ما قدرت أفهم الصوت، جرّب مرة ثانية أو اكتب سؤالك.")

if prompt := st.chat_input("اكتب سؤالك هنا…"):
    handle(prompt)
    st.rerun()

st.markdown(
    f'<div class="btns" style="justify-content:center;margin-top:1rem">'
    f'<a class="btn wa" target="_blank" href="{WA}">واتساب الإدارة</a>'
    f'<a class="btn pt" target="_blank" href="{PT}">بوابة الصندوق</a></div>',
    unsafe_allow_html=True)
