"""Streamlit UI rendering components for Persian news similarity comparison."""

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


def render_header(eitaa_channel: str = "", bale_channel: str = "") -> None:
    """Render modern hero header banner and architecture badges with channel names."""
    eitaa_name = config.get_channel_display_name(eitaa_channel) if eitaa_channel else "ایتا"
    bale_name = config.get_channel_display_name(bale_channel) if bale_channel else "بله"

    st.markdown(
        f"""
        <div class="app-hero-header">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                <div>
                    <h1>موتور تطبیق و تشابه‌سنجی اخبار فارسی</h1>
                    <p>استخراج برخط از کانال‌های ایتا و بله • پیش‌پردازش پیشرفته خط و زبان فارسی • تلفیق FAISS و TF-IDF</p>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                    <span class="platform-badge platform-eitaa">ایتا: {html.escape(eitaa_name)}</span>
                    <span class="platform-badge platform-bale">بله: {html.escape(bale_name)}</span>
                    <span style="background: rgba(255,255,255,0.15); color: #fff; padding: 5px 12px; border-radius: 9999px; font-size: 0.82rem;">BAAI/bge-m3</span>
                    <span style="background: rgba(255,255,255,0.15); color: #fff; padding: 5px 12px; border-radius: 9999px; font-size: 0.82rem;">FAISS FlatIP</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_scraped_posts_columns(
    eitaa_posts: List[str],
    bale_posts: List[str],
    eitaa_channel: str,
    bale_channel: str,
) -> None:
    """Render scraped posts in two distinct, aesthetically rich columns side-by-side.

    Args:
        eitaa_posts: List of texts scraped from Eitaa.
        bale_posts: List of texts scraped from Bale.
        eitaa_channel: Eitaa channel handle.
        bale_channel: Bale channel handle.
    """
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="column-header-box column-header-eitaa">
                <span style="display: flex; align-items: center; gap: 8px;">
                    <span>اخبار واکشی‌شده از ایتا</span>
                </span>
                <span class="platform-badge platform-eitaa">@{html.escape(eitaa_channel)} ({len(eitaa_posts)} پست)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for i, post in enumerate(eitaa_posts, 1):
            escaped_text = html.escape(post)
            words_count = len(post.split())
            chars_count = len(post)
            st.markdown(
                f"""
                <div class="post-feed-card">
                    <div class="post-card-top">
                        <span class="post-card-index">پست #{i}</span>
                        <span style="font-size: 0.78rem; color: #ea580c; font-weight: 700;">ایتا (@{html.escape(eitaa_channel)})</span>
                    </div>
                    <div class="post-card-text">{escaped_text}</div>
                    <div class="post-card-footer">
                        <span>📝 {words_count} کلمه</span>
                        <span>🔤 {chars_count} کاراکتر</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            f"""
            <div class="column-header-box column-header-bale">
                <span style="display: flex; align-items: center; gap: 8px;">
                    <span>اخبار واکشی‌شده از بله</span>
                </span>
                <span class="platform-badge platform-bale">@{html.escape(bale_channel)} ({len(bale_posts)} پست)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for i, post in enumerate(bale_posts, 1):
            escaped_text = html.escape(post)
            words_count = len(post.split())
            chars_count = len(post)
            st.markdown(
                f"""
                <div class="post-feed-card">
                    <div class="post-card-top">
                        <span class="post-card-index">پست #{i}</span>
                        <span style="font-size: 0.78rem; color: #059669; font-weight: 700;">بله (@{html.escape(bale_channel)})</span>
                    </div>
                    <div class="post-card-text">{escaped_text}</div>
                    <div class="post-card-footer">
                        <span>📝 {words_count} کلمه</span>
                        <span>🔤 {chars_count} کاراکتر</span>
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
            <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 6px;">مدل زبانی BAAI/bge-m3 + نگاشت کسینوسی FAISS FlatIP</div>
            <span class="score-badge {sem_badge_class}">{sem_label}</span>
        </div>
        <div class="similarity-metric-card metric-lexical">
            <div class="metric-score-title">تشابه واژگانی سطحی (Lexical TF-IDF Similarity)</div>
            <div class="metric-score-value">{lex_pct}%</div>
            <div style="font-size: 0.85rem; color: #cbd5e1; margin-bottom: 6px;">ماتریس فراوانی توکن‌ها + تشابه کسینوسی Scikit-Learn</div>
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
    """Render side-by-side view of selected raw texts from both platforms.

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
        <div class="comparison-card">
            <div class="comparison-card-header">
                <span style="font-weight: 800; font-size: 1.05rem; color: #9a3412;">خبر انتخابی از ایتا</span>
                <span class="platform-badge platform-eitaa">@{html.escape(eitaa_channel)}</span>
            </div>
            <div class="comparison-card-body">{escaped_eitaa}</div>
            <div style="margin-top: 1rem; font-size: 0.82rem; color: #64748b; display: flex; gap: 14px;">
                <span>تعداد کاراکتر: {len(eitaa_text):,}</span>
                <span>تعداد کلمات: {len(eitaa_text.split()):,}</span>
            </div>
        </div>
        """
        st.markdown(eitaa_card, unsafe_allow_html=True)

    with col2:
        escaped_bale = html.escape(bale_text)
        bale_card = f"""
        <div class="comparison-card">
            <div class="comparison-card-header">
                <span style="font-weight: 800; font-size: 1.05rem; color: #065f46;">خبر مقایسه‌ای از بله</span>
                <span class="platform-badge platform-bale">@{html.escape(bale_channel)}</span>
            </div>
            <div class="comparison-card-body">{escaped_bale}</div>
            <div style="margin-top: 1rem; font-size: 0.82rem; color: #64748b; display: flex; gap: 14px;">
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
    """Render detailed step-by-step cleaned NLP pipeline stages.

    Args:
        stages_eitaa: Tuple of (raw, normalized, cleaned, filtered) for Eitaa post.
        stages_bale: Tuple of (raw, normalized, cleaned, filtered) for Bale post.
    """
    stage_names = [
        ("۱. متن اولیه (Raw Text)", "متن واکشی شده از بستر پیام‌رسان", "📥"),
        ("۲. نرمال‌سازی نویسه‌ها (Persian Normalizer)", "اصلاح ی/ك عربی، اعراب‌زدایی، حذف کشیدگی و یکپارچه‌سازی نیم‌فاصله (ZWNJ)", "✨"),
        ("۳. پاک‌سازی کاراکترها و نشانه‌ها (Text Cleaner)", "حذف نشانی وب، شناسه‌ها (@)، ارقام، ایموجی‌ها و علائم نگارشی", "🧹"),
        ("۴. پالایش کلمات توقف (Stopwords Filtered)", "حذف بیش از ۱۲۰ کلمه ایستای فارسی و واژگان کم‌ارزش معنایی", "🎯"),
    ]

    for i, (title, desc, icon) in enumerate(stage_names):
        text_eitaa = html.escape(stages_eitaa[i]) if stages_eitaa[i] else "(بدون محتوا)"
        text_bale = html.escape(stages_bale[i]) if stages_bale[i] else "(بدون محتوا)"

        stage_html = f"""
        <div class="nlp-stage-card">
            <div class="nlp-stage-title">
                <span>{icon}</span>
                <span>{html.escape(title)}</span>
            </div>
            <div class="nlp-stage-desc">
                {html.escape(desc)}
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
                <div>
                    <div class="nlp-box-label nlp-label-eitaa">ایتا</div>
                    <div class="nlp-text-box nlp-text-box-eitaa">{text_eitaa}</div>
                </div>
                <div>
                    <div class="nlp-box-label nlp-label-bale">بله</div>
                    <div class="nlp-text-box nlp-text-box-bale">{text_bale}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(stage_html, unsafe_allow_html=True)




def render_ranking_list(
    bale_posts: List[str],
    rankings: List[Tuple[int, float]],
    bale_channel: str,
) -> None:
    """Render ranked list of candidate posts sorted by similarity score.

    Args:
        bale_posts: Full list of Bale posts.
        rankings: List of (index, similarity_score).
        bale_channel: Bale channel handle.
    """
    st.markdown("### 📊 رتبه‌بندی تشابه تمامی پست‌های بله با خبر انتخابی ایتا")
    for rank, (idx, score) in enumerate(rankings, start=1):
        post_snippet = bale_posts[idx]
        preview = post_snippet[:140] + ("..." if len(post_snippet) > 140 else "")
        score_pct = round(score * 100, 1)
        label, badge_class = get_similarity_classification(score)

        st.markdown(
            f"""
            <div class="ranking-row">
                <div style="flex: 1;">
                    <div style="font-weight: 800; font-size: 0.96rem; margin-bottom: 4px; color: #1e293b;">
                        رتبه {rank}: پست #{idx + 1} از @{html.escape(bale_channel)}
                    </div>
                    <div style="font-size: 0.88rem; color: #475569; line-height: 1.7;">{html.escape(preview)}</div>
                </div>
                <div style="text-align: left; min-width: 140px;">
                    <span style="font-size: 1.35rem; font-weight: 900; color: #312e81;">{score_pct}%</span>
                    <br/>
                    <span class="score-badge {badge_class}" style="font-size: 0.74rem; padding: 2px 10px;">{label}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
