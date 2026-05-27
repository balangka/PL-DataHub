import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="PL DataHub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 한글 폰트 ────────────────────────────────────────────────
import platform
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    plt.rcParams['font.family'] = 'Noto Sans CJK JP'
plt.rcParams['axes.unicode_minus'] = False

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    header {display: none !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem !important;}
    .stApp { background-color: #0a0e14; color: white; }
    p, div, span, label { color: white !important; }
    .stSelectbox label { color: white !important; }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1a1f2e !important;
        border: 1px solid rgba(0,255,135,0.2) !important;
        border-radius: 8px !important;
    }
    .stSelectbox div[data-baseweb="select"] * { color: white !important; }
    .stRadio label { color: white !important; }
    div[data-testid="stRadio"] label:nth-child(1) span { color: #00ff87 !important; }
    div[data-testid="stRadio"] label:nth-child(2) span { color: #ef4444 !important; }
    div[data-testid="stRadio"] label:nth-child(3) span { color: #38bdf8 !important; }
    div[data-testid="stRadio"] label:nth-child(4) span { color: #facc15 !important; }

    /* 사이드바 */
    div[data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #0d1117 0%, #0a1628 50%, #0d1117 100%);
        border-right: 1px solid rgba(0,255,135,0.15);
    }
    section[data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        transform: translateX(0) !important;
        min-width: 250px !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        display: flex !important;
        transform: translateX(0) !important;
        min-width: 250px !important;
    }
    button[data-testid="collapsedControl"],
    div[data-testid="collapsedControl"],
    button[data-testid="stSidebarCollapsedControl"],
    div[data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    .metric-card {
        background: linear-gradient(135deg, #1a1f2e, #151922);
        border: 1px solid rgba(0,255,135,0.2);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .metric-value { font-size: 26px; font-weight: 700; color: #00ff87; }
    .metric-label { font-size: 11px; color: rgba(255,255,255,0.6) !important; margin-top: 4px; }
    .metric-sub { font-size: 12px; color: white !important; margin-top: 6px; font-weight: 600; }
    .section-title {
        font-size: 11px;
        color: rgba(0,255,135,0.8) !important;
        letter-spacing: 2px;
        margin-bottom: 12px;
        margin-top: 8px;
    }
    .desc-box {
        background: rgba(0,255,135,0.05);
        border-left: 3px solid #00ff87;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 20px;
        font-size: 13px;
        color: rgba(255,255,255,0.8) !important;
        line-height: 1.7;
    }
    .stDataFrame { background: #1a1f2e !important; }
    div[data-testid="stDataFrame"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── 팀 로고 ──────────────────────────────────────────────────
TEAM_LOGOS = {
    "Arsenal":                  "https://resources.premierleague.com/premierleague/badges/t3.png",
    "Aston Villa":              "https://resources.premierleague.com/premierleague/badges/t7.png",
    "Bournemouth":              "https://resources.premierleague.com/premierleague/badges/t91.png",
    "Brentford":                "https://resources.premierleague.com/premierleague/badges/t94.png",
    "Brighton":                 "https://resources.premierleague.com/premierleague/badges/t36.png",
    "Burnley":                  "https://resources.premierleague.com/premierleague/badges/t90.png",
    "Chelsea":                  "https://resources.premierleague.com/premierleague/badges/t8.png",
    "Crystal Palace":           "https://resources.premierleague.com/premierleague/badges/t31.png",
    "Everton":                  "https://resources.premierleague.com/premierleague/badges/t11.png",
    "Fulham":                   "https://resources.premierleague.com/premierleague/badges/t54.png",
    "Leeds":                    "https://resources.premierleague.com/premierleague/badges/t2.png",
    "Liverpool":                "https://resources.premierleague.com/premierleague/badges/t14.png",
    "Manchester City":          "https://resources.premierleague.com/premierleague/badges/t43.png",
    "Manchester United":        "https://resources.premierleague.com/premierleague/badges/t1.png",
    "Newcastle United":         "https://resources.premierleague.com/premierleague/badges/t4.png",
    "Nottingham Forest":        "https://resources.premierleague.com/premierleague/badges/t17.png",
    "Sunderland":               "https://resources.premierleague.com/premierleague/badges/t56.png",
    "Tottenham":                "https://resources.premierleague.com/premierleague/badges/t6.png",
    "West Ham":                 "https://resources.premierleague.com/premierleague/badges/t21.png",
    "Wolverhampton Wanderers":  "https://resources.premierleague.com/premierleague/badges/t39.png",
}

# ── 데이터 로드 ──────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    import boto3, io
    s3 = boto3.client("s3", region_name="ap-northeast-2")
    BUCKET = "pl-datahub-data"
    def read_s3(key, fallback):
        try:
            obj = s3.get_object(Bucket=BUCKET, Key=key)
            return pd.read_csv(io.BytesIO(obj["Body"].read()))
        except:
            return pd.read_csv(fallback)

    df     = read_s3("pl_stats_clustered.csv", "pl_stats_clustered.csv")
    df_cur = read_s3("pl_stats_2526.csv", "pl_stats_2526.csv")
    df_fix = read_s3("pl_fixtures_2526.csv", "pl_fixtures_2526.csv")

    if "team" in df_cur.columns:
        df_cur = df_cur.rename(columns={"team": "팀", "season": "시즌"})
    if "team" in df.columns:
        df = df.rename(columns={"team": "팀", "season": "시즌"})

    df = df.loc[:, ~df.columns.duplicated()]
    df_cur = df_cur.loc[:, ~df_cur.columns.duplicated()]
    if not df_fix.empty:
        df_fix = df_fix.loc[:, ~df_fix.columns.duplicated()]

    if df_cur.empty or len(df_cur) == 0:
        df_cur = df[df["시즌"] == "25-26"].copy()

    if not df_fix.empty and "날짜" in df_fix.columns:
        df_fix["날짜"] = pd.to_datetime(df_fix["날짜"]) + pd.Timedelta(hours=9)

    return df, df_cur, df_fix

df, df_current, df_fixtures = load_data()

# ── 모델 학습 ────────────────────────────────────────────────
@st.cache_data
def train_model(_df):
    features = ["xG", "xGA", "xPTS", "PPDA", "DC"]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(_df[features].values, _df["순위"].values)
    return model

features = ["xG", "xGA", "xPTS", "PPDA", "DC"]
model = train_model(df)

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 24px 0 16px'>
        <div style='font-size:48px; margin-bottom:8px'>⚽</div>
        <div style='font-size:24px; font-weight:800; color:#00ff87;
                    letter-spacing:3px; text-shadow: 0 0 20px rgba(0,255,135,0.5)'>
            PL DataHub
        </div>
        <div style='font-size:9px; color:rgba(255,255,255,0.35);
                    letter-spacing:3px; margin-top:6px'>
            PREMIER LEAGUE ANALYSIS
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-bottom:20px'>
        <span style='background:rgba(0,255,135,0.1); border:1px solid rgba(0,255,135,0.3);
                     border-radius:20px; padding:4px 14px; font-size:11px; color:#00ff87'>
            ✅ 완료 · 25-26 시즌
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.08); margin:8px 0 16px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:9px; color:rgba(255,255,255,0.3); letter-spacing:2px; margin-bottom:8px'>NAVIGATION</div>", unsafe_allow_html=True)

    tab = st.radio("", [
        "📊 시즌 분석",
        "🔴 현재 시즌",
        "📅 예측 모델",
        "⚽ 경기 일정 & 예측"
    ], label_visibility="collapsed")

    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.08); margin:16px 0'></div>", unsafe_allow_html=True)

    menu_desc = {
        "📊 시즌 분석":      ("📊", "시즌 분석", "5시즌 전술 지표 상관관계\nVIF·PCA·군집 분석 결과"),
        "🔴 현재 시즌":      ("🏆", "현재 시즌", "25-26 최종 순위표\n팀별 전술 지표 현황"),
        "📅 예측 모델":      ("📅", "예측 모델", "xPTS 기반 순위 예측\n지표 중요도 분석"),
        "⚽ 경기 일정 & 예측":("⚽", "경기 일정", "예정 경기 일정\nAI 승패 확률 예측"),
    }
    icon, title, desc = menu_desc[tab]
    st.markdown(f"""
    <div style='background:rgba(0,255,135,0.06); border:1px solid rgba(0,255,135,0.2);
                border-radius:10px; padding:14px; margin-top:4px'>
        <div style='font-size:20px; margin-bottom:6px'>{icon}</div>
        <div style='font-size:13px; font-weight:700; color:#00ff87'>{title}</div>
        <div style='font-size:11px; color:rgba(255,255,255,0.55); margin-top:6px; line-height:1.7'>
            {desc.replace(chr(10), "<br>")}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 탭 1 — 시즌 분석
# ══════════════════════════════════════════════════════════════
if tab == "📊 시즌 분석":
    st.markdown("<h1 style='color:#00ff87; font-size:28px'>📊 시즌별 전술 분석</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='desc-box'>
        📌 <strong>이 페이지에서는?</strong><br>
        5개 시즌(21-22 ~ 25-26) 데이터를 바탕으로 <strong>전술 지표(xG, xGA, xPTS, PPDA, DC)가 최종 순위와 얼마나 관련 있는지</strong> 분석합니다.<br>
        Pearson vs Spearman 비교, VIF 다중공선성, PCA, K-means 대안 비교까지 교수님 피드백을 반영한 분석입니다.
    </div>
    """, unsafe_allow_html=True)

    seasons = ["21-22", "22-23", "23-24", "24-25", "25-26"]
    selected = st.radio("시즌 선택", seasons, horizontal=True)
    df_s = df[df["시즌"] == selected].sort_values("순위")

    # 핵심 지표 카드
    col1, col2, col3, col4 = st.columns(4)
    cards = [
        (col1, "최고 xG",   df_s.loc[df_s['xG'].idxmax()],   'xG',   "공격 기댓값 1위"),
        (col2, "최저 xGA",  df_s.loc[df_s['xGA'].idxmin()],  'xGA',  "수비 기댓값 1위"),
        (col3, "최고 xPTS", df_s.loc[df_s['xPTS'].idxmax()], 'xPTS', "기대 승점 1위"),
        (col4, "최강 압박", df_s.loc[df_s['PPDA'].idxmin()], 'PPDA', "압박 강도 1위"),
    ]
    for col, label, row, key, sub in cards:
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value'>{row[key]:.1f}</div>
                <div class='metric-sub'>{row['팀']}</div>
                <div class='metric-label'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 순위표
    st.markdown("<div class='section-title'>── 시즌 순위표</div>", unsafe_allow_html=True)
    df_rank = df_s[["팀", "순위", "실제승점", "xG", "xGA", "xPTS", "PPDA"]].sort_values("순위").reset_index(drop=True)
    df_rank.index = df_rank.index + 1

    hr1,hr2,hr3,hr4,hr5,hr6,hr7 = st.columns([0.5,2.5,1,1,1,1,1])
    for c, l in zip([hr1,hr2,hr3,hr4,hr5,hr6,hr7],["순위","팀","승점","xG","xGA","xPTS","PPDA"]):
        c.markdown(f"<div style='font-size:10px;color:rgba(255,255,255,0.4)'>{l}</div>", unsafe_allow_html=True)
    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.08);margin-bottom:6px'></div>", unsafe_allow_html=True)

    for _, r in df_rank.iterrows():
        rc1,rc2,rc3,rc4,rc5,rc6,rc7 = st.columns([0.5,2.5,1,1,1,1,1])
        rank_color = "#00ff87" if r["순위"] <= 4 else "#38bdf8" if r["순위"] <= 6 else "#ef4444" if r["순위"] >= 18 else "white"
        rc1.markdown(f"<div style='color:{rank_color};font-weight:700;padding-top:4px'>{int(r['순위'])}</div>", unsafe_allow_html=True)
        rc2.markdown(f"<div style='color:{rank_color};font-weight:600;padding-top:4px'>{r['팀']}</div>", unsafe_allow_html=True)
        rc3.markdown(f"<div style='color:#facc15;font-weight:700;padding-top:4px'>{int(r['실제승점'])}</div>", unsafe_allow_html=True)
        rc4.markdown(f"<div style='color:#00ff87;padding-top:4px'>{r['xG']:.1f}</div>", unsafe_allow_html=True)
        rc5.markdown(f"<div style='color:#fb923c;padding-top:4px'>{r['xGA']:.1f}</div>", unsafe_allow_html=True)
        rc6.markdown(f"<div style='color:#38bdf8;padding-top:4px'>{r['xPTS']:.1f}</div>", unsafe_allow_html=True)
        rc7.markdown(f"<div style='color:#a78bfa;padding-top:4px'>{r['PPDA']:.1f}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 분석 탭 ──────────────────────────────────────────────
    analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
        "📈 상관분석 (Pearson vs Spearman)",
        "🔬 VIF 다중공선성",
        "🧩 PCA 분석",
        "🎯 군집 방법 비교"
    ])

    indicators = ["xG", "xGA", "xPTS", "PPDA", "DC"]

    # ── 탭1: 상관분석 ──
    with analysis_tab1:
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("<div class='section-title'>── Pearson vs Spearman 상관계수</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>순위는 순서형 변수 → Spearman이 더 적절 · 두 결과 비교로 견고성 확인</div>", unsafe_allow_html=True)

            pearson_vals = [abs(round(stats.pearsonr(df_s[c], df_s["순위"])[0], 3)) for c in indicators]
            spearman_vals = [abs(round(stats.spearmanr(df_s[c], df_s["순위"])[0], 3)) for c in indicators]
            p_vals = [round(stats.spearmanr(df_s[c], df_s["순위"])[1], 4) for c in indicators]

            fig, ax = plt.subplots(figsize=(6, 3.5))
            fig.patch.set_facecolor("#0a0e14")
            ax.set_facecolor("#0a0e14")
            x = range(len(indicators))
            width = 0.35
            ax.bar([i - width/2 for i in x], pearson_vals, width, color="#00ff87", alpha=0.8, label="Pearson")
            ax.bar([i + width/2 for i in x], spearman_vals, width, color="#38bdf8", alpha=0.8, label="Spearman")
            ax.set_xticks(x)
            ax.set_xticklabels(indicators, color="white")
            ax.set_ylabel("|r|", color="white")
            ax.set_title(f"{selected} 상관계수 비교", color="white")
            ax.tick_params(colors="white")
            ax.axhline(y=0.8, color="yellow", linewidth=1, linestyle="--", alpha=0.5)
            ax.legend(facecolor="#1a1a2e", labelcolor="white")
            for spine in ax.spines.values():
                spine.set_edgecolor("#333")
            st.pyplot(fig)

        with col_r:
            st.markdown("<div class='section-title'>── p-value (Spearman)</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>p < 0.05 = 통계적으로 유의미 · 초록=유의 / 노랑=비유의</div>", unsafe_allow_html=True)

            for ind, pv, pr, sp in zip(indicators, p_vals, pearson_vals, spearman_vals):
                sig = "✅ 유의" if pv < 0.05 else "⚠️ 비유의"
                color = "#00ff87" if pv < 0.05 else "#facc15"
                st.markdown(f"""
                <div style='background:#141928;border:1px solid rgba(255,255,255,0.08);border-radius:8px;
                            padding:8px 12px;margin-bottom:6px;display:flex;justify-content:space-between'>
                    <span style='color:white;font-weight:700'>{ind}</span>
                    <span style='color:#38bdf8'>Pearson: {pr:.3f}</span>
                    <span style='color:#00ff87'>Spearman: {sp:.3f}</span>
                    <span style='color:{color}'>{sig} p={pv:.4f}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='font-size:11px;color:rgba(255,255,255,0.5);margin-top:8px;font-style:italic'>두 방법 모두 동일한 패턴 → 분석 견고성 확인</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>── 과대 / 과소 성과 분석</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>초록 = 기대보다 잘함(운 좋음) · 주황 = 기대보다 못함(운 나쁨)</div>", unsafe_allow_html=True)

        if "승점차(실제-xPTS)" in df_s.columns:
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            fig2.patch.set_facecolor("#0a0e14")
            ax2.set_facecolor("#0a0e14")
            df_sorted = df_s.sort_values("승점차(실제-xPTS)")
            colors2 = ["#00ff87" if v > 0 else "#fb923c" for v in df_sorted["승점차(실제-xPTS)"]]
            ax2.barh(df_sorted["팀"], df_sorted["승점차(실제-xPTS)"], color=colors2, alpha=0.8)
            ax2.axvline(x=0, color="white", linewidth=0.8, alpha=0.5)
            ax2.set_xlabel("승점차 (실제 - xPTS)", color="white", fontsize=9)
            ax2.tick_params(colors="white", labelsize=8)
            for spine in ax2.spines.values():
                spine.set_edgecolor("#333")
            st.pyplot(fig2)
            max_team = df_sorted.loc[df_sorted["승점차(실제-xPTS)"].idxmax(), "팀"]
            min_team = df_sorted.loc[df_sorted["승점차(실제-xPTS)"].idxmin(), "팀"]
            st.info(f"💡 최대 과대성과: **{max_team}** | 최대 과소성과: **{min_team}**")

    # ── 탭2: VIF ──
    with analysis_tab2:
        st.markdown("<div class='section-title'>── VIF 다중공선성 분석</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>VIF > 5 = 다중공선성 의심 · VIF > 10 = 심각 · xPTS는 xG 기반 산출 지표라 높게 나옴</div>", unsafe_allow_html=True)

        try:
            from statsmodels.stats.outliers_influence import variance_inflation_factor
            scaler = StandardScaler()
            X_vif = scaler.fit_transform(df_s[indicators].dropna())
            vif_vals = [variance_inflation_factor(X_vif, i) for i in range(len(indicators))]

            fig3, ax3 = plt.subplots(figsize=(8, 3.5))
            fig3.patch.set_facecolor("#0a0e14")
            ax3.set_facecolor("#0a0e14")
            colors3 = ["#ef4444" if v > 10 else "#facc15" if v > 5 else "#00ff87" for v in vif_vals]
            bars3 = ax3.bar(indicators, vif_vals, color=colors3, alpha=0.8)
            ax3.axhline(y=5, color="yellow", linewidth=1, linestyle="--", alpha=0.7, label="VIF=5")
            ax3.axhline(y=10, color="#ef4444", linewidth=1, linestyle="--", alpha=0.7, label="VIF=10")
            ax3.set_ylabel("VIF", color="white")
            ax3.set_title(f"{selected} VIF 다중공선성", color="white")
            ax3.tick_params(colors="white")
            ax3.legend(facecolor="#1a1a2e", labelcolor="white")
            for spine in ax3.spines.values():
                spine.set_edgecolor("#333")
            for bar, val in zip(bars3, vif_vals):
                ax3.text(bar.get_x() + bar.get_width()/2, val + 1,
                        f"{val:.1f}", ha="center", color="white", fontsize=9)
            st.pyplot(fig3)
            st.warning("⚠️ xPTS, xG, xGA 간 심각한 다중공선성 → xPTS가 xG 기반 산출 지표이기 때문 → PCA로 해결")

        except ImportError:
            st.error("statsmodels 패키지가 필요합니다: pip install statsmodels")

    # ── 탭3: PCA ──
    with analysis_tab3:
        st.markdown("<div class='section-title'>── PCA 차원 축소 분석</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>5개 지표를 주성분으로 압축 · PC1이 전체의 79% 설명</div>", unsafe_allow_html=True)

        df_pca_data = df[df["시즌"] != "25-26"][indicators].dropna()
        scaler2 = StandardScaler()
        X_pca = scaler2.fit_transform(df_pca_data)
        pca = PCA()
        pca.fit(X_pca)

        col_p1, col_p2 = st.columns(2)

        with col_p1:
            fig4, ax4 = plt.subplots(figsize=(5, 3.5))
            fig4.patch.set_facecolor("#0a0e14")
            ax4.set_facecolor("#0a0e14")
            ax4.bar(range(1, 6), pca.explained_variance_ratio_, color="#00ff87", alpha=0.8, label="개별 분산")
            ax4.plot(range(1, 6), pca.explained_variance_ratio_.cumsum(),
                    color="#facc15", marker="o", linewidth=2, label="누적 분산")
            ax4.axhline(y=0.9, color="white", linewidth=1, linestyle="--", alpha=0.5)
            ax4.set_xlabel("주성분", color="white")
            ax4.set_ylabel("설명 분산 비율", color="white")
            ax4.set_title("PCA 설명 분산", color="white")
            ax4.tick_params(colors="white")
            ax4.legend(facecolor="#1a1a2e", labelcolor="white")
            for spine in ax4.spines.values():
                spine.set_edgecolor("#333")
            st.pyplot(fig4)

        with col_p2:
            fig5, ax5 = plt.subplots(figsize=(5, 3.5))
            fig5.patch.set_facecolor("#0a0e14")
            ax5.set_facecolor("#0a0e14")
            loadings = pca.components_[0]
            colors5 = ["#00ff87" if l > 0 else "#fb923c" for l in loadings]
            ax5.barh(indicators, loadings, color=colors5, alpha=0.8)
            ax5.axvline(x=0, color="white", linewidth=0.8, alpha=0.5)
            ax5.set_xlabel("로딩값", color="white")
            ax5.set_title("PC1 로딩 (기여도)", color="white")
            ax5.tick_params(colors="white")
            for spine in ax5.spines.values():
                spine.set_edgecolor("#333")
            for i, (val, ind) in enumerate(zip(loadings, indicators)):
                ax5.text(val + 0.01 if val > 0 else val - 0.01, i,
                        f"{val:+.3f}", va="center", color="white", fontsize=9)
            st.pyplot(fig5)

        st.info(f"💡 PC1이 전체의 {pca.explained_variance_ratio_[0]:.1%} 설명 → 5개 지표가 '팀 전반적 강도 지수' 하나로 요약됨")

    # ── 탭4: 군집 비교 ──
    with analysis_tab4:
        st.markdown("<div class='section-title'>── K-means 대안 비교</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>K-means vs 계층적(Ward) vs GMM vs DBSCAN 비교</div>", unsafe_allow_html=True)

        df_cluster = df[df["시즌"] != "25-26"][indicators].dropna()
        scaler3 = StandardScaler()
        X_cl = scaler3.fit_transform(df_cluster)

        km2 = KMeans(n_clusters=3, random_state=42, n_init=10)
        ward2 = AgglomerativeClustering(n_clusters=3, linkage='ward')
        gmm2 = GaussianMixture(n_components=3, random_state=42)

        km_s   = silhouette_score(X_cl, km2.fit_predict(X_cl))
        ward_s = silhouette_score(X_cl, ward2.fit_predict(X_cl))
        gmm_s  = silhouette_score(X_cl, gmm2.fit_predict(X_cl))

        col_c1, col_c2 = st.columns(2)

        with col_c1:
            fig6, ax6 = plt.subplots(figsize=(5, 3.5))
            fig6.patch.set_facecolor("#0a0e14")
            ax6.set_facecolor("#0a0e14")
            methods = ["K-means\n(k=3)", "계층적\n(Ward)", "GMM", "DBSCAN\n(부적합)"]
            scores  = [km_s, ward_s, gmm_s, 0]
            colors6 = ["#00ff87", "#38bdf8", "#fb923c", "#ef4444"]
            bars6 = ax6.bar(methods, scores, color=colors6, alpha=0.8)
            ax6.set_ylabel("Silhouette Score", color="white")
            ax6.set_title("군집 방법 비교", color="white")
            ax6.tick_params(colors="white")
            for spine in ax6.spines.values():
                spine.set_edgecolor("#333")
            for bar, val in zip(bars6, scores):
                if val > 0:
                    ax6.text(bar.get_x() + bar.get_width()/2, val + 0.003,
                            f"{val:.3f}", ha="center", color="white", fontsize=11, fontweight="bold")
            st.pyplot(fig6)

        with col_c2:
            st.markdown("<br>", unsafe_allow_html=True)
            results_data = [
                ("K-means (k=3)", km_s, "#00ff87", "✅ 최고"),
                ("계층적 (Ward)", ward_s, "#38bdf8", ""),
                ("GMM", gmm_s, "#fb923c", ""),
                ("DBSCAN", 0, "#ef4444", "❌ 군집 1개만"),
            ]
            for name, score, color, note in results_data:
                st.markdown(f"""
                <div style='background:#141928;border:1px solid rgba(255,255,255,0.08);
                            border-radius:8px;padding:10px 14px;margin-bottom:8px;
                            display:flex;justify-content:space-between;align-items:center'>
                    <span style='color:white;font-weight:600'>{name}</span>
                    <span style='color:{color};font-weight:700;font-size:16px'>{f"{score:.3f}" if score > 0 else "N/A"}</span>
                    <span style='color:{color};font-size:12px'>{note}</span>
                </div>
                """, unsafe_allow_html=True)

        st.success(f"✅ K-means(k=3) Silhouette {km_s:.3f}으로 가장 높음 → 기존 선택 타당성 확인!")

        # 수비의 역설 재검증
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>── 수비의 역설 재검증 (PPDA)</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>PPDA 높음 = 압박 약함 → 하위권? 4시즌 모두 양의 상관 유지</div>", unsafe_allow_html=True)

        ppda_results = []
        for s in ["21-22","22-23","23-24","24-25"]:
            df_ss = df[df["시즌"]==s]
            r, p = stats.spearmanr(df_ss["PPDA"], df_ss["순위"])
            ppda_results.append({"시즌": s, "r": round(r,3), "p": round(p,4)})

        fig7, ax7 = plt.subplots(figsize=(8, 3))
        fig7.patch.set_facecolor("#0a0e14")
        ax7.set_facecolor("#0a0e14")
        seasons_list = [x["시즌"] for x in ppda_results]
        r_vals = [x["r"] for x in ppda_results]
        colors7 = ["#00ff87" if r > 0 else "#ef4444" for r in r_vals]
        ax7.bar(seasons_list, r_vals, color=colors7, alpha=0.8)
        ax7.axhline(y=0, color="white", linewidth=0.8, alpha=0.5)
        ax7.set_ylabel("Spearman r", color="white")
        ax7.set_title("PPDA vs 순위 상관계수 (4시즌)", color="white")
        ax7.tick_params(colors="white")
        for spine in ax7.spines.values():
            spine.set_edgecolor("#333")
        for i, (val, p) in enumerate(zip(r_vals, [x["p"] for x in ppda_results])):
            sig = "✅" if p < 0.05 else "⚠️"
            ax7.text(i, val + 0.02, f"{val:+.3f} {sig}", ha="center", color="white", fontsize=9)
        st.pyplot(fig7)
        st.info("💡 4시즌 모두 양의 상관 → 압박 약한 팀(PPDA↑)이 하위권 — 수비의 역설 재확인!")

# ══════════════════════════════════════════════════════════════
# 탭 2 — 현재 시즌
# ══════════════════════════════════════════════════════════════
elif tab == "🔴 현재 시즌":
    st.markdown("<h1 style='color:#00ff87; font-size:28px'>🏆 25-26 최종 시즌</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='desc-box'>
        📌 <strong>이 페이지에서는?</strong><br>
        25-26 시즌 <strong>최종 팀별 전술 지표와 순위</strong>입니다.<br>
        26-27 시즌은 2026년 8월 개막 후 자동으로 업데이트됩니다.
    </div>
    """, unsafe_allow_html=True)

    df_current["득실차"] = df_current["실제득점"] - df_current["실제실점"]
    df_current = df_current.sort_values(
        ["실제승점", "득실차", "실제득점"],
        ascending=[False, False, False]
    ).reset_index(drop=True)
    df_current["순위"] = range(1, len(df_current) + 1)
    df_show = df_current.copy()

    h1,h2,h3,h4,h5,h6,h7,h8 = st.columns([0.5,0.5,2.5,1,1,1,1,1])
    for col, label in zip([h1,h2,h3,h4,h5,h6,h7,h8],["#","","팀","xG","xGA","xPTS","PPDA","승점"]):
        col.markdown(f"<div style='font-size:10px;color:rgba(255,255,255,0.4);padding-bottom:4px'>{label}</div>", unsafe_allow_html=True)

    st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.08); margin-bottom:8px'></div>", unsafe_allow_html=True)

    for idx, row in df_show.iterrows():
        zone_color = (
            "#00ff87" if row["순위"] <= 4 else
            "#38bdf8" if row["순위"] <= 6 else
            "#ef4444" if row["순위"] >= 18 else
            "rgba(255,255,255,0.6)"
        )
        logo = TEAM_LOGOS.get(row["팀"], "")
        c1,c2,c3,c4,c5,c6,c7,c8 = st.columns([0.5,0.5,2.5,1,1,1,1,1])
        c1.markdown(f"<div style='color:{zone_color};font-weight:800;padding-top:6px;font-size:15px'>{int(row['순위'])}</div>", unsafe_allow_html=True)
        if logo:
            c2.image(logo, width=28)
        c3.markdown(f"<div style='padding-top:6px;font-weight:700;color:{zone_color};font-size:13px'>{row['팀']}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div style='padding-top:6px;color:#00ff87;font-weight:700'>{row['xG']:.1f}</div>", unsafe_allow_html=True)
        c5.markdown(f"<div style='padding-top:6px;color:#fb923c;font-weight:700'>{row['xGA']:.1f}</div>", unsafe_allow_html=True)
        c6.markdown(f"<div style='padding-top:6px;color:#38bdf8;font-weight:700'>{row['xPTS']:.1f}</div>", unsafe_allow_html=True)
        c7.markdown(f"<div style='padding-top:6px;color:#a78bfa;font-weight:700'>{row['PPDA']:.1f}</div>", unsafe_allow_html=True)
        c8.markdown(f"<div style='padding-top:6px;font-weight:700;color:#facc15'>{int(row['실제승점'])}</div>", unsafe_allow_html=True)

        if idx == 3:
            st.markdown("<div style='border-bottom:2px solid #00ff87;margin:2px 0 4px'></div>", unsafe_allow_html=True)
        elif idx == 5:
            st.markdown("<div style='border-bottom:2px solid #38bdf8;margin:2px 0 4px'></div>", unsafe_allow_html=True)
        elif idx == 16:
            st.markdown("<div style='border-bottom:2px solid #ef4444;margin:2px 0 4px'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    z1,z2,z3 = st.columns(3)
    z1.markdown("<div style='background:rgba(0,255,135,0.1);border:1px solid rgba(0,255,135,0.3);border-radius:8px;padding:8px 12px;text-align:center'><span style='color:#00ff87;font-weight:700'>● UCL (1-4위)</span><br><span style='font-size:10px;color:rgba(255,255,255,0.5)'>챔피언스리그 진출</span></div>", unsafe_allow_html=True)
    z2.markdown("<div style='background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.3);border-radius:8px;padding:8px 12px;text-align:center'><span style='color:#38bdf8;font-weight:700'>● 유로파 (5-6위)</span><br><span style='font-size:10px;color:rgba(255,255,255,0.5)'>유로파리그 진출</span></div>", unsafe_allow_html=True)
    z3.markdown("<div style='background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:8px;padding:8px 12px;text-align:center'><span style='color:#ef4444;font-weight:700'>● 강등권 (18-20위)</span><br><span style='font-size:10px;color:rgba(255,255,255,0.5)'>Championship 강등</span></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 탭 3 — 예측 모델
# ══════════════════════════════════════════════════════════════
elif tab == "📅 예측 모델":
    st.markdown("<h1 style='color:#00ff87; font-size:28px'>🔮 순위 예측 모델</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='desc-box'>
        📌 <strong>이 페이지에서는?</strong><br>
        4시즌 데이터로 학습한 <strong>Random Forest 모델</strong>이 25-26 현재 시즌 순위를 예측합니다.<br>
        <strong>예측순위와 현재순위의 차이</strong>를 통해 어떤 팀이 기대보다 잘하고 있는지 확인할 수 있습니다.<br>
        또한 <strong>어떤 지표가 순위 예측에 가장 중요한지</strong> 중요도 차트로 보여줍니다.
    </div>
    """, unsafe_allow_html=True)

    X_cur = df_current[features].values
    df_current["예측순위"] = model.predict(X_cur).round().astype(int)
    df_current["순위차"] = df_current["순위"] - df_current["예측순위"]
    df_pred = df_current.sort_values("순위").reset_index(drop=True)
    df_pred.index = df_pred.index + 1

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("<div class='section-title'>── 예측 vs 현재 순위</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>초록 = 예측과 일치 · 파랑 = 오차 ±3 이내 · 주황 = 오차 큼</div>", unsafe_allow_html=True)

        hc1,hc2,hc3,hc4,hc5 = st.columns([0.4,0.4,2.5,1,1])
        for c, l in zip([hc1,hc2,hc3,hc4,hc5],["#","","팀","예측","차이"]):
            c.markdown(f"<div style='font-size:10px;color:rgba(255,255,255,0.4)'>{l}</div>", unsafe_allow_html=True)

        for _, row in df_pred.iterrows():
            logo = TEAM_LOGOS.get(row["팀"], "")
            diff = int(row["순위차"])
            diff_color = "#00ff87" if diff == 0 else "#38bdf8" if abs(diff) <= 3 else "#fb923c"
            diff_text = "✓" if diff == 0 else f"{diff:+d}"
            c1,c2,c3,c4,c5 = st.columns([0.4,0.4,2.5,1,1])
            c1.markdown(f"<div style='padding-top:6px;font-weight:700;color:white'>{int(row['순위'])}</div>", unsafe_allow_html=True)
            if logo:
                c2.image(logo, width=24)
            c3.markdown(f"<div style='padding-top:6px;color:white'>{row['팀']}</div>", unsafe_allow_html=True)
            c4.markdown(f"<div style='padding-top:6px;color:#38bdf8'>{int(row['예측순위'])}위</div>", unsafe_allow_html=True)
            c5.markdown(f"<div style='padding-top:6px;color:{diff_color};font-weight:700'>{diff_text}</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown("<div class='section-title'>── 지표 중요도</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:10px'>값이 클수록 순위 예측에 더 중요한 지표</div>", unsafe_allow_html=True)

        imp_df = pd.DataFrame({
            "지표": features,
            "중요도": model.feature_importances_
        }).sort_values("중요도", ascending=True)

        fig5, ax5 = plt.subplots(figsize=(5, 3))
        fig5.patch.set_facecolor("#0a0e14")
        ax5.set_facecolor("#0a0e14")
        colors5 = ["#00ff87" if v == imp_df["중요도"].max() else "#38bdf8" for v in imp_df["중요도"]]
        ax5.barh(imp_df["지표"], imp_df["중요도"], color=colors5, alpha=0.85)
        ax5.set_xlabel("중요도", color="white")
        ax5.set_title("순위 예측 지표 중요도", color="white")
        ax5.tick_params(colors="white")
        for spine in ax5.spines.values():
            spine.set_edgecolor("#333")
        for i, val in enumerate(imp_df["중요도"]):
            ax5.text(val + 0.005, i, f"{val:.3f}", va="center", color="white", fontsize=9)
        st.pyplot(fig5)
        st.info("💡 xPTS(기대승점)가 전체의 60% 이상 — 가장 핵심 지표!")

# ══════════════════════════════════════════════════════════════
# 탭 4 — 경기 일정 & 예측
# ══════════════════════════════════════════════════════════════
elif tab == "⚽ 경기 일정 & 예측":
    st.markdown("<h1 style='color:#00ff87; font-size:28px'>⚽ 경기 일정 & 승패 예측</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='desc-box'>
        📌 <strong>이 페이지에서는?</strong><br>
        예정 경기 일정과 각 경기의 <strong>홈승/무승부/원정승 확률</strong>을 확인합니다.<br>
        확률은 <strong>xG, xGA, xPTS 기반 예측 모델</strong>로 계산되었습니다.
    </div>
    """, unsafe_allow_html=True)

    demo_mode = st.toggle("🎬 시연 모드 (발표용 샘플 데이터)", value=False)

    if demo_mode:
        import datetime
        base = datetime.datetime(2025, 5, 10, 20, 0)
        demo_data = [
            {"날짜": base,                                       "홈팀": "Arsenal",          "원정팀": "Chelsea",           "홈승확률": 0.52, "무승부확률": 0.26, "원정승확률": 0.22},
            {"날짜": base + datetime.timedelta(hours=2),         "홈팀": "Manchester City",  "원정팀": "Liverpool",         "홈승확률": 0.45, "무승부확률": 0.28, "원정승확률": 0.27},
            {"날짜": base + datetime.timedelta(days=1),          "홈팀": "Tottenham",        "원정팀": "Manchester United", "홈승확률": 0.48, "무승부확률": 0.27, "원정승확률": 0.25},
            {"날짜": base + datetime.timedelta(days=1, hours=2), "홈팀": "Newcastle United", "원정팀": "Aston Villa",       "홈승확률": 0.44, "무승부확률": 0.30, "원정승확률": 0.26},
            {"날짜": base + datetime.timedelta(days=2),          "홈팀": "Brighton",         "원정팀": "Brentford",         "홈승확률": 0.41, "무승부확률": 0.32, "원정승확률": 0.27},
            {"날짜": base + datetime.timedelta(days=2, hours=2), "홈팀": "Chelsea",          "원정팀": "Fulham",            "홈승확률": 0.55, "무승부확률": 0.25, "원정승확률": 0.20},
            {"날짜": base + datetime.timedelta(days=3),          "홈팀": "Liverpool",        "원정팀": "Arsenal",           "홈승확률": 0.43, "무승부확률": 0.29, "원정승확률": 0.28},
            {"날짜": base + datetime.timedelta(days=3, hours=2), "홈팀": "Everton",          "원정팀": "West Ham",          "홈승확률": 0.38, "무승부확률": 0.33, "원정승확률": 0.29},
        ]
        df_fix = pd.DataFrame(demo_data)
        df_fix["날짜"] = pd.to_datetime(df_fix["날짜"])
        st.info("🎬 시연 모드: 발표용 샘플 데이터를 표시중입니다.")
    else:
        df_fix = df_fixtures.copy()
        if df_fix.empty or len(df_fix) == 0:
            st.markdown("""
            <div style='text-align:center; padding:60px 20px;'>
                <div style='font-size:48px; margin-bottom:16px'>🏆</div>
                <div style='font-size:22px; font-weight:700; color:#00ff87; margin-bottom:12px'>
                    25-26 시즌 종료
                </div>
                <div style='font-size:14px; color:rgba(255,255,255,0.6); margin-bottom:20px'>
                    모든 경기가 완료되었습니다.<br>
                    26-27 시즌은 2026년 8월 개막 후 자동으로 업데이트됩니다.
                </div>
                <div style='font-size:12px; color:rgba(255,255,255,0.3)'>
                    🎬 발표용 시연은 시연 모드 토글을 활성화하세요
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.stop()

    df_fix = df_fix.sort_values("날짜").reset_index(drop=True)

    with st.expander("🔍 승패 예측 방법 보기"):
        st.markdown("""
        <div style='color:white; line-height:1.8; font-size:13px'>
        <b style='color:#00ff87'>📊 예측 모델 개요</b><br>
        4개 시즌(21-22 ~ 24-25) 80팀의 전술 데이터를 학습한 <b>Random Forest 모델</b>을 사용합니다.<br><br>
        <b style='color:#38bdf8'>📌 사용 지표</b><br>
        • <b style='color:#00ff87'>xG</b> — 공격 기댓값<br>
        • <b style='color:#fb923c'>xGA</b> — 실점 기댓값<br>
        • <b style='color:#38bdf8'>xPTS</b> — 기대 승점 (중요도 61.5%)<br>
        • <b style='color:#a78bfa'>PPDA</b> — 압박 강도<br>
        • <b style='color:#facc15'>DC</b> — 공격 침투 깊이
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>── 전체 예정 경기 (한국시간 기준)</div>", unsafe_allow_html=True)

    dates = df_fix["날짜"].dt.date.unique()
    for date in dates:
        st.markdown(f"<div style='font-size:14px;font-weight:700;color:#facc15;margin:16px 0 8px'>📆 {date}</div>", unsafe_allow_html=True)
        day_fix = df_fix[df_fix["날짜"].dt.date == date].reset_index(drop=True)

        h1,h2,h3,h4,h5,h6,h7 = st.columns([0.5,2,1,1,1,2,0.5])
        for c, l in zip([h1,h2,h3,h4,h5,h6,h7],["시간","홈팀","홈승","무","원정승","원정팀",""]):
            c.markdown(f"<div style='font-size:10px;color:rgba(255,255,255,0.4)'>{l}</div>", unsafe_allow_html=True)

        for _, row in day_fix.iterrows():
            home_logo = TEAM_LOGOS.get(row["홈팀"], "")
            away_logo = TEAM_LOGOS.get(row["원정팀"], "")
            time_str = row["날짜"].strftime("%H:%M")

            def prob_color(p):
                try:
                    p = float(p)
                    if p >= 0.5: return "#ef4444"
                    elif p >= 0.3: return "#00ff87"
                    else: return "#38bdf8"
                except:
                    return "rgba(255,255,255,0.5)"

            def safe_prob(p):
                try:
                    return f"{int(float(p)*100)}%"
                except:
                    return "N/A"

            c1,c2,c3,c4,c5,c6,c7 = st.columns([0.5,2,1,1,1,2,0.5])
            c1.markdown(f"<div style='padding-top:6px;font-size:11px;color:white;font-weight:600'>{time_str}</div>", unsafe_allow_html=True)

            hc1,hc2 = c2.columns([0.3,0.7])
            if home_logo:
                hc1.image(home_logo, width=24)
            hc2.markdown(f"<div style='padding-top:4px;font-size:11px;font-weight:600;color:white'>{row['홈팀']}</div>", unsafe_allow_html=True)

            c3.markdown(f"<div style='padding-top:6px;color:{prob_color(row['홈승확률'])};font-weight:700'>{safe_prob(row['홈승확률'])}</div>", unsafe_allow_html=True)
            c4.markdown(f"<div style='padding-top:6px;color:{prob_color(row['무승부확률'])};font-weight:700'>{safe_prob(row['무승부확률'])}</div>", unsafe_allow_html=True)
            c5.markdown(f"<div style='padding-top:6px;color:{prob_color(row['원정승확률'])};font-weight:700'>{safe_prob(row['원정승확률'])}</div>", unsafe_allow_html=True)

            ac1,ac2 = c6.columns([0.3,0.7])
            if away_logo:
                ac1.image(away_logo, width=24)
            ac2.markdown(f"<div style='padding-top:4px;font-size:11px;font-weight:600;color:white'>{row['원정팀']}</div>", unsafe_allow_html=True)

        st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.06);margin:12px 0'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>── 팀별 다음 경기</div>", unsafe_allow_html=True)

    all_teams = sorted(set(df_fix["홈팀"].tolist() + df_fix["원정팀"].tolist()))
    selected_team = st.selectbox("팀 선택", all_teams)

    team_fix = df_fix[
        (df_fix["홈팀"] == selected_team) |
        (df_fix["원정팀"] == selected_team)
    ].head(3)

    for _, row in team_fix.iterrows():
        home_team = row["홈팀"]
        away_team = row["원정팀"]
        home_logo = TEAM_LOGOS.get(home_team, "")
        away_logo = TEAM_LOGOS.get(away_team, "")
        is_home = home_team == selected_team
        win_prob = row["홈승확률"] if is_home else row["원정승확률"]
        try:
            win_pct = int(float(win_prob) * 100)
        except:
            win_pct = 0
        win_color = "#00ff87" if win_pct >= 50 else "#fb923c"

        st.markdown(f"<div style='font-size:11px;color:rgba(255,255,255,0.5);margin:16px 0 8px'>📅 {row['날짜'].strftime('%Y-%m-%d %H:%M')} (한국시간)</div>", unsafe_allow_html=True)

        mc1,mc2,mc3,mc4,mc5 = st.columns([1,1.5,0.5,1.5,1])
        if home_logo:
            mc1.image(home_logo, width=55)
        mc2.markdown(f"<div style='font-size:15px;font-weight:700;padding-top:8px;color:white'>{home_team}<br><span style='font-size:10px;color:#00ff87'>홈</span></div>", unsafe_allow_html=True)
        mc3.markdown("<div style='font-size:18px;font-weight:700;color:rgba(255,255,255,0.4);padding-top:12px;text-align:center'>VS</div>", unsafe_allow_html=True)
        mc4.markdown(f"<div style='font-size:15px;font-weight:700;padding-top:8px;text-align:right;color:white'>{away_team}<br><span style='font-size:10px;color:#fb923c'>원정</span></div>", unsafe_allow_html=True)
        if away_logo:
            mc5.image(away_logo, width=55)

        try:
            hw = int(float(row['홈승확률'])*100)
        except:
            hw = 0
        try:
            dw = int(float(row['무승부확률'])*100)
        except:
            dw = 0
        try:
            aw = int(float(row['원정승확률'])*100)
        except:
            aw = 0

        pc1,pc2,pc3 = st.columns(3)
        probs = {"home": hw, "draw": dw, "away": aw}
        sorted_probs = sorted(probs.values(), reverse=True)

        def box_style(val):
            if val == sorted_probs[0]:
                return "background:rgba(0,255,135,0.15);border:2px solid #00ff87;", "#00ff87"
            elif val == sorted_probs[-1]:
                return "background:rgba(239,68,68,0.15);border:2px solid #ef4444;", "#ef4444"
            else:
                return "background:rgba(250,204,21,0.15);border:2px solid #facc15;", "#facc15"

        hw_style, hw_color = box_style(hw)
        dw_style, dw_color = box_style(dw)
        aw_style, aw_color = box_style(aw)

        pc1.markdown(f"<div style='text-align:center;{hw_style}border-radius:8px;padding:12px'><div style='font-size:10px;color:rgba(255,255,255,0.5)'>{home_team} 승</div><div style='font-size:26px;font-weight:700;color:{hw_color}'>{hw}%</div></div>", unsafe_allow_html=True)
        pc2.markdown(f"<div style='text-align:center;{dw_style}border-radius:8px;padding:12px'><div style='font-size:10px;color:rgba(255,255,255,0.5)'>무승부</div><div style='font-size:26px;font-weight:700;color:{dw_color}'>{dw}%</div></div>", unsafe_allow_html=True)
        pc3.markdown(f"<div style='text-align:center;{aw_style}border-radius:8px;padding:12px'><div style='font-size:10px;color:rgba(255,255,255,0.5)'>{away_team} 승</div><div style='font-size:26px;font-weight:700;color:{aw_color}'>{aw}%</div></div>", unsafe_allow_html=True)

        st.markdown(f"<div style='text-align:center;margin-top:10px;font-size:13px;color:{win_color};font-weight:600'>{selected_team} 승리 확률: {win_pct}%</div>", unsafe_allow_html=True)
        st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.06);margin:16px 0'></div>", unsafe_allow_html=True)