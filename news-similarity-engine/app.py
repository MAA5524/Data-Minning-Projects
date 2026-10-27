"""Persian News Similarity Engine - Streamlit Web Application.

Fetches public posts from Eitaa and Bale, preprocesses Persian text, and
computes both Lexical (TF-IDF) and Semantic (FAISS + BAAI/bge-m3) similarity.
"""

import asyncio
import sys
from typing import List, Optional, Tuple
import streamlit as st
from streamlit import runtime

# If executed directly via 'python app.py', automatically launch using Streamlit runner
if not runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", sys.argv[0]] + sys.argv[1:]
    sys.exit(stcli.main())

import config
from src.nlp import PersianNLPPipeline
from src.scrapers import BaleScraper, ChannelNotFoundError, EitaaScraper, RateLimitError, ScraperError
from src.similarity import FaissSimilarityEngine, LexicalSimilarityEngine
from src.ui import (
    get_custom_css,
    render_header,
    render_nlp_pipeline_stages,
    render_ranking_list,
    render_scraped_posts_columns,
    render_side_by_side_comparison,
    render_similarity_cards,
)


# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Cached Singletons
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="موتور تشابه‌سنجی اخبار فارسی | ایتا و بله",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS styles for RTL layout, Vazirmatn font, and card aesthetics
st.markdown(get_custom_css(), unsafe_allow_html=True)


@st.cache_resource(show_spinner="در حال بارگذاری مدل زبانی و برداری BAAI/bge-m3...")
def get_faiss_engine() -> FaissSimilarityEngine:
    """Instantiate and cache the dense FAISS semantic similarity engine."""
    return FaissSimilarityEngine(model_name=config.EMBEDDING_MODEL_NAME)


@st.cache_resource
def get_lexical_engine() -> LexicalSimilarityEngine:
    """Instantiate and cache the lexical TF-IDF similarity engine."""
    return LexicalSimilarityEngine()


@st.cache_resource
def get_nlp_pipeline() -> PersianNLPPipeline:
    """Instantiate and cache the Persian NLP cleaning and normalization pipeline."""
    return PersianNLPPipeline()


# -----------------------------------------------------------------------------
# Asynchronous Scraping Helper
# -----------------------------------------------------------------------------
async def scrape_channels(
    eitaa_channel: str,
    bale_channel: str,
    limit: int = 10,
) -> Tuple[List[str], List[str]]:
    """Fetch latest posts concurrently from public web pages of Eitaa and Bale.

    Args:
        eitaa_channel: Channel ID for Eitaa.
        bale_channel: Channel ID for Bale.
        limit: Maximum posts per platform.

    Returns:
        Tuple of (eitaa_posts, bale_posts).
    """
    eitaa_scraper = EitaaScraper()
    bale_scraper = BaleScraper()

    # Concurrent execution using asyncio.gather
    eitaa_task = eitaa_scraper.fetch_posts(eitaa_channel, limit=limit)
    bale_task = bale_scraper.fetch_posts(bale_channel, limit=limit)

    eitaa_results, bale_results = await asyncio.gather(
        eitaa_task, bale_task, return_exceptions=True
    )

    eitaa_posts: List[str] = []
    bale_posts: List[str] = []

    if isinstance(eitaa_results, Exception):
        st.warning(f"⚠️ هشدار در استخراج ایتا (@{eitaa_channel}): {eitaa_results}")
    else:
        eitaa_posts = eitaa_results

    if isinstance(bale_results, Exception):
        st.warning(f"⚠️ هشدار در استخراج بله (@{bale_channel}): {bale_results}")
    else:
        bale_posts = bale_results

    return eitaa_posts, bale_posts


