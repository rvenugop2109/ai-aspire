import re, os, subprocess

folder = os.path.dirname(os.path.abspath(__file__))

files = [
    "section_01_open.html",
    "section_02_programme.html",
    "section_03_complete.html",
    "section_04_complete.html",
    "section_05_complete.html",
    "section_06_complete.html",
    "section_07_complete.html",
]

dark_bg_slides = {1, 3, 4, 10, 16, 21, 24, 27, 30, 31}

all_css, all_slides = [], []

for f in files:
    path = os.path.join(folder, f)
    with open(path, 'r', encoding='utf-8') as fh:
        content = fh.read()
    css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if css_match:
        all_css.append(f"/* ── {f} ── */\n" + css_match.group(1).strip())
    deck_match = re.search(r'<div class="deck">(.*?)(?:</div><!-- /deck -->|\n</div>\n\n<div class="nav)', content, re.DOTALL)
    if deck_match:
        all_slides.append(deck_match.group(1).strip())

themes = ["'light'" if i in dark_bg_slides else "'dark'" for i in range(1, 32)]
themes_js = "const themes = [" + ",".join(themes) + "];"

combined_slides = "\n\n".join(all_slides)
combined_slides = re.sub(r'(\d+)\s*/\s*3[12]', lambda m: m.group(1) + ' / 31', combined_slides)

master = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Campuslogix AI Aspire for Schools</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--deep-blue:#1A1AE6;--mid-blue:#3333CC;--periwinkle:#7B7BE8;--pale-blue:#A0A0F5;--off-white:#F4F4FB;--dark-navy:#1C1C2E;--white:#FFFFFF;--mid-grey:#4A4A6A;--light-grey:#8888A8}
html,body{width:100%;height:100%;font-family:'Sora',sans-serif;overflow:hidden}
.deck{width:100vw;height:100vh;position:relative;overflow:hidden}
.slide{position:absolute;inset:0;width:100%;height:100%;transform:translateY(100%);transition:transform .45s cubic-bezier(.65,0,.35,1);will-change:transform;overflow:hidden}
.slide.active{transform:translateY(0)}.slide.prev{transform:translateY(-100%)}
.nav-dots{position:fixed;bottom:clamp(18px,2.5vw,32px);left:50%;transform:translateX(-50%);display:flex;gap:8px;z-index:1000;flex-wrap:wrap;justify-content:center;max-width:80vw}
.nav-dot{width:6px;height:6px;border-radius:50%;border:none;cursor:pointer;padding:0;transition:background .25s,transform .25s;flex-shrink:0}
.nav-dot.light{background:rgba(255,255,255,.25)}.nav-dot.dark{background:rgba(28,28,46,.18)}
.nav-dot.active.light{background:var(--periwinkle);transform:scale(1.4)}.nav-dot.active.dark{background:var(--deep-blue);transform:scale(1.4)}
.nav-arrow{position:fixed;left:50%;transform:translateX(-50%);z-index:1000;width:clamp(36px,3.5vw,48px);height:clamp(36px,3.5vw,48px);border-radius:50%;font-size:clamp(14px,1.4vw,18px);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .2s,border-color .2s,color .2s;backdrop-filter:blur(4px)}
.nav-arrow.light{border:1px solid rgba(255,255,255,.15);background:rgba(255,255,255,.06);color:rgba(255,255,255,.5)}
.nav-arrow.dark{border:1px solid rgba(26,26,230,.2);background:rgba(26,26,230,.06);color:var(--mid-grey)}
.nav-arrow.light:hover{background:rgba(123,123,232,.2);border-color:rgba(123,123,232,.4);color:var(--white)}
.nav-arrow.dark:hover{background:rgba(26,26,230,.12);border-color:rgba(26,26,230,.4);color:var(--deep-blue)}
.nav-arrow.up{top:clamp(12px,1.5vw,24px)}.nav-arrow.down{bottom:clamp(52px,6vw,76px)}
.nav-arrow:disabled{opacity:.2;cursor:default}
""" + "\n".join(all_css) + """
</style>
</head>
<body>
<div class="deck">
""" + combined_slides + """
</div>
<div class="nav-dots" id="dots"></div>
<button class="nav-arrow up light" id="btn-up" disabled>&#8593;</button>
<button class="nav-arrow down light" id="btn-down">&#8595;</button>
<script>
const slides=Array.from(document.querySelectorAll('.slide'));
const dotsEl=document.getElementById('dots');
const btnUp=document.getElementById('btn-up');
const btnDown=document.getElementById('btn-down');
let current=0;
""" + themes_js + """
slides.forEach((s,i)=>{if(i!==0)s.classList.remove('active');});
slides[0].classList.add('active');
slides.forEach((_,i)=>{
  const d=document.createElement('button');
  d.className='nav-dot '+themes[i]+(i===0?' active':'');
  d.setAttribute('aria-label','Slide '+(i+1));
  d.addEventListener('click',()=>goTo(i));
  dotsEl.appendChild(d);
});
const dots=Array.from(dotsEl.querySelectorAll('.nav-dot'));
function setArrows(idx){[btnUp,btnDown].forEach(b=>{b.className=b.className.replace(/\\b(light|dark)\\b/,themes[idx]);});}
function goTo(idx){
  if(idx<0||idx>=slides.length)return;
  slides[current].classList.remove('active');slides[current].classList.add('prev');
  const prev=slides[current];setTimeout(()=>prev.classList.remove('prev'),500);
  current=idx;slides[current].classList.remove('prev');slides[current].classList.add('active');
  dots.forEach((d,i)=>d.classList.toggle('active',i===current));
  btnUp.disabled=current===0;btnDown.disabled=current===slides.length-1;setArrows(current);
}
btnUp.addEventListener('click',()=>goTo(current-1));
btnDown.addEventListener('click',()=>goTo(current+1));
document.addEventListener('keydown',e=>{
  if(['ArrowDown','ArrowRight',' '].includes(e.key)){e.preventDefault();goTo(current+1);}
  if(['ArrowUp','ArrowLeft'].includes(e.key)){e.preventDefault();goTo(current-1);}
});
let ty=0;
document.addEventListener('touchstart',e=>{ty=e.touches[0].clientY;},{passive:true});
document.addEventListener('touchend',e=>{const dy=e.changedTouches[0].clientY-ty;if(Math.abs(dy)>50){dy<0?goTo(current+1):goTo(current-1);}});
</script>
</body>
</html>"""

out_path = os.path.join(folder, "campuslogix_deck_master.html")
with open(out_path, 'w', encoding='utf-8') as fh:
    fh.write(master)

size_kb = os.path.getsize(out_path) / 1024
print(f"Done. campuslogix_deck_master.html created ({size_kb:.0f} KB)")
subprocess.run(['open', out_path])
