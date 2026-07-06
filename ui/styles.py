CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&display=swap');

:root{
  --bg0:#030712;
  --bg1:#07111F;
  --panel:#0B1220;
  --card:#0F172A;
  --card2:#111827;
  --line:rgba(148,163,184,.18);
  --text:#F8FAFC;
  --muted:#94A3B8;
  --blue:#3B82F6;
  --cyan:#22D3EE;
  --green:#22C55E;
  --yellow:#FACC15;
  --orange:#FB923C;
  --red:#F43F5E;
  --purple:#A78BFA;
}

html, body, [class*="css"]{font-family:'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;}
.stApp{background:
  radial-gradient(circle at 20% 5%, rgba(59,130,246,.12), transparent 32%),
  radial-gradient(circle at 90% 12%, rgba(34,211,238,.10), transparent 25%),
  linear-gradient(180deg, #030712 0%, #050914 45%, #020617 100%);
}
.block-container{padding-top:1.1rem; padding-bottom:4rem; max-width:1320px;}

section[data-testid="stSidebar"]{background:linear-gradient(180deg, #0B1220 0%, #050914 100%); border-right:1px solid rgba(148,163,184,.14);}
section[data-testid="stSidebar"] *{font-family:'Inter', sans-serif;}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3{letter-spacing:-.4px;}

.drd-hero{
  position:relative; overflow:hidden; border:1px solid rgba(56,189,248,.20); border-radius:34px; padding:34px 36px; margin:0 0 26px 0;
  background:
    radial-gradient(circle at 9% 18%, rgba(34,211,238,.26), transparent 25%),
    radial-gradient(circle at 74% 0%, rgba(59,130,246,.34), transparent 29%),
    radial-gradient(circle at 102% 82%, rgba(167,139,250,.16), transparent 28%),
    linear-gradient(135deg, rgba(15,23,42,.98), rgba(2,8,23,.96));
  box-shadow:0 28px 70px rgba(0,0,0,.42), inset 0 1px 0 rgba(255,255,255,.08);
}
.drd-hero:after{content:""; position:absolute; right:-90px; top:-100px; width:280px; height:280px; border-radius:50%; background:rgba(34,211,238,.08); filter:blur(3px);}
.drd-kicker{font-size:12px; text-transform:uppercase; letter-spacing:.22em; color:#7DD3FC; font-weight:950; margin-bottom:10px;}
.drd-title{font-size:54px; font-weight:950; letter-spacing:-1.4px; line-height:1.0; margin:0; color:#F8FAFC; text-shadow:0 10px 30px rgba(0,0,0,.35);}
.drd-sub{opacity:.88; margin-top:13px; font-size:16px; color:#CBD5E1; max-width:820px; line-height:1.65;}
.drd-hero-badges{display:flex; flex-wrap:wrap; gap:10px; margin-top:22px;}

.drd-glass, .card, .drd-card, .drd-match-card, .rank-card{
  border:1px solid rgba(148,163,184,.16);
  background:linear-gradient(180deg, rgba(15,23,42,.88), rgba(2,6,23,.78));
  box-shadow:0 18px 44px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.04);
  backdrop-filter: blur(10px);
}
.card, .drd-card{border-radius:28px; padding:24px; min-height:128px; transition:.18s ease;}
.card:hover, .drd-card:hover, .rank-card:hover{transform:translateY(-1px); border-color:rgba(56,189,248,.28);}
.card h2, .drd-card h2{margin:0; font-size:27px; letter-spacing:-.6px;}
.card p, .drd-card p{opacity:.76; margin-bottom:0; color:#CBD5E1; line-height:1.55;}
.drd-card-compact{border:1px solid rgba(148,163,184,.14); border-radius:20px; padding:17px 18px; background:rgba(15,23,42,.72);}

.drd-stat-grid{display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:14px; margin:18px 0 10px;}
.drd-stat{border:1px solid rgba(148,163,184,.14); border-radius:22px; padding:18px; background:linear-gradient(180deg, rgba(15,23,42,.8), rgba(15,23,42,.38));}
.drd-stat-label{font-size:12px; color:#94A3B8; font-weight:900; text-transform:uppercase; letter-spacing:.08em;}
.drd-stat-value{font-size:27px; font-weight:950; margin-top:8px; color:#F8FAFC;}
.drd-stat-sub{font-size:12px; color:#94A3B8; margin-top:6px;}

.drd-match-card{border-radius:30px; padding:30px; min-height:150px;}
.drd-match-card h2{font-size:32px; margin:0; letter-spacing:-.8px;}
.drd-match-card p{color:#94A3B8; font-weight:700; margin-top:12px;}
.vs{font-size:66px; font-weight:950; text-align:center; padding-top:38px; opacity:.95; background:linear-gradient(135deg, #FFFFFF, #7DD3FC); -webkit-background-clip:text; color:transparent;}

.badge{display:inline-flex; align-items:center; gap:6px; border:1px solid rgba(148,163,184,.22); border-radius:999px; padding:8px 14px; margin:0 8px 8px 0; background:rgba(15,23,42,.72); font-weight:900; font-size:13px; color:#E5E7EB;}
.badge-green{border-color:rgba(34,197,94,.40); background:rgba(34,197,94,.14); color:#BBF7D0;}
.badge-yellow{border-color:rgba(250,204,21,.42); background:rgba(250,204,21,.12); color:#FEF08A;}
.badge-red{border-color:rgba(244,63,94,.42); background:rgba(244,63,94,.12); color:#FDA4AF;}
.badge-blue{border-color:rgba(59,130,246,.42); background:rgba(59,130,246,.14); color:#BFDBFE;}
.badge-purple{border-color:rgba(167,139,250,.42); background:rgba(167,139,250,.13); color:#DDD6FE;}
.small-muted{opacity:.72; font-size:13px; color:#CBD5E1;}
.verified{display:inline-flex; align-items:center; font-weight:950; letter-spacing:.3px; padding:10px 16px; border-radius:999px; border:1px solid rgba(34,197,94,.55); background:rgba(34,197,94,.16); color:#BBF7D0; margin-bottom:8px;}
.not-verified{display:inline-flex; align-items:center; font-weight:900; letter-spacing:.2px; padding:10px 16px; border-radius:999px; border:1px solid rgba(250,204,21,.45); background:rgba(250,204,21,.10); color:#FEF08A; margin-bottom:8px;}

.drd-status-ok{border-radius:22px; padding:18px; background:linear-gradient(135deg, rgba(34,197,94,.22), rgba(13,148,136,.12)); border:1px solid rgba(34,197,94,.30); color:#DCFCE7; font-weight:900; box-shadow:0 12px 30px rgba(0,0,0,.22);}
.drd-status-warn{border-radius:22px; padding:18px; background:linear-gradient(135deg, rgba(250,204,21,.18), rgba(245,158,11,.08)); border:1px solid rgba(250,204,21,.25); color:#FEF9C3; font-weight:900;}

.drd-section-title{font-size:32px; font-weight:950; letter-spacing:-.8px; margin:34px 0 16px;}
.drd-section-sub{margin-top:-8px; color:#94A3B8; font-weight:700;}
.drd-caption{font-size:13px; color:#94A3B8; margin-top:4px;}
.drd-callout, .drd-callout-yellow, .drd-callout-green{border-radius:20px; padding:17px 19px; font-weight:800; line-height:1.55;}
.drd-callout{border:1px solid rgba(59,130,246,.25); background:linear-gradient(135deg, rgba(59,130,246,.15), rgba(34,211,238,.06)); color:#DBEAFE;}
.drd-callout-yellow{border:1px solid rgba(250,204,21,.30); background:linear-gradient(135deg, rgba(250,204,21,.13), rgba(251,146,60,.06)); color:#FEF9C3;}
.drd-callout-green{border:1px solid rgba(34,197,94,.30); background:linear-gradient(135deg, rgba(34,197,94,.13), rgba(16,185,129,.06)); color:#DCFCE7;}

.rank-card{border-radius:26px; padding:22px 24px; margin-bottom:16px;}
.rank-title{font-size:25px; font-weight:950; margin:0 0 4px; letter-spacing:-.5px;}
.rank-sub{color:#94A3B8; font-size:13px; font-weight:800;}
.rank-pill{display:inline-block; border-radius:999px; padding:8px 12px; font-weight:950; font-size:12px; border:1px solid rgba(255,255,255,.14);}

.drd-premium-card{border:1px solid rgba(56,189,248,.18); border-radius:30px; padding:26px; background:linear-gradient(135deg, rgba(15,23,42,.92), rgba(30,41,59,.56)); min-height:220px;}
.drd-price{font-size:46px; font-weight:950; letter-spacing:-1px;}
.drd-feature{padding:9px 0; border-bottom:1px solid rgba(148,163,184,.10); color:#E2E8F0; font-weight:700;}
.drd-feature:last-child{border-bottom:0;}

/* Streamlit components */
hr{border-color:rgba(148,163,184,.16);}
[data-testid="stMetric"]{background:rgba(15,23,42,.50); border:1px solid rgba(148,163,184,.12); border-radius:20px; padding:14px 16px;}
[data-testid="stMetricValue"]{font-size:31px; font-weight:950;}
[data-testid="stMetricLabel"]{font-weight:900; color:#CBD5E1;}
.stButton > button{border-radius:18px; min-height:52px; font-weight:950; letter-spacing:.4px; background:linear-gradient(135deg, #EF4444, #F97316); border:0; box-shadow:0 14px 30px rgba(239,68,68,.22);}
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div{border-radius:16px !important; border-color:rgba(148,163,184,.22) !important; background-color:rgba(15,23,42,.78) !important;}
[data-testid="stTabs"] button{font-weight:950;}
[data-testid="stTabs"] [role="tablist"]{gap:6px; border-bottom:1px solid rgba(148,163,184,.14);}
[data-testid="stTabs"] [role="tab"]{border-radius:14px 14px 0 0; padding:11px 14px;}
[data-testid="stDataFrame"]{border-radius:18px; overflow:hidden;}

/* === DRD v1.4 ULTRA STREAMLIT SKIN === */
#MainMenu, header, footer {visibility:hidden;}
.block-container{padding-top:.5rem; max-width:1400px;}
.stApp:before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:linear-gradient(rgba(148,163,184,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,.035) 1px, transparent 1px);
  background-size:42px 42px; mask-image:linear-gradient(to bottom, rgba(0,0,0,.9), transparent 75%);
}
.block-container > div{position:relative; z-index:1;}

.drd-hero-pro{
  position:relative; overflow:hidden; display:grid; grid-template-columns:1.35fr .85fr; gap:26px;
  border:1px solid rgba(56,189,248,.24); border-radius:38px; padding:38px; margin:0 0 28px;
  background:
    radial-gradient(circle at 18% 16%, rgba(34,211,238,.24), transparent 25%),
    radial-gradient(circle at 79% 2%, rgba(59,130,246,.28), transparent 28%),
    linear-gradient(135deg, rgba(15,23,42,.97), rgba(2,6,23,.94));
  box-shadow:0 28px 100px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.08);
}
.drd-hero-pro:before{content:""; position:absolute; inset:-2px; background:linear-gradient(110deg, transparent 0%, rgba(34,211,238,.16) 38%, transparent 62%); transform:translateX(-100%); animation:drdSweep 7s infinite;}
@keyframes drdSweep{0%,45%{transform:translateX(-100%)} 65%,100%{transform:translateX(100%)}}
.drd-hero-glow{position:absolute; right:6%; top:10%; width:260px; height:260px; background:radial-gradient(circle, rgba(34,211,238,.18), transparent 68%); filter:blur(2px);}
.drd-hero-left,.drd-hero-right{position:relative; z-index:1;}
.drd-title-pro{font-size:62px; font-weight:1000; letter-spacing:-2px; line-height:.95; background:linear-gradient(90deg,#fff,#DFF7FF 42%,#7DD3FC 72%,#C4B5FD); -webkit-background-clip:text; color:transparent; text-shadow:0 12px 50px rgba(14,165,233,.08);}
.drd-sub-pro{margin-top:16px; color:#CBD5E1; font-weight:650; font-size:17px; line-height:1.7; max-width:850px;}
.drd-hero-right{display:grid; grid-template-columns:.95fr 1.05fr; gap:14px; align-items:center;}
.drd-score-orb{height:190px; border-radius:34px; display:grid; place-items:center; background:radial-gradient(circle at 30% 25%, rgba(34,211,238,.34), transparent 32%), linear-gradient(145deg, rgba(15,23,42,.8), rgba(2,6,23,.82)); border:1px solid rgba(125,211,252,.25); box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 20px 54px rgba(0,0,0,.35);}
.drd-score-num{font-size:46px; font-weight:1000; letter-spacing:-2px;}
.drd-score-label{font-size:12px; letter-spacing:.26em; color:#7DD3FC; font-weight:950;}
.drd-mini-feed{display:flex; flex-direction:column; gap:11px;}
.feed-row{display:flex; align-items:center; gap:10px; padding:13px 14px; border-radius:20px; background:rgba(15,23,42,.70); border:1px solid rgba(148,163,184,.14);}
.feed-row b{font-size:14px}.feed-row em{margin-left:auto; color:#94A3B8; font-size:12px; font-style:normal; font-weight:800;}

.score-orb-card{display:flex; gap:14px; align-items:center; border:1px solid rgba(148,163,184,.16); border-radius:24px; padding:16px; background:linear-gradient(180deg, rgba(15,23,42,.84), rgba(2,6,23,.70)); min-height:104px; box-shadow:0 14px 34px rgba(0,0,0,.24);}
.score-ring{--c:#3B82F6; width:78px; height:78px; flex:0 0 78px; border-radius:50%; display:grid; place-items:center; background:conic-gradient(var(--c) calc(var(--score)*1%), rgba(148,163,184,.14) 0); box-shadow:0 0 28px rgba(59,130,246,.12);}
.score-ring>div{width:62px; height:62px; border-radius:50%; display:grid; place-items:center; background:#07111F; line-height:1;}
.score-ring span{font-size:25px; font-weight:1000;}.score-ring small{font-size:10px; color:#94A3B8; font-weight:900; margin-top:-15px;}
.score-meta b{font-size:16px;}.score-meta p{margin:.25rem 0 0; color:#94A3B8; font-size:13px; font-weight:750;}
.score-green .score-ring{--c:#22C55E}.score-yellow .score-ring{--c:#FACC15}.score-orange .score-ring{--c:#FB923C}.score-red .score-ring{--c:#F43F5E}

.kpi-card{position:relative; overflow:hidden; border:1px solid rgba(148,163,184,.16); border-radius:24px; padding:18px 19px; min-height:118px; background:linear-gradient(180deg, rgba(15,23,42,.82), rgba(2,6,23,.70)); box-shadow:0 14px 36px rgba(0,0,0,.22);}
.kpi-card:before{content:""; position:absolute; left:0; top:0; width:100%; height:3px; background:#3B82F6; opacity:.9;}
.kpi-icon{font-size:23px; margin-bottom:8px}.kpi-title{color:#94A3B8; font-size:12px; font-weight:950; text-transform:uppercase; letter-spacing:.08em}.kpi-value{font-size:29px; font-weight:1000; letter-spacing:-.9px; margin-top:4px}.kpi-sub{color:#94A3B8; font-size:12px; font-weight:750; margin-top:3px}
.kpi-green:before{background:#22C55E}.kpi-yellow:before{background:#FACC15}.kpi-orange:before{background:#FB923C}.kpi-red:before{background:#F43F5E}.kpi-purple:before{background:#A78BFA}.kpi-blue:before{background:#3B82F6}

.drd-match-card{position:relative; overflow:hidden;}
.drd-match-card:before{content:""; position:absolute; inset:0; background:radial-gradient(circle at 15% 15%, rgba(34,211,238,.12), transparent 30%); pointer-events:none;}
.drd-match-card h2,.drd-match-card p,.team-tag{position:relative; z-index:1;}
.team-tag{display:inline-block; padding:6px 10px; border-radius:999px; background:rgba(59,130,246,.13); border:1px solid rgba(59,130,246,.26); color:#BFDBFE; font-size:11px; font-weight:950; letter-spacing:.12em; margin-bottom:16px;}
.pro-away .team-tag{background:rgba(167,139,250,.13); border-color:rgba(167,139,250,.26); color:#DDD6FE;}
.vs-pro{height:172px; display:grid; place-items:center;}
.vs-pro span{font-size:58px; font-weight:1000; letter-spacing:-3px; background:linear-gradient(135deg,#fff,#7DD3FC,#A78BFA); -webkit-background-clip:text; color:transparent; filter:drop-shadow(0 20px 34px rgba(34,211,238,.16));}

.rank-card-pro{display:flex; align-items:center; justify-content:space-between; gap:20px; border:1px solid rgba(148,163,184,.17); border-radius:28px; padding:22px 24px; margin-bottom:16px; background:linear-gradient(135deg, rgba(15,23,42,.88), rgba(2,6,23,.76)); box-shadow:0 16px 42px rgba(0,0,0,.24); transition:.16s ease;}
.rank-card-pro:hover{transform:translateY(-2px); border-color:rgba(125,211,252,.32);}
.rank-left{display:flex; align-items:center; gap:16px;}
.rank-medal{font-size:32px; width:48px; height:48px; display:grid; place-items:center; border-radius:18px; background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.08);}
.rank-title-pro{font-size:25px; font-weight:1000; letter-spacing:-.6px;}.rank-sub-pro{color:#CBD5E1; font-weight:850; margin-top:4px}.rank-note{color:#94A3B8; font-size:13px; margin-top:8px;}
.rank-scores{display:flex; gap:12px; align-items:stretch;}.rank-score-box{min-width:124px; border-radius:20px; padding:14px 16px; background:rgba(15,23,42,.76); border:1px solid rgba(148,163,184,.14); text-align:center;}.rank-score-box span{display:block; font-size:29px; font-weight:1000;}.rank-score-box small{display:block; color:#94A3B8; font-weight:900; font-size:11px; text-transform:uppercase; letter-spacing:.05em;}.rank-score-box.main{border-color:rgba(56,189,248,.28); background:rgba(14,165,233,.08);}
.rank-green{border-color:rgba(34,197,94,.25)}.rank-yellow{border-color:rgba(250,204,21,.22)}.rank-orange{border-color:rgba(251,146,60,.22)}.rank-red{border-color:rgba(244,63,94,.22)}

.stAlert{border-radius:20px; border:1px solid rgba(148,163,184,.16);} 
.stProgress > div > div > div{background:linear-gradient(90deg,#3B82F6,#22D3EE)!important;}
[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"]{display:none;}

@media (max-width: 900px){
  .drd-hero-pro{grid-template-columns:1fr; padding:26px; border-radius:28px;}
  .drd-title-pro{font-size:42px;}
  .drd-hero-right{grid-template-columns:1fr;}
  .drd-stat-grid{grid-template-columns:1fr 1fr;}
  .rank-card-pro{flex-direction:column; align-items:flex-start;}
  .rank-scores{width:100%;}.rank-score-box{flex:1; min-width:0;}
}

</style>
"""