# Fallback sample dataset for demonstration and offline testing
SAMPLE_EITAA_POSTS = [
    (
        "بانک مرکزی در بخشنامه‌ای ضوابط جدید انتشار و فروش اوراق گواهی سپرده خاص "
        "با نرخ سود علی‌الحساب ۳۰ درصد را به شبکه بانکی ابلاغ کرد. هدف از این اقدام "
        "مهار انتظارات تورمی و هدایت منابع به بخش تولید است."
    ),
    (
        "سازمان هواشناسی کشور از ورود سامانه بارشی جدید به غرب و شمال غرب کشور "
        "خبر داد و نسبت به لغزندگی جاده‌ها و آب‌گرفتگی معابر در ۱۰ استان هشدار سطح نارنجی صادر کرد."
    ),
    (
        "تیم ملی فوتبال ایران در مرحله نیمه‌نهایی جام ملت‌های آسیا با ارائه یک بازی هجومی "
        "موفق شد به فینال رقابت‌ها راه پیدا کند و تحسین هواداران را برانگیزد."
    ),
]

SAMPLE_BALE_POSTS = [
    (
        "بر اساس بخشنامه جدید بانک مرکزی، اوراق گواهی سپرده مدت‌دار با سود علی‌الحساب ۳۰ درصد "
        "با هدف مهار تورم و تأمین مالی پروژه‌های پیشران و تولیدی از امروز در تمامی شعب عرضه می‌شود."
    ),
    (
        "هشدار نارنجی سازمان هواشناسی: نفوذ سامانه بارشی پرقدرت به مناطق شمال غربی و غربی کشور؛ "
        "مسافران از سفرهای غیرضروری و تردد در حاشیه رودخانه‌ها اکیداً خودداری نمایند."
    ),
    (
        "شاخص کل بورس اوراق بهادار تهران در پایان معاملات امروز با رشد ۱۰ هزار واحدی "
        "به تراز ۲ میلیون و ۱۵۰ هزار واحد رسید و نمادهای فلزی بیشترین تقاضا را ثبت کردند."
    ),
]


