"""Streamlit UI rendering components for news similarity comparison."""

from typing import List, Tuple
import html
import streamlit as st
import config


def get_similarity_classification(score: float) -> Tuple[str, str]:
    """Return Persian label and CSS class for a given similarity score (0.0 to 1.0).

    Args:
        score: Similarity value between 0.0 and 1.0.

    Returns:
        Tuple of (persian_label, css_badge_class).
    """
    if score >= config.SIMILARITY_HIGH_THRESHOLD:
        return "تطابق معنایی بالا (High)", "score-badge-high"
    elif score >= config.SIMILARITY_MODERATE_THRESHOLD:
        return "تطابق معنایی متوسط (Moderate)", "score-badge-moderate"
    else:
        return "تطابق معنایی ضعیف (Low)", "score-badge-low"


def render_header() -> None:
    """Render the main application banner and architecture badges."""
    st.markdown(
        """
        <div class="app-header-box">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h1>موتور تطبیق و تشابه‌سنجی اخبار فارسی</h1>
                    <p>پایش برخط کانال‌های ایتا و بله، پیش‌پردازش تخصصی متن فارسی، و تلفیق FAISS با TF-IDF</p>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span class="platform-badge platform-eitaa">پیام‌رسان ایتا</span>
                    <span class="platform-badge platform-bale">پیام‌رسان بله</span>
                    <span style="background: rgba(255,255,255,0.15); color: #fff; padding: 4px 12px; border-radius: 9999px; font-size: 0.82rem;">BAAI/bge-m3</span>
                    <span style="background: rgba(255,255,255,0.15); color: #fff; padding: 4px 12px; border-radius: 9999px; font-size: 0.82rem;">FAISS FlatIP</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_similarity_cards(semantic_score: float, lexical_score: float) -> None:
    """Render visual score cards displaying both Semantic and Lexical similarity percentages.

    Args:
        semantic_score: Semantic cosine similarity float (0.0 to 1.0).
        lexical_score: Lexical TF-IDF cosine similarity float (0.0 to 1.0).
    """
    sem_pct = round(semantic_score * 100, 1)
    lex_pct = round(lexical_score * 100, 1)

    sem_label, sem_badge_class = get_similarity_classification(semantic_score)
    lex_label, lex_badge_class = get_similarity_classification(lexical_score)

    card_html = f"""
    <div class="metric-card-wrapper">
        <div class="similarity-metric-card metric-semantic">
            <div class="metric-score-title">تشابه معنایی عمیق (Dense Semantic Similarity)</div>
            <div class="metric-score-value">{sem_pct}%</div>
            <div style="font-size: 0.82rem; color: #cbd5e1; margin-bottom: 4px;">مدل برداری BAAI/bge-m3 + نگاشت کسینوسی FAISS</div>
            <span class="score-badge {sem_badge_class}">{sem_label}</span>
        </div>
        <div class="similarity-metric-card metric-lexical">
            <div class="metric-score-title">تشابه واژگانی سطحی (Lexical TF-IDF Similarity)</div>
            <div class="metric-score-value">{lex_pct}%</div>
            <div style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 4px;">وزن‌دهی آماری توکن‌ها + تشابه کسینوسی Scikit-Learn</div>
            <span class="score-badge {lex_badge_class}">{lex_label}</span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_side_by_side_comparison(
    eitaa_text: str,
    bale_text: str,
    eitaa_channel: str,
    bale_channel: str,
) -> None:
    """Render side-by-side view of raw texts from both platforms.

    Args:
        eitaa_text: Raw news text from Eitaa.
        bale_text: Raw news text from Bale.
        eitaa_channel: Eitaa channel name.
        bale_channel: Bale channel name.
    """
    col1, col2 = st.columns(2)

    with col1:
        escaped_eitaa = html.escape(eitaa_text)
        eitaa_card = f"""
        <div class="news-card">
            <div class="news-card-header">
                <span class="news-card-title">خبر انتخابی از ایتا</span>
                <span class="platform-badge platform-eitaa">@{html.escape(eitaa_channel)}</span>
            </div>
            <div class="news-card-body">{escaped_eitaa}</div>
            <div class="news-card-meta">
                <span>تعداد کاراکتر: {len(eitaa_text):,}</span>
                <span>تعداد کلمات: {len(eitaa_text.split()):,}</span>
            </div>
        </div>
        """
        st.markdown(eitaa_card, unsafe_allow_html=True)

    with col2:
        escaped_bale = html.escape(bale_text)
        bale_card = f"""
        <div class="news-card">
            <div class="news-card-header">
                <span class="news-card-title">خبر مقایسه‌ای از بله</span>
                <span class="platform-badge platform-bale">@{html.escape(bale_channel)}</span>
            </div>
            <div class="news-card-body">{escaped_bale}</div>
            <div class="news-card-meta">
                <span>تعداد کاراکتر: {len(bale_text):,}</span>
                <span>تعداد کلمات: {len(bale_text.split()):,}</span>
            </div>
        </div>
        """
        st.markdown(bale_card, unsafe_allow_html=True)


def render_nlp_pipeline_stages(
    stages_eitaa: Tuple[str, str, str, str],
    stages_bale: Tuple[str, str, str, str],
) -> None:
    """Render accordion expander showing step-by-step cleaned NLP text.

    Args:
        stages_eitaa: Tuple of (raw, normalized, cleaned, filtered) for Eitaa post.
        stages_bale: Tuple of (raw, normalized, cleaned, filtered) for Bale post.
    """
    with st.expander("🔍 مشاهده مراحل گام‌به‌گام خط‌لوله پیش‌پردازش متن (NLP Pipeline Breakdown)", expanded=False):
        stage_names = [
            ("۱. متن اولیه (Raw Text)", "متن دست‌نخورده واکشی شده از وب"),
            ("۲. نرمال‌سازی نویسه‌ها (Persian Normalizer)", "تبدیل ی/ك/ة عربی به فارسی، حذف اعراب و تشدید، یکپارچه‌سازی نیم‌فاصله"),
            ("۳. پاک‌سازی کاراکترها و نشانه‌ها (Text Cleaner)", "حذف نشانی‌های اینترنتی، منشن‌ها، اعداد، ایموجی‌ها و علائم نگارشی"),
            ("۴. پالایش کلمات توقف (Stopwords Filtered)", "حذف بیش از ۱۲۰ کلمه ایستای فارسی و تک‌حرف‌های بدون ارزش معنایی"),
        ]

        for i, (title, desc) in enumerate(stage_names):
            st.markdown(f"**{title}** — *{desc}*")
            c1, c2 = st.columns(2)
            with c1:
                st.caption("🔹 ایتا:")
                st.code(stages_eitaa[i] if stages_eitaa[i] else "(بدون محتوا)", language=None)
            with c2:
                st.caption("🔸 بله:")
                st.code(stages_bale[i] if stages_bale[i] else "(بدون محتوا)", language=None)
            st.markdown("---")


def render_ranking_list(
    bale_posts: List[str],
    rankings: List[Tuple[int, float]],
    bale_channel: str,
) -> None:
    """Render ranked list of candidate posts sorted by similarity.

    Args:
        bale_posts: Full list of Bale posts.
        rankings: List of (index, similarity_score).
        bale_channel: Bale channel handle.
    """
    st.markdown("### 📊 رتبه‌بندی تشابه تمامی پست‌های واکشی‌شده از بله")
    for rank, (idx, score) in enumerate(rankings, start=1):
        post_snippet = bale_posts[idx]
        preview = post_snippet[:150] + ("..." if len(post_snippet) > 150 else "")
        score_pct = round(score * 100, 1)
        label, badge_class = get_similarity_classification(score)

        st.markdown(
            f"""
            <div class="ranking-row">
                <div style="flex: 1; padding-left: 15px;">
                    <div style="font-weight: 600; font-size: 0.95rem; margin-bottom: 4px;">
                        رتبه {rank}: پست #{idx + 1} از @{html.escape(bale_channel)}
                    </div>
                    <div style="font-size: 0.88rem; color: #475569;">{html.escape(preview)}</div>
                </div>
                <div style="text-align: left; min-width: 140px;">
                    <span style="font-size: 1.25rem; font-weight: 800;">{score_pct}%</span>
                    <br/>
                    <span class="score-badge {badge_class}" style="font-size: 0.75rem; padding: 2px 8px;">{label}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
