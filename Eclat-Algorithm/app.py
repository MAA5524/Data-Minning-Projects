"""Streamlit Dashboard for Eclat Association Rule Mining & Pattern Evaluation Suite.

Bilingual support: English & Persian (فارسی)
Based on Chapter 4 of 'Data Mining: Concepts and Techniques' (Han, Pei, Tong).
Featuring Vertical Data Format DFS, Lift vs. Kulczynski evaluation, and interactive visual analytics.
"""

from __future__ import annotations

import io
import math
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.eclat import eclat
from src.loader import TransactionData, load_dataset
from src.metrics import METRIC_METADATA, evaluate_rules
from src.rules import generate_association_rules

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Eclat Pattern Mining Suite | سامانه کاوش الگوهای اکلات",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. Internationalization (i18n) Dictionary
# -----------------------------------------------------------------------------
T = {
    "en": {
        "lang_name": "English",
        "title": "🛒 Eclat Association Rule Mining Suite",
        "subtitle": (
            "Equivalence Class Transformation with Vertical Data Format & Depth-First Search (DFS) "
            "• Han, Pei, Tong (Data Mining: Concepts and Techniques, Ch. 4)"
        ),
        "badge_format": "Format: {format}",
        "badge_algo": "Algorithm: Pure Vertical DFS Eclat",
        "badge_eval": "Evaluation: Lift vs. Null-Invariant Kulczynski",
        "sidebar_data_cfg": "🛒 Dataset Configuration",
        "data_source_label": "Choose Data Source:",
        "data_groceries": "Groceries Dataset (14.9k txns - Long Format)",
        "data_market_basket": "Market Basket Optimisation (7.5k txns - Basket Format)",
        "data_upload": "Upload Custom CSV",
        "upload_label": "Upload Transaction File (CSV)",
        "upload_help": "Supports Long format (Member_number, Date, itemDescription) or Horizontal Baskets (one basket per row).",
        "sidebar_params": "⚙️ Eclat Mining Parameters",
        "support_mode_label": "Support Threshold Mode:",
        "support_relative": "Relative Support (0.001 - 1.0)",
        "support_absolute": "Absolute Support Count (1 - N)",
        "minsup_rel_label": "Minimum Support (minsup):",
        "minsup_rel_help": "Fraction of transactions that must contain the itemset (e.g. 0.005 = 0.5%).",
        "minsup_abs_label": "Minimum Support Count (minsup count):",
        "minsup_abs_help": "Absolute number of transactions that must contain the itemset.",
        "minconf_label": "Minimum Confidence (minconf):",
        "minconf_help": "Conditional probability P(Y|X) required to validate a rule (e.g. 0.15 = 15%).",
        "max_len_label": "Max Itemset Length:",
        "max_len_help": "Optional ceiling on the size of frequent itemsets to mine.",
        "max_len_unconstrained": "Unconstrained",
        "focus_title": "📐 Pattern Evaluation Focus",
        "focus_active_hdr": "Active Evaluation Metrics:",
        "focus_lift": "• Lift: Non-Null-Invariant baseline",
        "focus_kulc": "• Kulczynski: Modern Null-Invariant measure",
        "focus_note": (
            "Han et al. (Ch. 4) highlight that Lift is heavily distorted by null-transactions, "
            "whereas Kulczynski stays neutral and reliable for sparse market baskets."
        ),
        "kpi_txns": "Transactions (N)",
        "kpi_txns_sub": "Total unique baskets",
        "kpi_items": "Unique Items",
        "kpi_items_sub": "Distinct catalog items",
        "kpi_itemsets": "Frequent Itemsets",
        "kpi_itemsets_sub": "min_sup: {minsup}",
        "kpi_rules": "Valid Rules",
        "kpi_rules_sub": "min_conf: {minconf}%",
        "kpi_time": "Mining Time",
        "kpi_time_sub": "Pure Python DFS",
        "tab_rules": "📋 Association Rules",
        "tab_itemsets": "📦 Frequent Itemsets Explorer",
        "tab_viz": "📊 Visual Analytics",
        "tab_theory": "📖 Theory & Formulas Guide",
        "rules_hdr": "Discovered Association Rules",
        "rules_empty": "💡 No association rules found with the current thresholds. Try lowering Minimum Support or Minimum Confidence.",
        "filter_ante": "🔍 Filter by Antecedent (X):",
        "filter_cons": "🔍 Filter by Consequent (Y):",
        "filter_min_lift": "Min Lift:",
        "filter_min_kulc": "Min Kulczynski:",
        "showing_rules": "Showing **{filtered:,}** of **{total:,}** rules",
        "col_rule": "Association Rule (X ➔ Y)",
        "col_rule_help": "Transactions containing X also tend to contain Y.",
        "col_support": "Support",
        "col_support_help": "Relative support s(X ∪ Y) = count(X ∪ Y) / N",
        "col_count": "Count",
        "col_count_help": "Number of transactions containing both X and Y",
        "col_confidence": "Confidence",
        "col_confidence_help": "Conditional probability P(Y|X) = sup(X ∪ Y) / sup(X)",
        "col_lift": "Lift",
        "col_lift_help": "Lift(X, Y) = s(X ∪ Y) / (s(X) * s(Y)). > 1 implies positive correlation; < 1 negative.",
        "col_kulc": "Kulczynski",
        "col_kulc_help": "Kulc(X, Y) = 0.5 * (P(Y|X) + P(X|Y)). Null-invariant measure in [0, 1]. > 0.5 implies positive correlation.",
        "btn_download_rules": "📥 Download Filtered Rules as CSV",
        "itemsets_hdr": "Frequent Itemsets Discovered by Vertical Eclat",
        "itemsets_empty": "No frequent itemsets discovered. Try lowering the Minimum Support.",
        "filter_k_size": "Filter by Itemset Size (k):",
        "filter_item_search": "🔍 Search Item within Itemsets:",
        "showing_itemsets": "Showing **{filtered:,}** of **{total:,}** itemsets",
        "col_itemset": "Frequent Itemset",
        "col_size": "Size (k)",
        "col_sup_count": "Support Count",
        "btn_download_itemsets": "📥 Download Itemsets as CSV",
        "viz_hdr": "Interactive Pattern Visualizations",
        "viz_top_items": "🏆 Top 15 Most Frequent Items",
        "viz_sizes": "📊 Frequent Itemset Size Distribution",
        "viz_scatter": "🔍 Support vs. Confidence Rule Space (Colored by Lift, Sized by Kulczynski)",
        "theory_hdr": "📖 Mathematical Foundations & Eclat Algorithm Theory",
        "theory_caption": "Based on Chapter 4 of Data Mining: Concepts and Techniques (Han, Pei, Tong)",
        "theory_sec1_title": "1. Vertical Data Format & Eclat DFS",
        "theory_sec2_title": "2. Rule Generation & Confidence",
        "theory_sec3_title": "3. Pattern Evaluation: Lift vs. Kulczynski & The Null-Invariance Dilemma",
        "theory_matrix_title": "⚖️ Metric Comparison Matrix",
        "upload_prompt": "👆 Please upload a CSV file in the sidebar to begin mining.",
        "dataset_empty": "The selected dataset is empty or could not be parsed.",
        "dataset_not_found": "Default dataset not found at `{path}`.",
    },
    "fa": {
        "lang_name": "فارسی",
        "title": "🛒 سامانه کاوش الگوهای مکرر و قوانین وابستگی با الگوریتم Eclat",
        "subtitle": (
            "تبدیل کلاس‌های هم‌ارزی با قالب داده عمودی و جستجوی عمق‌اول (DFS) "
            "• هان، پی، تانگ (مفاهیم و تکنیک‌های داده‌کاوی، فصل ۴)"
        ),
        "badge_format": "قالب داده: {format}",
        "badge_algo": "الگوریتم: Eclat عمودی با DFS خالص",
        "badge_eval": "ارزیابی الگو: مقایسه Lift و Kulczynski ناوردای تهی",
        "sidebar_data_cfg": "🛒 تنظیمات مجموعه داده",
        "data_source_label": "انتخاب منبع داده:",
        "data_groceries": "دیتاست خواربارفروشی (۱۴.۹ هزار تراکنش - قالب طولی)",
        "data_market_basket": "بهینه‌سازی سبد خرید Market Basket (۷.۵ هزار تراکنش - قالب افقی)",
        "data_upload": "بارگذاری فایل CSV دلخواه",
        "upload_label": "بارگذاری فایل تراکنش‌ها (CSV)",
        "upload_help": "پشتیبانی از قالب طولی (شماره عضو، تاریخ، نام قلم) یا سبدهای افقی (هر سطر یک سبد خرید).",
        "sidebar_params": "⚙️ پارامترهای کاوش Eclat",
        "support_mode_label": "حالت آستانه پشتیبان (Support):",
        "support_relative": "پشتیبان نسبی (۰.۰۰۱ تا ۱.۰)",
        "support_absolute": "شمارش پشتیبان مطلق (۱ تا N)",
        "minsup_rel_label": "حداقل پشتیبان نسبی (minsup):",
        "minsup_rel_help": "کسری از کل تراکنش‌ها که باید شامل مجموعه اقلام باشند (مثلاً ۰.۰۰۵ = ۰.۵ درصد).",
        "minsup_abs_label": "حداقل شمارش پشتیبان (تعداد تراکنش):",
        "minsup_abs_help": "حداقل تعداد سبدهایی که باید شامل مجموعه اقلام باشند.",
        "minconf_label": "حداقل اطمینان (minconf):",
        "minconf_help": "احتمال شرطی P(Y|X) مورد نیاز برای اعتبارسنجی قانون (مثلاً ۰.۱۵ = ۱۵ درصد).",
        "max_len_label": "حداکثر طول مجموعه اقلام:",
        "max_len_help": "سقف اختیاری برای طول مجموعه‌های اقلام مکرر.",
        "max_len_unconstrained": "نامحدود",
        "focus_title": "📐 تمرکز بر ارزیابی الگوها",
        "focus_active_hdr": "معیارهای ارزیابی فعال:",
        "focus_lift": "• لیفت (Lift): معیار سنتی (وابسته به تراکنش‌های تهی)",
        "focus_kulc": "• کولچینسکی (Kulczynski): معیار مدرن ناوردای تهی (Null-Invariant)",
        "focus_note": (
            "هان و همکاران (فصل ۴) تأکید می‌کنند که لیفت با افزایش تراکنش‌های تهی به شدت گمراه‌کننده "
            "می‌شود، در حالی که کولچینسکی کاملاً پایدار، بی‌طرف و ایده‌آل برای سبد خرید تنک است."
        ),
        "kpi_txns": "تعداد کل تراکنش‌ها (N)",
        "kpi_txns_sub": "سبدهای خرید یکتا",
        "kpi_items": "اقلام منحصربه‌فرد",
        "kpi_items_sub": "تعداد اقلام متمایز کاتالوگ",
        "kpi_itemsets": "مجموعه‌های اقلام مکرر",
        "kpi_itemsets_sub": "پشتیبان: {minsup}",
        "kpi_rules": "قوانین معتبر استخراج‌شده",
        "kpi_rules_sub": "اطمینان: {minconf}%",
        "kpi_time": "زمان کاوش",
        "kpi_time_sub": "پایتون خالص (DFS)",
        "tab_rules": "📋 قوانین وابستگی (Association Rules)",
        "tab_itemsets": "📦 کاوشگر مجموعه‌های مکرر (Itemsets)",
        "tab_viz": "📊 تحلیل‌های بصری تعاملی",
        "tab_theory": "📖 راهنمای نظریه و فرمول‌های ریاضی",
        "rules_hdr": "قوانین وابستگی کشف‌شده",
        "rules_empty": "💡 قانونی با آستانه‌های فعلی یافت نشد. لطفاً حداقل پشتیبان یا اطمینان را کاهش دهید.",
        "filter_ante": "🔍 فیلتر بر اساس پیش‌آیند (X):",
        "filter_cons": "🔍 فیلتر بر اساس پس‌آیند (Y):",
        "filter_min_lift": "حداقل لیفت (Lift):",
        "filter_min_kulc": "حداقل کولچینسکی (Kulczynski):",
        "showing_rules": "نمایش **{filtered:,}** از **{total:,}** قانون استخراج‌شده",
        "col_rule": "قانون وابستگی (X ➔ Y)",
        "col_rule_help": "بیان می‌کند که خریداران پیش‌آیند X، تمایل به خرید پس‌آیند Y نیز دارند.",
        "col_support": "پشتیبان نسبی",
        "col_support_help": "پشتیبان نسبی s(X ∪ Y) = count(X ∪ Y) / N",
        "col_count": "شمارش",
        "col_count_help": "تعداد تراکنش‌های حاوی هر دو قلم X و Y",
        "col_confidence": "اطمینان (Confidence)",
        "col_confidence_help": "احتمال شرطی P(Y|X) = sup(X ∪ Y) / sup(X)",
        "col_lift": "لیفت (Lift)",
        "col_lift_help": "لیفت Lift(X, Y). مقادیر بیشتر از ۱ بیانگر همبستگی مثبت و کمتر از ۱ منفی است.",
        "col_kulc": "کولچینسکی (Kulczynski)",
        "col_kulc_help": "معیار ناوردای تهی در بازه [۰, ۱]. مقادیر بیشتر از ۰.۵ نشان‌دهنده همبستگی مثبت است.",
        "btn_download_rules": "📥 دریافت قوانین فیلترشده در قالب فایل CSV",
        "itemsets_hdr": "مجموعه‌های مکرر کشف‌شده توسط الگوریتم عمودی Eclat",
        "itemsets_empty": "هیچ مجموعه مکرری با این آستانه یافت نشد. مقدار پشتیبان را کاهش دهید.",
        "filter_k_size": "فیلتر بر اساس اندازه مجموعه اقلام (k):",
        "filter_item_search": "🔍 جستجوی نام قلم درون مجموعه‌ها:",
        "showing_itemsets": "نمایش **{filtered:,}** از **{total:,}** مجموعه مکرر",
        "col_itemset": "مجموعه اقلام مکرر",
        "col_size": "اندازه (k)",
        "col_sup_count": "شمارش تکرار",
        "btn_download_itemsets": "📥 دریافت مجموعه‌های اقلام در قالب CSV",
        "viz_hdr": "نمودارهای تحلیلی و بصری تعاملی",
        "viz_top_items": "🏆 ۱۵ قلم با بیشترین فراوانی در تراکنش‌ها",
        "viz_sizes": "📊 توزیع اندازه مجموعه‌های اقلام مکرر",
        "viz_scatter": "🔍 فضای قوانین: پشتیبان در برابر اطمینان (رنگ: لیفت، اندازه: کولچینسکی)",
        "theory_hdr": "📖 مبانی ریاضی و نظری الگوریتم Eclat و ارزیابی الگوها",
        "theory_caption": "بر اساس فصل ۴ کتاب مفاهیم و تکنیک‌های داده‌کاوی (هان، پی، تانگ)",
        "theory_sec1_title": "۱. قالب داده عمودی (Vertical Format) و جستجوی عمق‌اول Eclat",
        "theory_sec2_title": "۲. استخراج قوانین وابستگی و اطمینان",
        "theory_sec3_title": "۳. ارزیابی الگوها: مقایسه Lift و Kulczynski و مسئله ناوردایی تهی",
        "theory_matrix_title": "⚖️ ماتریس مقایسه ویژگی‌های دو معیار",
        "upload_prompt": "👆 لطفاً برای شروع کاوش، یک فایل CSV در نوار کناری بارگذاری کنید.",
        "dataset_empty": "مجموعه داده انتخاب‌شده خالی است یا قابل خواندن نمی‌باشد.",
        "dataset_not_found": "مجموعه داده پیش‌فرض در مسیر `{path}` یافت نشد.",
    },
}

