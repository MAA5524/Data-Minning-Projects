"""Custom CSS styles and RTL layout configurations for Streamlit UI."""

def get_custom_css() -> str:
    """Return custom CSS string for injection into Streamlit app."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap');

    /* Global Typography & Direction */
    html, body, [class*="css"], .stMarkdown, .stSelectbox, .stTextInput, .stButton {
        font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* Container RTL adjustments */
    .block-container {
        direction: rtl;
        text-align: right;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* App Header Banner */
    .app-header-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        color: #ffffff;
        padding: 2.2rem 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.4), 0 8px 10px -6px rgba(49, 46, 129, 0.2);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .app-header-box h1 {
        font-weight: 800;
        font-size: 2.1rem;
        margin: 0 0 0.5rem 0;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .app-header-box p {
        font-size: 1.05rem;
        color: #cbd5e1;
        margin: 0;
        line-height: 1.6;
    }

    /* Platform Badge Pills */
    .platform-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .platform-eitaa {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(234, 88, 12, 0.35);
    }
    .platform-bale {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(5, 150, 105, 0.35);
    }

    /* News Content Cards */
    .news-card {
        background-color: var(--background-secondary, #f8fafc);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.07);
    }
    .news-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
    }
    .news-card-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: var(--text-color, #1e293b);
    }
    .news-card-body {
        font-size: 0.98rem;
        line-height: 1.85;
        color: var(--text-color, #334155);
        white-space: pre-wrap;
        word-break: break-word;
    }
    .news-card-meta {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 1rem;
        display: flex;
        gap: 12px;
    }

    /* Similarity Metric Cards */
    .metric-card-wrapper {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    .similarity-metric-card {
        border-radius: 18px;
        padding: 1.6rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }
    .metric-semantic {
        background: linear-gradient(135deg, #1e1b4b 0%, #3730a3 100%);
        color: #ffffff;
    }
    .metric-lexical {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
    }
    .metric-score-value {
        font-size: 2.8rem;
        font-weight: 900;
        margin: 0.4rem 0;
        line-height: 1;
        letter-spacing: -1px;
    }
    .metric-score-title {
        font-size: 0.95rem;
        font-weight: 500;
        color: #94a3b8;
    }

    /* Score Badges */
    .score-badge {
        display: inline-block;
        padding: 0.4rem 1.1rem;
        border-radius: 9999px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-top: 0.6rem;
    }
    .score-badge-high {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
    }
    .score-badge-moderate {
        background-color: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid #f59e0b;
    }
    .score-badge-low {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
    }

    /* NLP Pipeline Stages Box */
    .nlp-stage-container {
        background-color: var(--background-secondary, #f8fafc);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.9rem;
    }
    .nlp-stage-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
        font-size: 0.92rem;
        color: #475569;
        margin-bottom: 0.5rem;
    }
    .nlp-stage-text {
        font-family: 'Vazirmatn', monospace;
        font-size: 0.92rem;
        color: var(--text-color, #1e293b);
        background: rgba(0, 0, 0, 0.03);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        line-height: 1.7;
    }

    /* Ranking Table Styling */
    .ranking-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        transition: background-color 0.15s ease;
    }
    .ranking-row:hover {
        background-color: rgba(99, 102, 241, 0.06);
    }
    </style>
    """
