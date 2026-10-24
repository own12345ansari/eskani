import base64, hashlib, html, io, json, re, time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

BASE = Path(__file__).parent
LOGO = next((f for f in BASE.iterdir() if f.name.lower() == "logo.png"), None)
LOGO_PATH = str(LOGO) if LOGO else None
WA = "https://wa.me/962787355555"
PT = "https://webportals.ju.edu.jo/housing/"

WELCOME = "أهلًا فيك! أنا مساعد صندوق إسكان العاملين في الجامعة الأردنية. اسألني بصوتك أو اكتب سؤالك عن الاشتراك، القروض، الدفعات، التأجيل، فك الرهن أو السداد المبكر."
SAY_NO_AR = "ما لقيت هاي المعلومة بدليل الصندوق. بتقدر تتواصل مع الإدارة على واتساب أو من خلال البوابة."
SAY_NO_EN = "I couldn't find that in the Fund guide. You can contact the management on WhatsApp or through the portal."
AR_VOICES = [("ar-JO-TaimNeural", "طيم"), ("ar-SY-LaithNeural", "ليث"), ("ar-SA-HamedNeural", "حامد"),
             ("ar-EG-ShakirNeural", "شاكر"), ("ar-AE-HamdanNeural", "حمدان"),
             ("en-US-AndrewMultilingualNeural", "أندرو (تجريبي)"), ("en-US-BrianMultilingualNeural", "براين (تجريبي)")]
RATES = [("بطيء", "-14%"), ("هادئ", "-6%"), ("عادي", "+0%")]
PRON = {"الجبيهة": "الجُبَيْهَة", "ياجوز": "يَاجُوز"}  # أضف هنا الكلمات التي تُنطق خطأ: "الكلمة": "الكلمة بالتشكيل"
EN_VOICE = "en-US-AndrewNeural"
NO_ANSWER_EN = "I couldn't find that in the Fund guide. You can contact the Fund management directly or check the Fund portal."
AR = re.compile(r"[\u0600-\u06FF]")
NO_ANSWER = "ما لقيت هاي المعلومة في دليل الصندوق. بتقدر تتواصل مع إدارة الصندوق مباشرة أو تراجع بوابة الصندوق الإلكترونية."
QUICK = ["كيف اشترك بالصندوق؟", "كم أقصى قيمة للقرض؟", "شو نسبة الاقتطاع الشهري؟",
         "كيف بنصرف دفعات البناء؟", "بقدر أأجل الأقساط؟", "كيف بفك الرهن؟"]