# -----------------------------------------------------------------------------
# 3. Sidebar Language Switcher
# -----------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "fa"  # Persian as default or toggleable

with st.sidebar:
    st.markdown("### 🌐 Language / انتخاب زبان")
    selected_lang = st.radio(
        label="Language Selector",
        options=["فارسی (Persian)", "English"],
        index=0 if st.session_state.lang == "fa" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    current_lang = "fa" if "فارسی" in selected_lang else "en"
    st.session_state.lang = current_lang

txt = T[current_lang]
is_rtl = current_lang == "fa"

# -----------------------------------------------------------------------------
# 4. Custom CSS Injection (Theme-Agnostic, High-Contrast & RTL-Aware)
# -----------------------------------------------------------------------------
direction_css = "rtl" if is_rtl else "ltr"
text_align_css = "right" if is_rtl else "left"
font_family_css = (
    "'Vazirmatn', 'Tahoma', 'Segoe UI', system-ui, sans-serif"
    if is_rtl
    else "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
)

st.markdown(
    f"""
    <style>
    /* Global Typography & Direction */
    body, p, div, span, h1, h2, h3, h4, h5, h6, input, label {{
        font-family: {font_family_css};
    }}
    .app-container {{
        direction: {direction_css};
        text-align: {text_align_css};
    }}

    /* Metric Cards - Translucent background adapts to both Light and Dark modes */
    .metric-card {{
        background: rgba(99, 102, 241, 0.06);
        border: 1px solid rgba(99, 102, 241, 0.22);
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        margin-bottom: 0.6rem;
        direction: {direction_css};
        text-align: {text_align_css};
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.12);
    }}
    .metric-label {{
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.8;
        margin-bottom: 0.25rem;
    }}
    .metric-value {{
        font-size: 1.85rem;
        font-weight: 800;
        color: #4f46e5;
        line-height: 1.2;
    }}
    .metric-sub {{
        font-size: 0.78rem;
        opacity: 0.7;
        margin-top: 0.25rem;
    }}

    /* Header Banner */
    .header-container {{
        padding: 1.2rem 0 1rem 0;
        border-bottom: 1px solid rgba(148, 163, 184, 0.25);
        margin-bottom: 1.4rem;
        direction: {direction_css};
        text-align: {text_align_css};
    }}
    .header-title {{
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.35rem;
    }}
    .header-subtitle {{
        font-size: 1rem;
        opacity: 0.8;
        margin-bottom: 0.75rem;
        line-height: 1.5;
    }}
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 0.4rem;
        margin-left: 0.4rem;
        margin-bottom: 0.35rem;
    }}
    .badge-primary {{
        background: rgba(79, 70, 229, 0.15);
        color: #4f46e5;
        border: 1px solid rgba(79, 70, 229, 0.3);
    }}
    .badge-success {{
        background: rgba(16, 185, 129, 0.15);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .badge-info {{
        background: rgba(14, 165, 233, 0.15);
        color: #0284c7;
        border: 1px solid rgba(14, 165, 233, 0.3);
    }}

    /* Callout & Theory Boxes - Fixed for 100% readability in Dark and Light themes */
    .callout-box {{
        background: rgba(99, 102, 241, 0.08);
        border-{'right' if is_rtl else 'left'}: 4px solid #4f46e5;
        border-radius: {'8px 0 0 8px' if is_rtl else '0 8px 8px 0'};
        padding: 0.95rem 1.15rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        direction: {direction_css};
        text-align: {text_align_css};
        line-height: 1.55;
    }}
    .callout-box b {{
        color: inherit;
        font-weight: 700;
    }}
    .callout-note {{
        font-size: 0.82rem;
        opacity: 0.8;
        margin-top: 0.45rem;
        display: block;
        line-height: 1.5;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. Cached Data Loading & Mining Functions
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_cached_dataset(source_identifier: str, file_bytes: bytes | None = None) -> TransactionData:
    """Load and parse the dataset with caching."""
    if file_bytes is not None:
        stream = io.BytesIO(file_bytes)
        return load_dataset(stream)
    return load_dataset(source_identifier)


@st.cache_data(show_spinner=False)
def run_cached_eclat(
    _tid_lists: dict[str, set[int]],
    total_transactions: int,
    minsup: float | int,
    max_len: int | None = None,
) -> dict[frozenset[str], int]:
    """Execute Eclat frequent itemset mining with caching."""
    return eclat(_tid_lists, total_transactions, minsup, max_len)


# -----------------------------------------------------------------------------
# 6. Sidebar Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown(f"### {txt['sidebar_data_cfg']}")

    DATA_DIR = Path(__file__).parent / "data"
    default_groceries_path = DATA_DIR / "Groceries_dataset.csv"
    default_market_basket_path = DATA_DIR / "Market_Basket_Optimisation.csv"

    dataset_options = [txt["data_groceries"], txt["data_market_basket"], txt["data_upload"]]
    dataset_choice = st.radio(
        txt["data_source_label"],
        options=dataset_options,
        index=0,
    )

    uploaded_file = None
    if dataset_choice == txt["data_upload"]:
        uploaded_file = st.file_uploader(
            txt["upload_label"],
            type=["csv", "txt"],
            help=txt["upload_help"],
        )

    st.markdown("---")
    st.markdown(f"### {txt['sidebar_params']}")

    support_mode = st.radio(
        txt["support_mode_label"],
        options=[txt["support_relative"], txt["support_absolute"]],
        index=0,
    )

    if support_mode == txt["support_relative"]:
        minsup_val = st.slider(
            txt["minsup_rel_label"],
            min_value=0.001,
            max_value=0.200,
            value=0.005,
            step=0.001,
            format="%.3f",
            help=txt["minsup_rel_help"],
        )
    else:
        minsup_val = st.number_input(
            txt["minsup_abs_label"],
            min_value=1,
            max_value=1000,
            value=75,
            step=5,
            help=txt["minsup_abs_help"],
        )

    minconf_val = st.slider(
        txt["minconf_label"],
        min_value=0.01,
        max_value=1.00,
        value=0.15,
        step=0.01,
        format="%.2f",
        help=txt["minconf_help"],
    )

    max_len_options = [txt["max_len_unconstrained"], "2", "3", "4", "5"]
    max_len_option = st.selectbox(
        txt["max_len_label"],
        options=max_len_options,
        index=0,
        help=txt["max_len_help"],
    )
    max_len = None if max_len_option == txt["max_len_unconstrained"] else int(max_len_option)

    st.markdown("---")
    st.markdown(f"### {txt['focus_title']}")
    st.markdown(
        f"""
        <div class="callout-box">
            <b>{txt['focus_active_hdr']}</b><br/>
            {txt['focus_lift']}<br/>
            {txt['focus_kulc']}<br/>
            <span class="callout-note">
                {txt['focus_note']}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 7. Data Ingestion & Algorithm Execution
# -----------------------------------------------------------------------------
with st.spinner("در حال بارگذاری داده‌ها..." if is_rtl else "Loading dataset..."):
    if dataset_choice == txt["data_upload"]:
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            txn_data = get_cached_dataset(f"upload_{uploaded_file.name}", file_bytes=file_bytes)
        else:
            st.info(txt["upload_prompt"])
            st.stop()
    elif dataset_choice == txt["data_market_basket"]:
        if default_market_basket_path.exists():
            txn_data = get_cached_dataset(str(default_market_basket_path))
        else:
            st.error(txt["dataset_not_found"].format(path=default_market_basket_path))
            st.stop()
    else:  # Groceries Dataset
        if default_groceries_path.exists():
            txn_data = get_cached_dataset(str(default_groceries_path))
        else:
            st.error(txt["dataset_not_found"].format(path=default_groceries_path))
            st.stop()

if txn_data.total_transactions == 0:
    st.warning(txt["dataset_empty"])
    st.stop()

# Run Eclat mining and benchmark runtime
t_start = time.perf_counter()
frequent_itemsets = run_cached_eclat(
    txn_data.tid_lists,
    txn_data.total_transactions,
    minsup_val,
    max_len=max_len,
)
t_eclat = (time.perf_counter() - t_start) * 1000.0

# Generate rules & evaluate metrics
raw_rules = generate_association_rules(frequent_itemsets, txn_data.total_transactions, minconf_val)
rules_df = evaluate_rules(raw_rules)

# -----------------------------------------------------------------------------
# 8. Header Banner
# -----------------------------------------------------------------------------
badge_format_txt = txt["badge_format"].format(format=txn_data.format_detected)
st.markdown(
    f"""
    <div class="header-container">
        <div class="header-title">{txt['title']}</div>
        <div class="header-subtitle">{txt['subtitle']}</div>
        <div>
            <span class="badge badge-primary">{badge_format_txt}</span>
            <span class="badge badge-success">{txt['badge_algo']}</span>
            <span class="badge badge-info">{txt['badge_eval']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 9. KPI Summary Cards
# -----------------------------------------------------------------------------
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{txt['kpi_txns']}</div>
            <div class="metric-value">{txn_data.total_transactions:,}</div>
            <div class="metric-sub">{txt['kpi_txns_sub']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{txt['kpi_items']}</div>
            <div class="metric-value">{len(txn_data.items):,}</div>
            <div class="metric-sub">{txt['kpi_items_sub']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col3:
    minsup_display = f"{minsup_val:.3f}" if isinstance(minsup_val, float) else f"{minsup_val}"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{txt['kpi_itemsets']}</div>
            <div class="metric-value">{len(frequent_itemsets):,}</div>
            <div class="metric-sub">{txt['kpi_itemsets_sub'].format(minsup=minsup_display)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{txt['kpi_rules']}</div>
            <div class="metric-value">{len(rules_df):,}</div>
            <div class="metric-sub">{txt['kpi_rules_sub'].format(minconf=int(minconf_val * 100))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col5:
    time_unit = "میلی‌ثانیه" if is_rtl else "ms"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{txt['kpi_time']}</div>
            <div class="metric-value">{t_eclat:.1f} <span style="font-size:1rem;font-weight:600;">{time_unit}</span></div>
            <div class="metric-sub">{txt['kpi_time_sub']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 10. Interactive Tabs
# -----------------------------------------------------------------------------
tab_rules, tab_itemsets, tab_viz, tab_theory = st.tabs(
    [
        txt["tab_rules"],
        txt["tab_itemsets"],
        txt["tab_viz"],
        txt["tab_theory"],
    ]
)

# -----------------------------------------------------------------------------
# TAB 1: Association Rules Table
# -----------------------------------------------------------------------------
with tab_rules:
    st.markdown(f"#### {txt['rules_hdr']}")

    if rules_df.empty:
        st.info(txt["rules_empty"])
    else:
        f_col1, f_col2, f_col3, f_col4 = st.columns([2, 2, 1.5, 1.5])
        with f_col1:
            ante_search = st.text_input(txt["filter_ante"], placeholder="whole milk / rolls/buns")
        with f_col2:
            cons_search = st.text_input(txt["filter_cons"], placeholder="other vegetables / yogurt")
        with f_col3:
            min_lift_filter = st.number_input(txt["filter_min_lift"], min_value=0.0, value=0.0, step=0.1)
        with f_col4:
            min_kulc_filter = st.number_input(txt["filter_min_kulc"], min_value=0.0, max_value=1.0, value=0.0, step=0.05)

        filtered_df = rules_df.copy()
        if ante_search.strip():
            filtered_df = filtered_df[
                filtered_df["antecedent_str"].str.contains(ante_search.strip(), case=False, na=False)
            ]
        if cons_search.strip():
            filtered_df = filtered_df[
                filtered_df["consequent_str"].str.contains(cons_search.strip(), case=False, na=False)
            ]
        if min_lift_filter > 0:
            filtered_df = filtered_df[filtered_df["lift"] >= min_lift_filter]
        if min_kulc_filter > 0:
            filtered_df = filtered_df[filtered_df["kulczynski"] >= min_kulc_filter]

        st.caption(txt["showing_rules"].format(filtered=len(filtered_df), total=len(rules_df)))

        max_sup_in_rules = float(rules_df["support"].max()) if not rules_df.empty else 1.0

        column_config = {
            "rule_str": st.column_config.TextColumn(
                txt["col_rule"],
                help=txt["col_rule_help"],
                width="large",
            ),
            "support": st.column_config.ProgressColumn(
                txt["col_support"],
                help=txt["col_support_help"],
                format="%.3f",
                min_value=0.0,
                max_value=max(0.05, max_sup_in_rules),
            ),
            "support_count": st.column_config.NumberColumn(
                txt["col_count"],
                help=txt["col_count_help"],
                format="%d",
            ),
            "confidence": st.column_config.ProgressColumn(
                txt["col_confidence"],
                help=txt["col_confidence_help"],
                format="%.1f%%",
                min_value=0.0,
                max_value=1.0,
            ),
            "lift": st.column_config.NumberColumn(
                txt["col_lift"],
                help=txt["col_lift_help"],
                format="%.3f",
            ),
            "kulczynski": st.column_config.NumberColumn(
                txt["col_kulc"],
                help=txt["col_kulc_help"],
                format="%.3f",
            ),
        }

        display_columns = ["rule_str", "support", "support_count", "confidence", "lift", "kulczynski"]
        st.dataframe(
            filtered_df[display_columns],
            column_config=column_config,
            width="stretch",
            hide_index=True,
        )

        csv_data = filtered_df[display_columns].to_csv(index=False).encode("utf-8")
        st.download_button(
            label=txt["btn_download_rules"],
            data=csv_data,
            file_name="eclat_association_rules.csv",
            mime="text/csv",
        )

# -----------------------------------------------------------------------------
# TAB 2: Frequent Itemsets Explorer
# -----------------------------------------------------------------------------
with tab_itemsets:
    st.markdown(f"#### {txt['itemsets_hdr']}")

    if not frequent_itemsets:
        st.info(txt["itemsets_empty"])
    else:
        itemset_records = []
        for iset, cnt in frequent_itemsets.items():
            itemset_records.append(
                {
                    "itemset_str": "{" + ", ".join(sorted(iset)) + "}",
                    "size": len(iset),
                    "support_count": cnt,
                    "support": cnt / txn_data.total_transactions,
                }
            )
        itemsets_df = pd.DataFrame(itemset_records)

        i_col1, i_col2 = st.columns([1, 2])
        with i_col1:
            available_sizes = sorted(itemsets_df["size"].unique())
            all_size_label = "همه (All)" if is_rtl else "All"
            size_options = [all_size_label] + [str(s) for s in available_sizes]
            selected_size = st.selectbox(txt["filter_k_size"], size_options, index=0)
        with i_col2:
            item_query = st.text_input(txt["filter_item_search"], placeholder="whole milk / yogurt")

        filtered_itemsets = itemsets_df.copy()
        if selected_size != all_size_label:
            filtered_itemsets = filtered_itemsets[filtered_itemsets["size"] == int(selected_size)]
        if item_query.strip():
            filtered_itemsets = filtered_itemsets[
                filtered_itemsets["itemset_str"].str.contains(item_query.strip(), case=False, na=False)
            ]

        st.caption(txt["showing_itemsets"].format(filtered=len(filtered_itemsets), total=len(itemsets_df)))

        max_sup_itemset = float(itemsets_df["support"].max()) if not itemsets_df.empty else 1.0

        itemset_config = {
            "itemset_str": st.column_config.TextColumn(txt["col_itemset"], width="large"),
            "size": st.column_config.NumberColumn(txt["col_size"], format="%d"),
            "support_count": st.column_config.NumberColumn(txt["col_sup_count"], format="%d"),
            "support": st.column_config.ProgressColumn(
                txt["col_support"],
                format="%.3f",
                min_value=0.0,
                max_value=max(0.1, max_sup_itemset),
            ),
        }

        st.dataframe(
            filtered_itemsets,
            column_config=itemset_config,
            width="stretch",
            hide_index=True,
        )

        itemset_csv = filtered_itemsets.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=txt["btn_download_itemsets"],
            data=itemset_csv,
            file_name="eclat_frequent_itemsets.csv",
            mime="text/csv",
        )

# -----------------------------------------------------------------------------
# TAB 3: Visual Analytics
# -----------------------------------------------------------------------------
with tab_viz:
    st.markdown(f"#### {txt['viz_hdr']}")

    v_col1, v_col2 = st.columns(2)

    # 1. Top 15 Most Frequent 1-Items
    with v_col1:
        st.markdown(f"##### {txt['viz_top_items']}")
        item_frequencies = [
            {"item": item, "count": len(tids), "support": len(tids) / txn_data.total_transactions}
            for item, tids in txn_data.tid_lists.items()
        ]
        top_items_df = (
            pd.DataFrame(item_frequencies)
            .sort_values(by="count", ascending=False)
            .head(15)
            .iloc[::-1]  # reverse for horizontal bar chart
        )

        fig_items = px.bar(
            top_items_df,
            x="count",
            y="item",
            orientation="h",
            text="count",
            labels={
                "count": "تعداد در تراکنش‌ها" if is_rtl else "Transaction Count",
                "item": "قلم" if is_rtl else "Item",
            },
            color="support",
            color_continuous_scale="Purples",
        )
        fig_items.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=420,
            coloraxis_colorbar=dict(title="پشتیبان" if is_rtl else "Support"),
        )
        fig_items.update_traces(
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>"
            + ("تعداد: %{x}<br>پشتیبان: %{marker.color:.2%}" if is_rtl else "Count: %{x}<br>Support: %{marker.color:.2%}"),
        )
        st.plotly_chart(fig_items, width="stretch")

    # 2. Frequent Itemset Size Distribution
    with v_col2:
        st.markdown(f"##### {txt['viz_sizes']}")
        if frequent_itemsets:
            size_counts = pd.Series([len(iset) for iset in frequent_itemsets.keys()]).value_counts().sort_index()
            size_df = pd.DataFrame(
                {
                    "Size": size_counts.index.astype(str),
                    "Count": size_counts.values,
                }
            )
            fig_sizes = px.bar(
                size_df,
                x="Size",
                y="Count",
                text="Count",
                labels={
                    "Size": "طول مجموعه اقلام (k)" if is_rtl else "Itemset Size (k)",
                    "Count": "تعداد مجموعه‌ها" if is_rtl else "Number of Itemsets",
                },
                color="Count",
                color_continuous_scale="Teal",
            )
            fig_sizes.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20),
                height=420,
                coloraxis_showscale=False,
            )
            fig_sizes.update_traces(
                textposition="outside",
                hovertemplate=("طول: %{x}<br>مجموعه‌ها: %{y}" if is_rtl else "Size: %{x}<br>Itemsets: %{y}"),
            )
            st.plotly_chart(fig_sizes, width="stretch")
        else:
            st.info("مجموعه مکرری موجود نیست." if is_rtl else "No frequent itemsets to display.")

    # 3. Support vs Confidence Scatter Plot colored by Lift
    st.markdown(f"##### {txt['viz_scatter']}")
    if not rules_df.empty:
        fig_scatter = px.scatter(
            rules_df,
            x="support",
            y="confidence",
            color="lift",
            size="kulczynski",
            hover_name="rule_str",
            hover_data={
                "support": ":.3f",
                "confidence": ":.2%",
                "lift": ":.3f",
                "kulczynski": ":.3f",
                "support_count": True,
            },
            labels={
                "support": "پشتیبان نسبی (Support)" if is_rtl else "Support (s)",
                "confidence": "اطمینان (Confidence)" if is_rtl else "Confidence (c)",
                "lift": "لیفت (Lift)" if is_rtl else "Lift",
                "kulczynski": "کولچینسکی (Kulczynski)" if is_rtl else "Kulczynski",
            },
            color_continuous_scale="Viridis",
        )
        fig_scatter.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=480,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(tickformat=".2%"),
            yaxis=dict(tickformat=".0%"),
        )
        st.plotly_chart(fig_scatter, width="stretch")
    else:
        st.info(
            "برای رسم نمودار پراکندگی، آستانه‌ها را کاهش دهید تا قوانین استخراج شوند."
            if is_rtl
            else "Extract rules with lower thresholds to render the Support vs. Confidence scatter plot."
        )

# -----------------------------------------------------------------------------
# TAB 4: Theory & Formulas Guide
# -----------------------------------------------------------------------------
with tab_theory:
    st.markdown(f"#### {txt['theory_hdr']}")
    st.caption(txt["theory_caption"])

    t_col1, t_col2 = st.columns(2)

    with t_col1:
        if is_rtl:
            st.markdown("### ۱. قالب داده عمودی و جستجوی عمق‌اول Eclat")
            st.markdown(
                r"""
                الگوریتم **Eclat** (*Equivalence Class Transformation*) تراکنش‌های سنتی افقی سبد خرید
                $\langle \text{TID}: i_1, i_2, \dots \rangle$ را به **قالب داده عمودی** تبدیل می‌کند:
                $$\text{item} \longrightarrow \{ \text{TID}_1, \text{TID}_2, \dots \}$$

                **مزایای کلیدی نسبت به Apriori:**
                1. **عدم نیاز به تولید کاندیدا:** به جای اسکن مکرر دیتابیس، پشتیبان با **تقاطع مجموعه‌ها** محاسبه می‌شود:
                   $$\text{TID}(X \cup Y) = \text{TID}(X) \cap \text{TID}(Y)$$
                2. **جستجوی عمق‌اول (DFS):** کلاس‌های هم‌ارزی پیشوندی در درخت بازگشتی جستجو شده و مسیرهای کمتر از حد آستانه فوراً هرس می‌شوند.
                """
            )
        else:
            st.markdown(f"### {txt['theory_sec1_title']}")
            st.markdown(
                r"""
                **Eclat** (*Equivalence Class Transformation*) transforms traditional horizontal market baskets
                $\langle \text{TID}: i_1, i_2, \dots \rangle$ into the **Vertical Data Format**:
                $$\text{item} \longrightarrow \{ \text{TID}_1, \text{TID}_2, \dots \}$$

                **Key Computational Advantages:**
                1. **No Candidate Generation:** Rather than generating $(k+1)$-candidates and rescanning the full database,
                   Eclat computes itemset support via fast **set intersections**:
                   $$\text{TID}(X \cup Y) = \text{TID}(X) \cap \text{TID}(Y)$$
                2. **Depth-First Search (DFS):** Equivalence classes are recursively decomposed along prefix trees.
                   Infrequent paths are pruned immediately when $|\text{TID}(X \cup Y)| < \text{minsup}$.
                """
            )

    with t_col2:
        if is_rtl:
            st.markdown("### ۲. استخراج قوانین وابستگی و اطمینان")
            st.markdown(
                r"""
                برای هر مجموعه اقلام مکرر $I$ با طول $|I| \ge 2$، با افراز $I$ به زیرمجموعه‌های ناتهی و محض $X \subset I$
                و پس‌آیند $Y = I \setminus X$، قوانین کاندید $X \rightarrow Y$ تولید می‌شوند:

                - **پشتیبان مطلق (تعداد):** $\text{sup}(X \cup Y) = | \text{TID}(I) |$
                - **پشتیبان نسبی:**
                  $$s(X \cup Y) = \frac{\text{sup}(X \cup Y)}{N}$$
                - **اطمینان (Confidence):**
                  $$c(X \rightarrow Y) = \frac{\text{sup}(X \cup Y)}{\text{sup}(X)} = P(Y \mid X)$$

                قوانینی که شرط $c(X \rightarrow Y) \ge \text{minconf}$ را داشته باشند تأیید می‌شوند.
                """
            )
        else:
            st.markdown(f"### {txt['theory_sec2_title']}")
            st.markdown(
                r"""
                For every frequent itemset $I$ where $|I| \ge 2$, candidate rules $X \rightarrow Y$ are formed
                by partitioning $I$ into non-empty proper subsets $X \subset I$ and $Y = I \setminus X$:

                - **Support Count:** $\text{sup}(X \cup Y) = | \text{TID}(I) |$
                - **Relative Support:**
                  $$s(X \cup Y) = \frac{\text{sup}(X \cup Y)}{N}$$
                - **Confidence:**
                  $$c(X \rightarrow Y) = \frac{\text{sup}(X \cup Y)}{\text{sup}(X)} = P(Y \mid X)$$

                Rules satisfying $c(X \rightarrow Y) \ge \text{minconf}$ are retained for evaluation.
                """
            )

    st.markdown("---")
    st.markdown(f"### {txt['theory_sec3_title']}")

    p_col1, p_col2 = st.columns(2)

    with p_col1:
        if is_rtl:
            st.markdown(
                r"""
                #### 🔴 لیفت Lift (وابسته به تراکنش‌های تهی)
                $$\text{Lift}(X, Y) = \frac{s(X \cup Y)}{s(X) \times s(Y)} = \frac{P(X \cup Y)}{P(X) \cdot P(Y)}$$

                - **بازه مقادیر:** $[0, \infty)$
                - **مقدار مبنا (استقلال):** $1.0$
                  - $\text{Lift} > 1.0 \implies$ همبستگی مثبت.
                  - $\text{Lift} < 1.0 \implies$ همبستگی منفی.
                - **نقص تراکنش‌های تهی (Null-Transactions):**
                  در سبدهای خرید واقعی، اکثر تراکنش‌ها حاوی هیچ‌کدام از دو قلم $X$ یا $Y$ نیستند (مقدار $N$ بسیار بزرگ است).
                  چون مخرج کسر به $N$ وابسته است، افزایش تراکنش‌های تهی مقدار لیفت را به صورت کاذب افزایش می‌دهد!
                """
            )
        else:
            st.markdown(
                r"""
                #### 🔴 Lift (Non-Null-Invariant)
                $$\text{Lift}(X, Y) = \frac{s(X \cup Y)}{s(X) \times s(Y)} = \frac{P(X \cup Y)}{P(X) \cdot P(Y)}$$

                - **Range:** $[0, \infty)$
                - **Baseline:** $1.0$ (statistical independence).
                  - $\text{Lift} > 1.0 \implies$ Positive correlation.
                  - $\text{Lift} < 1.0 \implies$ Negative correlation.
                - **The Null-Transaction Flaw:**
                  In real market baskets, the vast majority of transactions contain neither $X$ nor $Y$.
                  Because the denominator relies quadratically on $N$, adding null transactions artificially inflates Lift!
                """
            )

    with p_col2:
        if is_rtl:
            st.markdown(
                r"""
                #### 🟢 کولچینسکی Kulczynski (ناوردای تهی - Null-Invariant)
                $$\text{Kulc}(X, Y) = \frac{1}{2} \left( \frac{s(X \cup Y)}{s(X)} + \frac{s(X \cup Y)}{s(Y)} \right) = \frac{1}{2} \Big( c(X \rightarrow Y) + c(Y \rightarrow X) \Big)$$

                - **بازه مقادیر:** $[0, 1]$
                - **مقدار مبنا (خنثی):** $0.5$
                  - $\text{Kulc} > 0.5 \implies$ همبستگی مثبت.
                  - $\text{Kulc} < 0.5 \implies$ همبستگی منفی.
                - **چرا هان و همکاران Kulczynski را توصیه می‌کنند؟**
                  کولچینسکی **ناوردای تهی (Null-Invariant)** است: مقدار آن کاملاً از تراکنش‌هایی که نه شامل $X$ و نه شامل $Y$ هستند مستقل است
                  و مقداری پایدار و بدون سوگیری در تحلیل سبد خرید تنک ارائه می‌دهد.
                """
            )
        else:
            st.markdown(
                r"""
                #### 🟢 Kulczynski (Null-Invariant)
                $$\text{Kulc}(X, Y) = \frac{1}{2} \left( \frac{s(X \cup Y)}{s(X)} + \frac{s(X \cup Y)}{s(Y)} \right) = \frac{1}{2} \Big( c(X \rightarrow Y) + c(Y \rightarrow X) \Big)$$

                - **Range:** $[0, 1]$
                - **Baseline:** $0.5$ (neutral / independent).
                  - $\text{Kulc} > 0.5 \implies$ Positive correlation.
                  - $\text{Kulc} < 0.5 \implies$ Negative correlation.
                - **Why Han et al. Recommend Kulczynski:**
                  Kulczynski is **Null-Invariant**: it depends strictly on $s(X \cup Y)$, $s(X)$, and $s(Y)$.
                  Adding null transactions does NOT alter its value, making it reliable for sparse datasets.
                """
            )

    st.markdown("---")
    st.markdown(f"#### {txt['theory_matrix_title']}")
    if is_rtl:
        comparison_table = pd.DataFrame(
            [
                {
                    "معیار": "لیفت (Lift)",
                    "فرمول ریاضی": "s(X ∪ Y) / (s(X) × s(Y))",
                    "بازه تغییرات": "[0, ∞)",
                    "مقدار خنثی": "1.0",
                    "ناوردای تهی؟": "❌ خیر (وابسته به N)",
                    "کاربرد پیشنهادی": "مجموعه داده‌های متراکم با تراکنش‌های تهی ناچیز",
                },
                {
                    "معیار": "کولچینسکی (Kulczynski)",
                    "فرمول ریاضی": "0.5 × (c(X→Y) + c(Y→X))",
                    "بازه تغییرات": "[0, 1]",
                    "مقدار خنثی": "0.5",
                    "ناوردای تهی؟": "✅ بله (مستقل از N)",
                    "کاربرد پیشنهادی": "سبد خرید تنک و داده‌های واقعی بازار (توصیه هان و همکاران)",
                },
            ]
        )
    else:
        comparison_table = pd.DataFrame(
            [
                {
                    "Metric": "Lift",
                    "Formula": "s(X ∪ Y) / (s(X) × s(Y))",
                    "Range": "[0, ∞)",
                    "Neutral Value": "1.0",
                    "Null-Invariant?": "❌ No",
                    "Recommended Use": "Dense datasets with few null transactions",
                },
                {
                    "Metric": "Kulczynski",
                    "Formula": "0.5 × (s(XY)/s(X) + s(XY)/s(Y))",
                    "Range": "[0, 1]",
                    "Neutral Value": "0.5",
                    "Null-Invariant?": "✅ Yes",
                    "Recommended Use": "Sparse transaction / market basket datasets (Han et al.)",
                },
            ]
        )
    st.table(comparison_table)
