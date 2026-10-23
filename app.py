import base64, hashlib, io, json, re, time
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent
LOGO = next((f for f in BASE.iterdir() if f.name.lower() == "logo.png"), None)
LOGO_PATH = str(LOGO) if LOGO else None
WA = "https://wa.me/962787355555"
PT = "https://webportals.ju.edu.jo/housing/"

WELCOME = "أهلًا فيك! أنا مساعد صندوق إسكان العاملين في الجامعة الأردنية. اسألني بصوتك أو اكتب سؤالك عن الاشتراك، القروض، الدفعات، التأجيل، فك الرهن أو السداد المبكر."
NO_ANSWER = "ما لقيت هاي المعلومة في دليل الصندوق. بتقدر تتواصل مع إدارة الصندوق مباشرة أو تراجع بوابة الصندوق الإلكترونية."
QUICK = ["كيف اشترك بالصندوق؟", "كم أقصى قيمة للقرض؟", "شو نسبة الاقتطاع الشهري؟",
         "كيف بنصرف دفعات البناء؟", "بقدر أأجل الأقساط؟", "كيف بفك الرهن؟"]

st.set_page_config(page_title="مساعد صندوق إسكان العاملين", page_icon=LOGO_PATH or "🏠", layout="centered",
                   initial_sidebar_state="collapsed")