MIC_JS = r'''<script>
(function(){
 var win=window.parent, doc=win.document;
 if(win.__hfMicInit){return;} win.__hfMicInit=true;
 var SR=win.SpeechRecognition||win.webkitSpeechRecognition;
 var css=doc.createElement('style');
 css.textContent=`
 .hf-wrap{display:inline-flex;align-items:center;gap:6px;margin-inline:6px;direction:ltr}
 .hf-mic{width:38px;height:38px;border-radius:50%;border:0;background:#0B2A5C;color:#fff;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;transition:transform .15s ease,background .2s ease;padding:0}
 .hf-mic:hover{transform:scale(1.06)} .hf-mic:focus-visible,.hf-lang:focus-visible{outline:3px solid #C9A24A;outline-offset:2px}
 .hf-mic svg{width:20px;height:20px}
 .hf-mic.rec{background:#C9A24A;color:#0B2A5C;animation:hfp 1.1s infinite}
 @keyframes hfp{50%{box-shadow:0 0 0 9px rgba(201,162,74,.28)}}
 @media (prefers-reduced-motion:reduce){.hf-mic.rec{animation:none}}
 .hf-lang{border:1px solid #C9A24A;background:#fff;color:#0B2A5C;border-radius:999px;font:700 .72rem sans-serif;padding:5px 9px;cursor:pointer;min-height:30px}
 .hf-corner{position:fixed;left:50%;transform:translateX(-50%);bottom:8px;white-space:nowrap;font:500 .75rem 'Noto Sans Arabic',sans-serif;color:#475569;z-index:50;pointer-events:none}
 `;
 doc.head.appendChild(css);
 var corner=doc.createElement('div'); corner.className='hf-corner'; corner.textContent='اسأل بصوتك · Ask by voice'; doc.body.appendChild(corner);
 var lang=win.localStorage.getItem('hf_lang')||'ar-JO', rec=null, on=false;
 var wrap=doc.createElement('span'); wrap.id='hf-mic-wrap'; wrap.className='hf-wrap';
 var mic=doc.createElement('button'); mic.type='button'; mic.className='hf-mic'; mic.setAttribute('aria-label','تحدث بالميكروفون'); mic.title='اضغط وتحدث';
 mic.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v4"/></svg>';
 var chip=doc.createElement('button'); chip.type='button'; chip.className='hf-lang';
 function setLang(l){lang=l; win.localStorage.setItem('hf_lang',l); chip.textContent=l.indexOf('ar')===0?'AR':'EN'; chip.title=l.indexOf('ar')===0?'لغة الكلام: العربية':'Speech language: English';}
 chip.onclick=function(e){e.preventDefault(); setLang(lang.indexOf('ar')===0?'en-US':'ar-JO');};
 function ta(){return doc.querySelector('[data-testid="stChatInputTextArea"]')||doc.querySelector('[data-testid="stChatInput"] textarea');}
 function setText(t){var el=ta(); if(!el)return; var set=Object.getOwnPropertyDescriptor(win.HTMLTextAreaElement.prototype,'value').set; set.call(el,t); el.dispatchEvent(new win.Event('input',{bubbles:true}));}
 function submit(){
  var b=doc.querySelector('[data-testid="stChatInputSubmitButton"]'); if(b){b.click();}
  setTimeout(function(){var el=ta(); if(el&&el.value){el.dispatchEvent(new win.KeyboardEvent('keydown',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true}));}},200);
 }
 mic.onclick=function(e){
  e.preventDefault();
  if(!SR){alert('المتصفح لا يدعم التعرف على الصوت. استخدم Chrome أو Edge. · Speech recognition is not supported in this browser.');return;}
  if(on){rec.stop();return;}
  if(win.__hfAudio){try{win.__hfAudio.pause();}catch(x){}}
  rec=new SR(); rec.lang=lang; rec.interimResults=true; rec.continuous=false;
  rec.onstart=function(){on=true; mic.classList.add('rec');};
  rec.onresult=function(ev){var t=''; for(var i=0;i<ev.results.length;i++){t+=ev.results[i][0].transcript;} setText(t); if(ev.results[ev.results.length-1].isFinal){setTimeout(submit,350);}};
  rec.onerror=function(ev){ if(ev.error==='not-allowed'||ev.error==='service-not-allowed'){alert('الميكروفون غير مسموح. فعّل الإذن من إعدادات المتصفح. · Microphone permission is blocked.');} };
  rec.onend=function(){on=false; mic.classList.remove('rec');};
  try{rec.start();}catch(x){}
 };
 wrap.appendChild(chip); wrap.appendChild(mic); setLang(lang);
 function place(){ if(doc.getElementById('hf-mic-wrap'))return; var b=doc.querySelector('[data-testid="stChatInputSubmitButton"]'); if(b&&b.parentNode){b.parentNode.insertBefore(wrap,b);} }
 place();
 new win.MutationObserver(place).observe(doc.body,{childList:true,subtree:true});
})();
</script>'''

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
.block-container{max-width:780px;padding:3.6rem 1rem 7rem!important}
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
[data-testid="stChatInput"]:focus-within,[data-testid="stChatInput"] div:focus-within{border-color:var(--navy)!important;box-shadow:0 0 0 2px rgba(11,42,92,.18)!important}
[data-testid="stChatInputSubmitButton"],[data-testid="stChatInput"] button{background:var(--navy)!important;color:#fff!important;border-radius:50%!important}
[data-testid="stChatInput"] button:disabled{background:#CBD5E1!important}
[data-testid="stChatInput"] textarea{caret-color:var(--navy)}
[data-testid="stAudioInput"]{filter:hue-rotate(205deg) saturate(1.3)}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"]{flex:0 1 auto!important;width:fit-content!important}
[data-testid="stAudio"] audio,audio{height:36px;width:100%;max-width:340px}
.stRadio label,.stToggle label{font-family:inherit}
.block-container{position:relative;isolation:isolate;background:transparent!important}
.toplinks{position:fixed;top:10px;left:12px;display:flex;gap:8px;z-index:60}
.toplinks a{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;min-height:36px;border:1px solid #0B2A5C;border-radius:999px;background:#fff;color:#0B2A5C!important;font-size:.82rem;font-weight:500;text-decoration:none!important;transition:all .2s ease}
.toplinks a:hover{background:#FFF9E8;border-color:#C9A24A}
.toplinks svg{width:16px;height:16px}
.st-key-vc{position:fixed!important;left:12px;bottom:6px;z-index:60;display:flex;flex-direction:row!important;flex-wrap:wrap;gap:8px!important;width:auto!important;max-width:calc(100vw - 24px)}
.st-key-vc button{min-height:34px;font-size:.78rem;padding:2px 12px}
.bgfx{position:fixed;inset:0;z-index:-1;pointer-events:none;overflow:hidden}
.bgfx:before{content:"";position:absolute;inset:0;background:radial-gradient(600px 400px at 85% 8%,rgba(201,162,74,.13),transparent 70%),radial-gradient(700px 500px at 8% 95%,rgba(11,42,92,.10),transparent 70%)}
.pt{position:absolute;bottom:-40px;border-radius:50%;opacity:0;animation:rise linear infinite}
.pt.g{background:#C9A24A}.pt.n{background:#0B2A5C}
.pt.h{border-radius:0;background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23C9A24A' stroke-width='1.5' stroke-linejoin='round'><path d='M3 11 12 3l9 8v10H3z'/><path d='M9 21v-6h6v6'/></svg>") center/contain no-repeat}
@keyframes rise{0%{transform:translate(0,0) rotate(0);opacity:0}12%{opacity:var(--o)}88%{opacity:var(--o)}100%{transform:translate(var(--dx),-115vh) rotate(40deg);opacity:0}}
@media (prefers-reduced-motion:reduce){.pt{animation:none;bottom:auto;top:var(--t);opacity:var(--o)}}
</style>""", unsafe_allow_html=True)


import random
_r = random.Random(11)
_p = []
for _i in range(30):
    _k = "h" if _i % 4 == 0 else ("n" if _i % 5 == 0 else "g")
    _sz = _r.randint(16, 26) if _k == "h" else _r.randint(3, 8)
    _o = 0.5 if _k == "h" else (0.22 if _k == "n" else 0.4)
    _p.append(f'<span class="pt {_k}" style="left:{_r.randint(2, 96)}%;width:{_sz}px;height:{_sz}px;'
              f'animation-duration:{_r.randint(22, 44)}s;animation-delay:-{_r.randint(0, 40)}s;'
              f'--dx:{_r.randint(-70, 70)}px;--o:{_o};--t:{_r.randint(5, 95)}%"></span>')
st.markdown('<div class="bgfx" aria-hidden="true">' + "".join(_p) + "</div>", unsafe_allow_html=True)


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


def answer(q, lang):
    t = q.lower() if lang == "en" else norm(q)
    best, score = None, 0
    for e in load_kb():
        keys = e["ke"] if lang == "en" else e["n"]
        sc = sum(len(k) for k in keys if k in t)
        if sc > score:
            best, score = e, sc
    if best and score >= 4:
        ar_md, links = to_md(best["a"])
        return (best["en"] if lang == "en" else ar_md), links, best["say_en" if lang == "en" else "say_ar"]
    return ((NO_ANSWER_EN, ["wa", "pt"], SAY_NO_EN) if lang == "en" else (NO_ANSWER, ["wa", "pt"], SAY_NO_AR))


def wrap(t, lang):
    d, a = ("rtl", "right") if lang == "ar" else ("ltr", "left")
    return f'<div dir="{d}" style="text-align:{a}">\n\n{t}\n\n</div>'


def tokens(text):
    for tok in re.findall(r"\s+|\S+", text):
        yield tok


def link_buttons(links, lang="ar"):
    cols = st.columns(len(links) + 1)
    wa = "WhatsApp" if lang == "en" else "واتساب الإدارة"
    pt = "Fund portal" if lang == "en" else "بوابة الصندوق"
    if "wa" in links:
        cols[0].link_button(wa, WA, icon=":material/chat:")
    if "pt" in links:
        cols[len(links) - 1].link_button(pt, PT, icon=":material/open_in_new:")


def spoken(md, lang):
    t = re.sub(r"\n\n\*\[.*?\]\*", "", md)
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", t)
    t = re.sub(r"^\s*[-*]\s*", "", t, flags=re.M)
    t = t.replace("%", " بالمئة" if lang == "ar" else " percent")
    t = re.sub(r"\s+", " ", re.sub(r"\s*\n+\s*", ". ", t)).strip()
    if len(t) > 900:
        t = t[:900].rsplit(". ", 1)[0] + "."
    return t


def tts(text, lang):
    ss_ = st.session_state
    if lang == "ar":
        voice = AR_VOICES[ss_.get("voice_idx", 0) % len(AR_VOICES)][0]
        for k, v in PRON.items():
            text = text.replace(k, v)
    else:
        voice = EN_VOICE
    rate = RATES[ss_.get("rate_idx", 1) % len(RATES)][1]
    parts = [p for p in re.split(r"(?<=[.!?؟])\s+", text) if p.strip()]
    try:
        import asyncio
        import edge_tts

        async def one(p):
            buf = b""
            async for c in edge_tts.Communicate(p, voice, rate=rate).stream():
                if c["type"] == "audio":
                    buf += c["data"]
            return buf

        async def run():
            return b"".join(await asyncio.gather(*[one(p) for p in parts]))

        loop = asyncio.new_event_loop()
        try:
            data = loop.run_until_complete(run())
        finally:
            loop.close()
        if data:
            return data, "edge"
    except Exception:
        pass
    try:
        from gtts import gTTS
        b = io.BytesIO()
        gTTS(text=text, lang=lang).write_to_fp(b)
        return b.getvalue(), "gtts"
    except Exception:
        return None, None


def play(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    components.html("<script>try{var w=window.parent;if(w.__hfAudio){w.__hfAudio.pause();}"
                    "w.__hfAudio=new w.Audio('data:audio/mp3;base64," + b64 + "');"
                    "w.__hfAudio.play().catch(function(){});}catch(e){}</script>", height=0)


ss = st.session_state
ss.setdefault("msgs", [("assistant", WELCOME, [], "ar")])
ss.setdefault("pending", None)
ss.setdefault("akey", 0)
ss.setdefault("last_audio", None)

img = f'<img src="data:image/png;base64,{logo_b64()}" alt="شعار صندوق إسكان العاملين">' if LOGO else ""
st.markdown(f'<div class="hero">{img}<h1>مساعد صندوق إسكان العاملين</h1>'
            '<p>الجامعة الأردنية</p><div class="rule"></div></div>', unsafe_allow_html=True)

_ic1 = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L3 21l1.9-6.2A8 8 0 1 1 21 12z"/></svg>'
_ic2 = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3h7v7M10 14 21 3M19 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h5"/></svg>'
st.markdown(f'<div class="toplinks"><a href="{WA}" target="_blank" rel="noopener">{_ic1}واتساب الإدارة</a>'
            f'<a href="{PT}" target="_blank" rel="noopener">{_ic2}بوابة الصندوق</a></div>', unsafe_allow_html=True)

if len(ss.msgs) <= 1 and not ss.pending:
    cols = st.columns(2)
    for i, q in enumerate(QUICK):
        if cols[i % 2].button(q, key=f"q{i}", use_container_width=True):
            ss.pending = q
            st.rerun()

for role, text, links, lang in ss.msgs:
    with st.chat_message(role, avatar=LOGO_PATH if role == "assistant" else None):
        st.markdown(wrap(html.escape(text) if role == "user" else text, lang), unsafe_allow_html=True)
        if links:
            link_buttons(links, lang)

if ss.pending:
    q, ss.pending = ss.pending, None
    lang = "ar" if AR.search(q) else "en"
    with st.chat_message("user"):
        st.markdown(wrap(html.escape(q), lang), unsafe_allow_html=True)
    text, links, say = answer(q, lang)
    with st.chat_message("assistant", avatar=LOGO_PATH):
        box = st.empty()
        box.markdown('<div class="typing"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
        audio, engine = tts(say, lang) if ss.get("voice_on", True) else (None, None)
        if audio is None:
            time.sleep(0.6)
        box.empty()
        if audio:
            play(audio)
            if engine == "gtts":
                st.caption("الصوت الاحتياطي مفعّل (الجودة أقل من المعتاد)")
        out, acc = st.empty(), ""
        for tok in tokens(text):
            acc += tok
            out.markdown(wrap(acc, lang), unsafe_allow_html=True)
            if tok.strip():
                time.sleep(0.04)
        if links:
            link_buttons(links, lang)
    ss.msgs += [("user", q, [], lang), ("assistant", text, links, lang)]

ss.setdefault("voice_on", True)
_on = "background:#0B2A5C!important;color:#fff!important;border-color:#0B2A5C!important"
st.markdown("<style>" + (f".st-key-voice_btn button{{{_on}}}" if ss.voice_on else "") + "</style>", unsafe_allow_html=True)
ss.setdefault("voice_idx", 0)
ss.setdefault("rate_idx", 1)
with st.container(key="vc"):
    if st.button("الرد الصوتي: " + ("مفعّل" if ss.voice_on else "متوقف"), key="voice_btn",
                 icon=":material/volume_up:" if ss.voice_on else ":material/volume_off:"):
        ss.voice_on = not ss.voice_on
        st.rerun()
    if st.button("الصوت: " + AR_VOICES[ss.voice_idx % len(AR_VOICES)][1], key="voice_pick", icon=":material/record_voice_over:"):
        ss.voice_idx = (ss.voice_idx + 1) % len(AR_VOICES)
        st.rerun()
    if st.button("السرعة: " + RATES[ss.rate_idx % len(RATES)][0], key="rate_btn", icon=":material/speed:"):
        ss.rate_idx = (ss.rate_idx + 1) % len(RATES)
        st.rerun()
components.html(MIC_JS, height=0)

if prompt := st.chat_input("اكتب سؤالك أو اضغط على الميكروفون… · Type or tap the mic"):
    ss.pending = prompt
    st.rerun()

