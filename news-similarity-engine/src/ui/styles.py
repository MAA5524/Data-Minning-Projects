"""Custom CSS styles, Vazirmatn typography, and RTL layout configurations for Streamlit UI."""

def get_custom_css() -> str:
    """Return custom CSS string for injection into Streamlit app."""
    return """
    <style>
    /* Robust Vazirmatn & Material Icons font loading */
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* Global Persian Typography & RTL Direction */
    html, body, .stApp, .stMarkdown, .stSelectbox, .stTextInput, .stButton,
    .stTabs, div.stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input, button, select, textarea {
        font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Tahoma, sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* CRITICAL FIX: Protect Google Material Icons from being overridden by Persian font */
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"] *,
    [class*="material-symbols"],
    [class*="material-icons"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        direction: ltr !important;
        display: inline-block !important;
        vertical-align: middle !important;
        font-style: normal !important;
        font-weight: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
    }

    /* Container RTL adjustments */
    .block-container {
        direction: rtl;
        text-align: right;
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        max-width: 1350px;
    }

    /* Streamlit Sidebar RTL styling & modern dark design */
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        border-left: 1px solid rgba(255, 255, 255, 0.08);
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
    }
    [data-testid="stSidebar"] * {
        text-align: right;
    }
    [data-testid="stSidebar"] .stSelectbox > div {
        border-radius: 10px;
    }

    /* CRITICAL FIX: Streamlit Slider Direction */
    [data-testid="stSlider"] {
        direction: ltr !important;
    }
    [data-testid="stSlider"] [data-testid="stWidgetLabel"],
    [data-testid="stSlider"] label {
        direction: rtl !important;
        text-align: right !important;
    }
    [data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
        direction: rtl !important;
        text-align: right !important;
    }

    /* Modern App Hero Banner */
    .app-hero-header {
        background: radial-gradient(circle at top right, #3730a3 0%, #1e1b4b 60%, #0f172a 100%);
        color: #ffffff;
        padding: 2.2rem 2.4rem;
        border-radius: 24px;
        box-shadow: 0 16px 36px -10px rgba(30, 27, 75, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .app-hero-header::after {
        content: "";
        position: absolute;
        top: -60px;
        left: -60px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.35) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .app-hero-header h1 {
        font-weight: 900;
        font-size: 2.15rem;
        margin: 0 0 0.6rem 0;
        color: #ffffff;
        letter-spacing: -0.5px;
        line-height: 1.3;
    }
    .app-hero-header p {
        font-size: 1.05rem;
        color: #cbd5e1;
        margin: 0;
        line-height: 1.7;
        font-weight: 400;
    }

    /* Platform Badge Pills */
    .platform-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.2px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    .platform-eitaa {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 50%, #c2410c 100%);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .platform-bale {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Column Container Titles */
    .column-header-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.9rem 1.2rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
        font-weight: 700;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
    .column-header-eitaa {
        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
        border: 1px solid #fed7aa;
        color: #9a3412;
    }
    .column-header-bale {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 1px solid #a7f3d0;
        color: #065f46;
    }

    /* News Post Feed Cards */
    .post-feed-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        transition: all 0.22s ease-in-out;
        position: relative;
    }
    .post-feed-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
        border-color: #cbd5e1;
    }
    .post-feed-card.selected-post-eitaa {
        border: 2px solid #ea580c;
        background: #fffaf5;
    }
    .post-feed-card.selected-post-bale {
        border: 2px solid #059669;
        background: #f0fdf4;
    }
    .post-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px dashed #e2e8f0;
    }
    .post-card-index {
        font-size: 0.85rem;
        font-weight: 800;
        color: #64748b;
        background: #f1f5f9;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .post-card-text {
        font-size: 0.95rem;
        line-height: 1.85;
        color: #1e293b;
        word-break: break-word;
        white-space: pre-wrap;
    }
    .post-card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.85rem;
        padding-top: 0.5rem;
        font-size: 0.8rem;
        color: #94a3b8;
    }

    /* Similarity Metric Cards */
    .metric-card-wrapper {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.4rem;
        margin: 1.5rem 0;
    }
    @media (max-width: 768px) {
        .metric-card-wrapper {
            grid-template-columns: 1fr;
        }
    }
    .similarity-metric-card {
        border-radius: 20px;
        padding: 1.8rem 1.6rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
        transition: transform 0.2s ease;
    }
    .similarity-metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-semantic {
        background: linear-gradient(135deg, #1e1b4b 0%, #3730a3 50%, #4338ca 100%);
        color: #ffffff;
    }
    .metric-lexical {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        color: #ffffff;
    }
    .metric-score-value {
        font-size: 3.2rem;
        font-weight: 900;
        margin: 0.3rem 0;
        line-height: 1.1;
        letter-spacing: -1px;
    }
    .metric-score-title {
        font-size: 1rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 4px;
    }

    /* Score Badges */
    .score-badge {
        display: inline-block;
        padding: 0.45rem 1.2rem;
        border-radius: 9999px;
        font-size: 0.88rem;
        font-weight: 800;
        margin-top: 0.7rem;
    }
    .score-badge-high {
        background-color: rgba(16, 185, 129, 0.22);
        color: #34d399;
        border: 1px solid #10b981;
    }
    .score-badge-moderate {
        background-color: rgba(245, 158, 11, 0.22);
        color: #fbbf24;
        border: 1px solid #f59e0b;
    }
    .score-badge-low {
        background-color: rgba(239, 68, 68, 0.22);
        color: #f87171;
        border: 1px solid #ef4444;
    }

    /* Comparison Box */
    .comparison-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
    .comparison-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 0.75rem;
        margin-bottom: 0.9rem;
    }
    .comparison-card-body {
        font-size: 0.98rem;
        line-height: 1.9;
        color: #1e293b;
        white-space: pre-wrap;
        word-break: break-word;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 700;
        font-size: 1rem;
        padding: 10px 20px;
        border-radius: 10px 10px 0 0;
    }

    /* Streamlit Button Beautification */
    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        padding: 0.55rem 1.2rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    /* Ranking Rows */
    .ranking-row {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        transition: all 0.2s ease;
    }
    .ranking-row:hover {
        border-color: #6366f1;
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.08);
        transform: translateX(-3px);
    }

    /* NLP Pipeline Stages Cards & Persian Text Box */
    .nlp-stage-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    }
    .nlp-stage-title {
        font-weight: 800;
        font-size: 1.05rem;
        color: #38bdf8 !important; /* Bright cyan/blue visible on dark background */
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }
    .nlp-stage-desc {
        font-size: 0.9rem;
        color: #e2e8f0 !important; /* Bright crisp text, perfectly readable */
        line-height: 1.7;
        margin-bottom: 12px;
    }
    .nlp-text-box {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        font-family: 'Vazirmatn', -apple-system, sans-serif !important;
        font-size: 0.94rem;
        line-height: 1.9;
        color: #f8fafc !important;
        word-break: break-word;
        white-space: pre-wrap;
        direction: rtl;
        text-align: right;
        min-height: 80px;
    }
    .nlp-text-box-eitaa {
        border-right: 4px solid #f97316;
    }
    .nlp-text-box-bale {
        border-right: 4px solid #10b981;
    }
    .nlp-box-label {
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .nlp-label-eitaa {
        color: #fb923c !important;
    }
    .nlp-label-bale {
        color: #34d399 !important;
    }
    </style>
    """