# -----------------------------------------------------------------------------
# Main Application Flow
# -----------------------------------------------------------------------------
def main() -> None:
    """Render and orchestrate the Streamlit application."""
    # Initialize session state store for scraped posts
    if "eitaa_posts" not in st.session_state:
        st.session_state["eitaa_posts"] = []
    if "bale_posts" not in st.session_state:
        st.session_state["bale_posts"] = []
    if "eitaa_channel_name" not in st.session_state:
        st.session_state["eitaa_channel_name"] = config.DEFAULT_EITAA_CHANNEL
    if "bale_channel_name" not in st.session_state:
        st.session_state["bale_channel_name"] = config.DEFAULT_BALE_CHANNEL
    if "selected_eitaa_idx" not in st.session_state:
        st.session_state["selected_eitaa_idx"] = 0
    if "selected_bale_idx" not in st.session_state:
        st.session_state["selected_bale_idx"] = 0

    render_header(
        eitaa_channel=st.session_state.get("eitaa_channel_name", ""),
        bale_channel=st.session_state.get("bale_channel_name", ""),
    )

    # Load processing engines
    faiss_engine = get_faiss_engine()
    lexical_engine = get_lexical_engine()
    nlp_pipeline = get_nlp_pipeline()

    # Pre-defined Iranian news channel sources
    CHANNEL_PRESETS = [
        ("farsna", "خبرگزاری فارس (farsna)"),
        ("tasnimnews", "خبرگزاری تسنیم (tasnimnews)"),
        ("iribnews", "خبرگزاری صدا و سیما (iribnews)"),
        ("akharinkhabar", "آخرین خبر (akharinkhabar)"),
        ("mehrnews", "خبرگزاری مهر (mehrnews)"),
        ("isna", "خبرگزاری ایسنا (isna)"),
        ("irnanews", "خبرگزاری ایرنا (irnanews)"),
        ("custom", "کانال دیگر (ورود دستی شناسه)"),
    ]
    preset_keys = [k for k, _ in CHANNEL_PRESETS]

    # -------------------------------------------------------------------------
    # Sidebar: Channels configuration and controls
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### ⚙️ تنظیمات استخراج و کانال‌ها")

        st.markdown("**کانال ایتا (Eitaa):**")
        curr_eitaa = st.session_state.get("eitaa_channel_name", config.DEFAULT_EITAA_CHANNEL)
        default_eitaa_idx = preset_keys.index(curr_eitaa) if curr_eitaa in preset_keys else len(preset_keys) - 1

        selected_eitaa_preset = st.selectbox(
            "انتخاب کانال ایتا",
            options=preset_keys,
            index=default_eitaa_idx,
            format_func=lambda k: next(label for key, label in CHANNEL_PRESETS if key == k),
            key="eitaa_select_widget",
        )

        if selected_eitaa_preset == "custom":
            eitaa_final_channel = st.text_input(
                "شناسه کانال ایتا",
                value=curr_eitaa if curr_eitaa not in preset_keys else "",
                placeholder="مثال: farsna (بدون @)",
                help="شناسه کانال عمومی بدون @ یا لینک کامل",
            ).strip().lstrip("@")
        else:
            eitaa_final_channel = selected_eitaa_preset

        st.markdown("**کانال بله (Bale):**")
        curr_bale = st.session_state.get("bale_channel_name", config.DEFAULT_BALE_CHANNEL)
        default_bale_idx = preset_keys.index(curr_bale) if curr_bale in preset_keys else len(preset_keys) - 1

        selected_bale_preset = st.selectbox(
            "انتخاب کانال بله",
            options=preset_keys,
            index=default_bale_idx,
            format_func=lambda k: next(label for key, label in CHANNEL_PRESETS if key == k),
            key="bale_select_widget",
        )

        if selected_bale_preset == "custom":
            bale_final_channel = st.text_input(
                "شناسه کانال بله",
                value=curr_bale if curr_bale not in preset_keys else "",
                placeholder="مثال: iribnews (بدون @)",
                help="شناسه کانال عمومی بدون @ یا لینک کامل",
            ).strip().lstrip("@")
        else:
            bale_final_channel = selected_bale_preset

        st.markdown("**🔢 تعداد پست‌های واکشی:**")
        posts_limit = st.slider(
            "تعداد پست‌های دریافتی:",
            min_value=3,
            max_value=25,
            value=8,
            step=1,
            help="حداقل ۳ و حداکثر ۲۵ پست جهت استخراج",
        )

        st.markdown("---")
        fetch_col, sample_col = st.columns(2)

        with fetch_col:
            fetch_button = st.button("واکشی آنلاین", use_container_width=True, type="primary")

        with sample_col:
            load_sample_button = st.button("داده نمونه", use_container_width=True)

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.7; background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08);">
            💡 <b>روش کار:</b><br/>
            ۱. پیام‌های کانال‌های انتخابی به‌صورت ناهمگام (Async) دریافت می‌شوند.<br/>
            ۲. متن‌ها تحت نرمال‌سازی اختصاصی فارسی، اعراب‌زدایی و پالایش کلمات توقف قرار می‌گیرند.<br/>
            ۳. بردارهای متراکم با BAAI/bge-m3 استخراج و در نمایه‌ساز FAISS برای کشف شباهت معنایی جستجو می‌شوند.<br/>
            ۴. ماتریس واژگانی TF-IDF تطابق مستقیم واژگان را ارزیابی می‌کند.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # Actions: Fetch or Load Data
    # -------------------------------------------------------------------------
    if fetch_button:
        clean_eitaa = eitaa_final_channel.strip().lstrip("@")
        clean_bale = bale_final_channel.strip().lstrip("@")

        if not clean_eitaa or not clean_bale:
            st.error("⚠️ لطفاً شناسه کانال‌های ایتا و بله را وارد کنید.")
        else:
            with st.spinner(f"در حال واکشی آخرین پیام‌ها از @{clean_eitaa} (ایتا) و @{clean_bale} (بله)..."):
                try:
                    e_posts, b_posts = asyncio.run(
                        scrape_channels(clean_eitaa, clean_bale, limit=posts_limit)
                    )

                    if not e_posts and not b_posts:
                        st.error("❌ هیچ پیامی از کانال‌های مشخص شده دریافت نشد. لطفاً از اتصال اینترنت یا درستی شناسه اطمینان حاصل کنید.")
                    else:
                        st.session_state["eitaa_posts"] = e_posts
                        st.session_state["bale_posts"] = b_posts
                        st.session_state["eitaa_channel_name"] = clean_eitaa
                        st.session_state["bale_channel_name"] = clean_bale
                        st.success(
                            f"✅ استخراج موفق: {len(e_posts)} پست از ایتا (@{clean_eitaa}) و "
                            f"{len(b_posts)} پست از بله (@{clean_bale}) دریافت شد."
                        )
                except Exception as e:
                    st.error(f"خطا حین واکشی: {e}")


    if load_sample_button:
        st.session_state["eitaa_posts"] = SAMPLE_EITAA_POSTS.copy()
        st.session_state["bale_posts"] = SAMPLE_BALE_POSTS.copy()
        st.session_state["eitaa_channel_name"] = "farsna (نمونه)"
        st.session_state["bale_channel_name"] = "iribnews (نمونه)"
        st.info("ℹ️ داده‌های واقعی خبری نمونه جهت آزمون و ارزیابی بارگذاری شدند.")

    # -------------------------------------------------------------------------
    # Check Data Availability
    # -------------------------------------------------------------------------
    eitaa_posts: List[str] = st.session_state["eitaa_posts"]
    bale_posts: List[str] = st.session_state["bale_posts"]

    if not eitaa_posts or not bale_posts:
        st.info(
            "👋 برای شروع، شناسه کانال‌های مورد نظر را در نوار کناری وارد کرده و دکمه "
            "**«واکشی آنلاین»** را بزنید یا برای مشاهده فوری کارکرد سیستم بر روی **«داده نمونه»** کلیک کنید."
        )
        return

    # -------------------------------------------------------------------------
    # Main Tabs: Two-Column Feed View & Similarity Analysis Studio
    # -------------------------------------------------------------------------
    tab_feed, tab_similarity, tab_pipeline = st.tabs([
        f"📰 فید دو ستونه اخبار ({len(eitaa_posts)} ایتا | {len(bale_posts)} بله)",
        "🔬 استودیوی سنجش تشابه و تطابق (FAISS + TF-IDF)",
        "⚙️ خط‌لوله پیش‌پردازش متن فارسی (NLP Pipeline)",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Two-Column Live Scraped Feed
    # -------------------------------------------------------------------------
    with tab_feed:
        st.markdown(
            """
            <div style="margin-bottom: 1rem; color: #cbd5e1; font-size: 0.95rem;">
                📌 در این بخش تمامی پست‌های استخراج‌شده از هر دو پیام‌رسان به‌صورت ستون‌های تفکیک‌شده و ساختاریافته نمایش داده شده‌اند:
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_scraped_posts_columns(
            eitaa_posts=eitaa_posts,
            bale_posts=bale_posts,
            eitaa_channel=st.session_state["eitaa_channel_name"],
            bale_channel=st.session_state["bale_channel_name"],
        )

    # -------------------------------------------------------------------------
    # TAB 2: Similarity Matching Studio
    # -------------------------------------------------------------------------
    with tab_similarity:
        st.markdown("### 📌 انتخاب خبر و راهبرد مقایسه")

        col_select_eitaa, col_mode = st.columns([1, 1])

        with col_select_eitaa:
            st.markdown(f"**خبر مرجع از ایتا (@{st.session_state['eitaa_channel_name']}):**")
            eitaa_options = [
                f"پست #{i+1}: {post[:65]}..." for i, post in enumerate(eitaa_posts)
            ]
            selected_eitaa_idx = st.selectbox(
                "انتخاب خبر مرجع ایتا",
                range(len(eitaa_posts)),
                index=st.session_state.get("selected_eitaa_idx", 0) if st.session_state.get("selected_eitaa_idx", 0) < len(eitaa_posts) else 0,
                format_func=lambda i: eitaa_options[i],
                key="similarity_eitaa_select",
                label_visibility="collapsed",
            )
            st.session_state["selected_eitaa_idx"] = selected_eitaa_idx

        selected_eitaa_raw = eitaa_posts[selected_eitaa_idx]
        eitaa_cleaned = nlp_pipeline.transform(selected_eitaa_raw)

        with col_mode:
            st.markdown(f"**راهبرد انتخاب خبر از بله (@{st.session_state['bale_channel_name']}):**")
            match_strategy = st.radio(
                "راهبرد تطبیق با بله",
                [
                    "🔍 کشف خودکار مشابه‌ترین خبر با FAISS",
                    "⏱️ آخرین خبر دریافتی بله",
                    "✍️ انتخاب دستی خبر از بله",
                ],
                horizontal=False,
                key="similarity_strategy_radio",
                label_visibility="collapsed",
            )

            selected_bale_idx: int = 0
            rankings: List[Tuple[int, float]] = []

            if match_strategy.startswith("🔍 کشف خودکار"):
                with st.spinner("در حال محاسبه بردارها و جستجوی شباهت با FAISS..."):
                    bale_cleaned_list = [nlp_pipeline.transform(p) for p in bale_posts]
                    index, _ = faiss_engine.build_index(bale_cleaned_list)
                    rankings = faiss_engine.search_top_k(
                        index=index,
                        query=eitaa_cleaned,
                        top_k=len(bale_posts),
                    )
                    if rankings:
                        selected_bale_idx = rankings[0][0]
                st.caption(f"✨ کشف خودکار FAISS: **پست #{selected_bale_idx + 1}** بیشترین تطابق را دارد.")

            elif match_strategy.startswith("⏱️ آخرین خبر"):
                selected_bale_idx = 0
                st.caption("⏱️ جدیدترین پست دریافتی از بله انتخاب شد.")
            else:  # Manual selection
                bale_options = [
                    f"پست #{i+1}: {post[:65]}..." for i, post in enumerate(bale_posts)
                ]
                selected_bale_idx = st.selectbox(
                    "انتخاب دستی خبر بله",
                    range(len(bale_posts)),
                    index=st.session_state.get("selected_bale_idx", 0) if st.session_state.get("selected_bale_idx", 0) < len(bale_posts) else 0,
                    format_func=lambda i: bale_options[i],
                    key="similarity_bale_manual_select",
                    label_visibility="collapsed",
                )

            st.session_state["selected_bale_idx"] = selected_bale_idx

        selected_bale_raw = bale_posts[selected_bale_idx]
        bale_cleaned = nlp_pipeline.transform(selected_bale_raw)

        # Compute Similarities
        semantic_sim = faiss_engine.compute_similarity(eitaa_cleaned, bale_cleaned)
        lexical_sim = lexical_engine.compute_similarity(eitaa_cleaned, bale_cleaned)

        # Render Visual Metric Score Cards
        render_similarity_cards(semantic_score=semantic_sim, lexical_score=lexical_sim)

        # Side-by-side View of Raw Texts
        render_side_by_side_comparison(
            eitaa_text=selected_eitaa_raw,
            bale_text=selected_bale_raw,
            eitaa_channel=st.session_state["eitaa_channel_name"],
            bale_channel=st.session_state["bale_channel_name"],
        )

        # Ranking Table (when automatic search is active)
        if rankings and len(rankings) > 1:
            st.markdown("---")
            render_ranking_list(
                bale_posts=bale_posts,
                rankings=rankings,
                bale_channel=st.session_state["bale_channel_name"],
            )

    # -------------------------------------------------------------------------
    # TAB 3: NLP Pipeline Breakdown
    # -------------------------------------------------------------------------
    with tab_pipeline:
        st.markdown(
            """
            <div style="margin-bottom: 1.2rem; color: #cbd5e1; font-size: 0.95rem;">
                مراحل تمیزسازی، اصلاح نویسه‌ها، اعراب‌زدایی و پالایش کلمات توقف برای خبر انتخابی ایتا و بله:
            </div>
            """,
            unsafe_allow_html=True,
        )
        cur_eitaa_idx = st.session_state.get("selected_eitaa_idx", 0)
        cur_bale_idx = st.session_state.get("selected_bale_idx", 0)
        safe_eitaa_post = eitaa_posts[cur_eitaa_idx] if cur_eitaa_idx < len(eitaa_posts) else eitaa_posts[0]
        safe_bale_post = bale_posts[cur_bale_idx] if cur_bale_idx < len(bale_posts) else bale_posts[0]

        eitaa_stages = nlp_pipeline.transform_detailed(safe_eitaa_post)
        bale_stages = nlp_pipeline.transform_detailed(safe_bale_post)
        render_nlp_pipeline_stages(eitaa_stages, bale_stages)



if __name__ == "__main__":
    main()