@st.cache_data
def logo_b64():
    return base64.b64encode(LOGO.read_bytes()).decode() if LOGO else ""


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;700&display=swap');
:root{--navy:#0B2A5C;--navy-d:#071A3D;--gold:#C9A24A;--bg:#F5F7FB;--card:#FFFFFF;--txt:#0F172A;--mut:#475569;--bd:#E2E8F0}
html,body,.stApp,[data-testid="stAppViewContainer"]{direction:rtl;font-family:'Noto Sans Arabic','Segoe UI',Tahoma,sans-serif!important;background:var(--bg)}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],#MainMenu,footer,.stDeployButton,[data-testid="stAppDeployButton"]{display:none!important;visibility:hidden!important;height:0!important}
.block-container{max-width:780px;padding:1.2rem 1rem 7rem!important}
.hero{text-align:center;padding:.5rem 0 1rem}
.hero img{width:92px;height:auto;filter:drop-shadow(0 6px 14px rgba(11,42,92,.25))}
.hero h1{font-size:1.55rem;font-weight:700;color:var(--navy);margin:.6rem 0 .2rem;padding:0}
.hero p{color:var(--mut);font-size:.95rem;margin:0}
.hero .rule{width:56px;height:3px;background:var(--gold);border-radius:3px;margin:.7rem auto 0}
[data-testid="stChatMessage"]{direction:rtl;background:transparent;padding:.35rem 0;gap:.7rem;align-items:flex-start}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] li{font-size:1.02rem;line-height:1.95;color:var(--txt)}
[data-testid="stChatMessage"] em{color:var(--mut);font-size:.85rem}
[data-testid="stChatMessageAvatarUser"]{display:none}
[data-testid="stChatMessageAvatarAssistant"],[data-testid="stChatMessage"] img{border-radius:0;background:transparent;width:2.1rem;height:auto}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){justify-content:flex-start}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"]{background:var(--navy);border-radius:18px 18px 4px 18px;padding:.45rem 1.1rem;width:fit-content;max-width:85%}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p{color:#fff}
.typing span{display:inline-block;width:8px;height:8px;margin:8px 3px;border-radius:50%;background:var(--navy);animation:tb 1.1s infinite ease-in-out}
.typing span:nth-child(2){animation-delay:.18s}.typing span:nth-child(3){animation-delay:.36s}
@keyframes tb{0%,80%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-4px)}}
@media (prefers-reduced-motion:reduce){.typing span{animation:none;opacity:.6}}
div.stButton>button{border:1px solid var(--bd);background:var(--card);color:var(--navy);border-radius:999px;font-family:inherit;font-weight:500;min-height:44px;transition:all .2s ease;cursor:pointer}
div.stButton>button:hover{border-color:var(--gold);background:#FFF9E8;color:var(--navy-d)}
div.stButton>button:focus-visible,a:focus-visible{outline:3px solid var(--gold)!important;outline-offset:2px}
[data-testid="stBaseLinkButton-secondary"],a[data-testid^="stBaseLinkButton"]{border-radius:999px!important;border:1px solid var(--navy)!important;color:var(--navy)!important;font-family:inherit;min-height:44px}
[data-testid="stChatInput"]{direction:rtl;border-radius:999px;border:1px solid var(--bd);background:var(--card);box-shadow:0 4px 18px rgba(11,42,92,.10)}
[data-testid="stChatInput"] textarea{font-family:inherit;font-size:1rem}
[data-testid="stAudioInput"]{direction:ltr;border-radius:18px}
.voice-h{display:flex;align-items:center;gap:.5rem;color:var(--navy);font-weight:700;font-size:.95rem;margin:1.2rem 0 .3rem}
.voice-h svg{width:20px;height:20px}
.foot{display:flex;gap:.6rem;justify-content:center;flex-wrap:wrap;margin-top:1rem}
</style>""", unsafe_allow_html=True)


def norm(s):
    s = re.sub(r"[\u064B-\u065F\u0640]", "", s)
    s = re.sub("[أإآ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    return s.lower()


@st.cache_data
def load_kb():
    kb = json.loads((BASE / "kb.json").read_text(encoding="utf-8"))
    for e in kb:
        e["n"] = [norm(k) for k in e["k"]]
    return kb


def to_md(h):
    links = [n for n, u in (("wa", WA), ("pt", PT)) if u in h]
    h = re.sub(r'<div class="btns">.*?</div>', "", h, flags=re.S)
    h = re.sub(r"<small>(.*?)</small>", r"\n\n*\1*", h, flags=re.S)
    h = re.sub(r"<b>(.*?)</b>", r"**\1**", h, flags=re.S)
    h = re.sub(r"<li>(.*?)</li>", r"\n- \1", h, flags=re.S)
    h = re.sub(r"</?ul>", "\n", h)
    return re.sub(r"<[^>]+>", "", h).strip(), links


def answer(q):
    t, best, score = norm(q), None, 0
    for e in load_kb():
        s = sum(len(k) for k in e["n"] if k in t)
        if s > score:
            best, score = e, s
    if best and score >= 4:
        return to_md(best["a"])
    return NO_ANSWER, ["wa", "pt"]


def stream(text):
    for tok in re.findall(r"\s+|\S+", text):
        yield tok
        if tok.strip():
            time.sleep(0.04)


def link_buttons(links):
    cols = st.columns(len(links) + 1)
    if "wa" in links:
        cols[0].link_button("واتساب الإدارة 0787355555", WA, icon=":material/chat:")
    if "pt" in links:
        cols[len(links) - 1].link_button("بوابة الصندوق", PT, icon=":material/open_in_new:")


def transcribe(wav):
    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav)) as src:
        audio = r.record(src)
    return r.recognize_google(audio, language="ar-JO")


ss = st.session_state
ss.setdefault("msgs", [("assistant", WELCOME, [])])
ss.setdefault("pending", None)
ss.setdefault("akey", 0)
ss.setdefault("last_audio", None)

img = f'<img src="data:image/png;base64,{logo_b64()}" alt="شعار صندوق إسكان العاملين">' if LOGO else ""
st.markdown(f'<div class="hero">{img}<h1>مساعد صندوق إسكان العاملين</h1>'
            '<p>الجامعة الأردنية</p><div class="rule"></div></div>', unsafe_allow_html=True)

if len(ss.msgs) <= 1 and not ss.pending:
    cols = st.columns(2)
    for i, q in enumerate(QUICK):
        if cols[i % 2].button(q, key=f"q{i}", use_container_width=True):
            ss.pending = q
            st.rerun()

for role, text, links in ss.msgs:
    with st.chat_message(role, avatar=LOGO_PATH if role == "assistant" else None):
        st.markdown(text)
        if links:
            link_buttons(links)

if ss.pending:
    q, ss.pending = ss.pending, None
    with st.chat_message("user"):
        st.markdown(q)
    text, links = answer(q)
    with st.chat_message("assistant", avatar=LOGO_PATH):
        box = st.empty()
        box.markdown('<div class="typing"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
        time.sleep(0.7)
        box.write_stream(stream(text))
        if links:
            link_buttons(links)
    ss.msgs += [("user", q, []), ("assistant", text, links)]

st.markdown('<div class="voice-h"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2" width="6" height="12" rx="3"/>'
            '<path d="M5 11a7 7 0 0 0 14 0M12 18v4"/></svg>اسأل بصوتك</div>', unsafe_allow_html=True)
audio = st.audio_input("اضغط على الميكروفون وتحدث، ثم اضغط إيقاف ليصلني سؤالك", key=f"mic{ss.akey}")
if audio is not None:
    data = audio.getvalue()
    h = hashlib.md5(data).hexdigest()
    if h != ss.last_audio:
        ss.last_audio = h
        try:
            with st.spinner("عم بسمعك…"):
                ss.pending = transcribe(data)
            ss.akey += 1
            st.rerun()
        except Exception as ex:
            if type(ex).__name__ == "RerunException":
                raise
            st.warning("ما قدرت أفهم الصوت، جرّب مرة ثانية أو اكتب سؤالك.")

if prompt := st.chat_input("اكتب سؤالك هنا…"):
    ss.pending = prompt
    st.rerun()

st.markdown(f'<div class="foot"></div>', unsafe_allow_html=True)
link_buttons(["wa", "pt"])
