/**
 * static/app.js - Modern Bilingual Controller for HUP-FPGrowth
 * Full English & Persian (فارسی) Support with Dynamic LTR/RTL Switching,
 * Chart.js Visualizations, and Table Analytics.
 */

// Bilingual Translation Dictionary
const I18N = {
  en: {
    langName: "فارسی",
    brandTitle: "HUP-FPGrowth",
    brandSubtitle: "High Utility Pattern Mining Dashboard",
    algoBadge: "UP-Tree • TWU Two-Phase",
    miningParams: "Mining Parameters",
    configureThresholds: "Configure tree pruning thresholds",
    targetDataset: "Target Dataset",
    uploadCustom: "Upload Custom Dataset",
    dropzonePrompt: "Upload <strong>.csv</strong> or SPMF <strong>.txt</strong>",
    thresholdMode: "Threshold Mode",
    modeRelative: "Relative (% of Utility)",
    modeAbsolute: "Absolute Value",
    minUtility: "Minimum Utility",
    presetLabel: "Preset:",
    presetLow: "Rich (Low)",
    presetDefault: "Optimal",
    presetHigh: "Strict",
    maxPatternLength: "Max Pattern Length (k)",
    kPairs: "2-itemsets (Pairs)",
    kTriples: "3-itemsets (Triples)",
    kStandard: "4-itemsets (Standard)",
    kFive: "5-itemsets",
    kUnlimited: "Unlimited Length",
    btnRunMining: "Run HUP-FPGrowth",
    miningInProgress: "Mining patterns...",
    executionPipeline: "Execution Pipeline",
    pipelineStep1: "TWU Pruning (Downward Closure)",
    pipelineStep2: "Compressed UP-Tree Construction",
    pipelineStep3: "Phase 1: Conditional Tree DFS (PHUIs)",
    pipelineStep4: "Phase 2: Inverted-Index Verification (HUIs)",

    // KPIs
    kpiTotalTx: "Total Transactions",
    kpiPromising: "Promising Items",
    kpiItemsAboveTWU: "Items above min TWU",
    kpiVerifiedHuis: "Verified HUIs (Phase 2)",
    kpiFromPhuis: "from {0} Phase 1 PHUIs",
    kpiTopPattern: "Top Pattern Utility",
    topEarner: "Top earner",
    kpiExecutionTime: "Execution Time",
    kpiPruningEff: "Pruning: {0}%",
    totalUtilSub: "Total Utility: {0}",

    // Tabs
    tabPatternsTable: "High Utility Patterns Table",
    tabAnalytics: "Visual Analytics & Charts",
    tabHiddenGems: "Hidden Gems",
    tabTheoryGuide: "Algorithm & Theory Guide",

    // Table
    searchPlaceholder: "Filter by item name or ID...",
    filterSizeLabel: "Size k:",
    filterAllSizes: "All Sizes",
    sortByLabel: "Sort By:",
    sortUtilDesc: "Exact Utility (High → Low)",
    sortUtilAsc: "Exact Utility (Low → High)",
    sortSupDesc: "Support Count (High → Low)",
    sortAvgDesc: "Avg Utility / Tx (High → Low)",
    sortLengthDesc: "Length k (High → Low)",
    btnDownloadCsv: "Download CSV",

    colIndex: "#",
    colK: "k",
    colPattern: "High Utility Itemset (Pattern)",
    colSupport: "Support Count",
    colSupportPct: "Support %",
    colUtility: "Exact Utility",
    colAvgUtility: "Avg Utility / Tx",
    colUtilityShare: "Utility Share",
    tableInitialState: "Click \"Run HUP-FPGrowth\" to mine high utility patterns.",
    tableNoMatch: "No matching high utility patterns found.",

    // Pagination
    showingText: "Showing",
    ofText: "of",
    patternsText: "patterns",
    rowsPerPage: "Rows:",
    btnPrev: "Prev",
    btnNext: "Next",
    pageText: "Page {0} of {1}",

    // Charts
    chartTopPatternsTitle: "Top High Utility Patterns",
    chartTopPatternsSubtitle: "Highest utility itemsets mined by UP-Tree",
    chartScatterTitle: "Utility vs. Frequency Scatter Plot",
    chartScatterSubtitle: "Exact Utility plotted against Support Frequency (%)",
    chartKDistTitle: "Pattern Size (k) Distribution",
    chartKDistSubtitle: "Number of itemsets discovered per cardinality",
    chartFunnelTitle: "Two-Phase Pruning Funnel",
    chartFunnelSubtitle: "Step-by-step candidate elimination efficiency",

    chartUtilAxisLabel: "Exact Utility ($)",
    chartSupportAxisLabel: "Support Frequency (%)",
    chartItemsetsAxisLabel: "Number of Itemsets",
    funnelStep1: "1. Total Items",
    funnelStep2: "2. Promising TWU",
    funnelStep3: "3. Phase 1 PHUIs",
    funnelStep4: "4. Phase 2 Verified HUIs",

    // Gems
    gemsIntroTitle: "Why High Utility Mining Beats Standard Frequency Mining",
    gemsIntroDesc: "In standard Frequent Pattern Mining (FP-Growth / Apriori), an itemset is discarded if its support frequency is below <code>min_sup</code>. In enterprise and e-commerce contexts, high-margin luxury items, premium bundles, or high-profit goods are purchased infrequently, yet generate the vast majority of business profit. <strong>These are \"Hidden Gems\"</strong>: patterns with low transaction frequency but huge utility yields.",
    gemsEmptyState: "No patterns mined yet. Run the algorithm to uncover hidden high-utility gems.",
    gemScoreLabel: "Score:",
    gemSupportLabel: "Support",
    gemExactUtilLabel: "Exact Utility",
    gemAvgOrderLabel: "Avg / Order",

    // Theory
    theoryHeading: "Theoretical Foundations of HUIM",
    theoryLead: "High Utility Itemset Mining (HUIM) generalizes Frequent Itemset Mining by considering both <strong>item quantities</strong> in transactions and <strong>unit profits (utility)</strong>, addressing the fundamental limitation that frequent items are not necessarily high-profit items.",
    mathItemUtilTitle: "1. Item Utility in Transaction",
    mathItemUtilDesc: "The utility of item <em>i</em> in transaction <em>T</em> is the product of its purchased quantity <em>q(i, T)</em> and its unit utility (e.g., profit margin) <em>p(i)</em>.",
    mathTUTitle: "2. Transaction Utility (TU)",
    mathTUDesc: "The total utility of transaction <em>T</em> across all items contained within it.",
    mathTWUTitle: "3. Transaction-Weighted Utility (TWU)",
    mathTWUDesc: "The sum of transaction utilities for all transactions containing itemset <em>X</em>. Used as an upper bound on true utility.",
    mathDownwardTitle: "4. TWU Downward Closure Property",
    mathDownwardDesc: "Unlike exact utility, <strong>TWU is monotonic</strong>. If <em>TWU(X) < min_utility</em>, no superset <em>Y ⊇ X</em> can be a high-utility itemset, guaranteeing zero false negatives!",
    workflowHeading: "Two-Phase Tree-Based Architecture",
    flowStep1Badge: "Phase 1",
    flowStep1Title: "Global TWU Pruning",
    flowStep1Desc: "Prune all unpromising items where <code>TWU(i) < min_utility</code>.",
    flowStep2Badge: "Phase 1",
    flowStep2Title: "UP-Tree Construction",
    flowStep2Desc: "Insert transactions ordered by descending TWU with Reorganized Transaction Utility (RTU).",
    flowStep3Badge: "Phase 1",
    flowStep3Title: "Conditional UP-Trees",
    flowStep3Desc: "Traverse HeaderTable bottom-up to generate Potential High Utility Itemsets (PHUIs).",
    flowStep4Badge: "Phase 2",
    flowStep4Title: "Exact Verification",
    flowStep4Desc: "Intersect inverted-index TID sets to compute exact <code>u(X) ≥ min_utility</code>.",
    dguDluTitle: "DGU & DLU Pruning Strategies",
    dguDesc: "<strong>DGU (Discarding Global Unpromising items):</strong> When constructing the global UP-Tree, utilities of items with global <em>TWU < min_utility</em> are eliminated from the transaction utility, dramatically tightening tree node upper bounds.",
    dluDesc: "<strong>DLU (Discarding Local Unpromising items):</strong> In conditional UP-Trees, items that are unpromising in the conditional pattern base are excluded from path utilities, avoiding tree inflation and accelerating recursive mining.",

    // Datasets
    dsEcommerce: "E-Commerce Retail (Named Items)",
    dsFoodmart: "Foodmart Grocery Utility",
  },

  fa: {
    langName: "English",
    brandTitle: "HUP-FPGrowth",
    brandSubtitle: "داشبورد تخصصی کاوش الگوهای با مطلوبیت بالا (HUIM)",
    algoBadge: "درخت UP • روش دوفازی TWU",
    miningParams: "پارامترهای کاوش",
    configureThresholds: "تنظیم آستانه‌های هرس درخت مطلوبیت",
    targetDataset: "دیتاست هدف",
    uploadCustom: "بارگذاری دیتاست دلخواه",
    dropzonePrompt: "بارگذاری فایل <strong>.csv</strong> یا فرمت SPMF <strong>.txt</strong>",
    thresholdMode: "حالت آستانه مطلوبیت",
    modeRelative: "نسبی (درصد از مطلوبیت کل)",
    modeAbsolute: "مقدار مطلق مطلوبیت",
    minUtility: "حداقل مطلوبیت (min_utility)",
    presetLabel: "پیش‌تنظیم:",
    presetLow: "غنی (پایین)",
    presetDefault: "بهینه",
    presetHigh: "سخت‌گیرانه",
    maxPatternLength: "حداکثر طول الگو (k)",
    kPairs: "الگوهای ۲-آیتمی (جفت‌ها)",
    kTriples: "الگوهای ۳-آیتمی (سه‌تایی)",
    kStandard: "الگوهای ۴-آیتمی (استاندارد)",
    kFive: "الگوهای ۵-آیتمی",
    kUnlimited: "طول نامحدود",
    btnRunMining: "اجرای الگوریتم HUP-FPGrowth",
    miningInProgress: "در حال کاوش الگوها...",
    executionPipeline: "خط‌سیر اجرای الگوریتم",
    pipelineStep1: "هرس بر اساس TWU (خاصیت بسته رو به پایین)",
    pipelineStep2: "ساخت درخت فشرده UP-Tree",
    pipelineStep3: "فاز ۱: کاوش درخت‌های شرطی (کاندیدهای PHUI)",
    pipelineStep4: "فاز ۲: راستی‌آزمایی دقیق با نمایه معکوس (HUI)",

    // KPIs
    kpiTotalTx: "تعداد کل تراکنش‌ها",
    kpiPromising: "اقلام امیدبخش",
    kpiItemsAboveTWU: "اقلام دارای TWU بالاتر از آستانه",
    kpiVerifiedHuis: "الگوهای با مطلوبیت بالا (فاز ۲)",
    kpiFromPhuis: "از میان {0} کاندید فاز ۱",
    kpiTopPattern: "بیشترین مطلوبیت الگو",
    topEarner: "پردرآمدترین الگو",
    kpiExecutionTime: "زمان اجرای الگوریتم",
    kpiPruningEff: "نرخ هرس: {0}٪",
    totalUtilSub: "مطلوبیت کل پایگاه‌داده: {0}",

    // Tabs
    tabPatternsTable: "جدول الگوهای با مطلوبیت بالا",
    tabAnalytics: "تحلیل بصری و نمودارها",
    tabHiddenGems: "گوهرهای پنهان سودآوری",
    tabTheoryGuide: "راهنمای مبانی نظری و ریاضی",

    // Table
    searchPlaceholder: "جستجو بر اساس نام کالا یا شناسه...",
    filterSizeLabel: "اندازه k:",
    filterAllSizes: "همه اندازه‌ها",
    sortByLabel: "مرتب‌سازی بر اساس:",
    sortUtilDesc: "مطلوبیت دقیق (بیشترین به کمترین)",
    sortUtilAsc: "مطلوبیت دقیق (کمترین به بیشترین)",
    sortSupDesc: "تعداد پشتیبان / تکرار (نزولی)",
    sortAvgDesc: "میانگین مطلوبیت در هر سفارش (نزولی)",
    sortLengthDesc: "طول الگو k (نزولی)",
    btnDownloadCsv: "دانلود خروجی CSV",

    colIndex: "ردیف",
    colK: "k",
    colPattern: "مجموعه آیتم با مطلوبیت بالا (الگو)",
    colSupport: "تعداد پشتیبان",
    colSupportPct: "درصد پشتیبان",
    colUtility: "مطلوبیت دقیق",
    colAvgUtility: "میانگین مطلوبیت / تراکنش",
    colUtilityShare: "سهم از کل مطلوبیت",
    tableInitialState: "برای استخراج الگوهای سودآور، روی دکمه «اجرای الگوریتم HUP-FPGrowth» کلیک کنید.",
    tableNoMatch: "هیچ الگوی با مطلوبیت بالایی با فیلترهای کنونی یافت نشد.",

    // Pagination
    showingText: "نمایش",
    ofText: "از مجموع",
    patternsText: "الگو",
    rowsPerPage: "سطرها:",
    btnPrev: "قبلی",
    btnNext: "بعدی",
    pageText: "صفحه {0} از {1}",

    // Charts
    chartTopPatternsTitle: "برترین الگوهای با مطلوبیت بالا",
    chartTopPatternsSubtitle: "پردرآمدترین مجموعه‌آیتم‌های استخراج‌شده توسط UP-Tree",
    chartScatterTitle: "نمودار پراکندگی مطلوبیت در برابر فراوانی (پشتیبان)",
    chartScatterSubtitle: "نمایش مطلوبیت دقیق در برابر درصد تکرار در تراکنش‌ها",
    chartKDistTitle: "توزیع فراوانی اندازه الگوها (k)",
    chartKDistSubtitle: "تعداد مجموعه‌آیتم‌های کشف‌شده به تفکیک طول الگو",
    chartFunnelTitle: "قیف هرس دوفازی الگوریتم",
    chartFunnelSubtitle: "کارایی مرحله‌به‌مرحله حذف نامزدهای کاذب",

    chartUtilAxisLabel: "مطلوبیت دقیق",
    chartSupportAxisLabel: "درصد فراوانی پشتیبان (٪)",
    chartItemsetsAxisLabel: "تعداد مجموعه‌آیتم‌ها",
    funnelStep1: "۱. کل اقلام",
    funnelStep2: "۲. اقلام امیدبخش TWU",
    funnelStep3: "۳. کاندیدهای فاز اول (PHUI)",
    funnelStep4: "۴. الگوهای تاییدشده نهایی (HUI)",

    // Gems
    gemsIntroTitle: "چرا کاوش مطلوبیت (HUIM) بر کاوش سنتی فراوانی برتری دارد؟",
    gemsIntroDesc: "در کاوش سنتی الگوهای مکرر (FP-Growth یا Apriori)، چنانچه تکرار یک آیتم کمتر از <code>min_sup</code> باشد حذف می‌شود. در تجارت و خرده‌فروشی واقعی، کالاهای گران‌قیمت یا بسته‌های لوکس ممکن است به ندرت خریداری شوند، اما بخش عمده سود خالص را تولید می‌کنند. <strong>این‌ها «گوهرهای پنهان» هستند</strong>: الگوهایی با تکرار اندک ولی سودآوری فوق‌العاده بالا که الگوریتم‌های سنتی فراوانی آن‌ها را به اشتباه دور می‌ریزند.",
    gemsEmptyState: "هنوز الگویی استخراج نشده است. الگوریتم را اجرا کنید تا گوهرهای پنهان سودآوری نمایان شوند.",
    gemScoreLabel: "امتیاز گوهر:",
    gemSupportLabel: "پشتیبان",
    gemExactUtilLabel: "مطلوبیت دقیق",
    gemAvgOrderLabel: "میانگین در سفارش",

    // Theory
    theoryHeading: "مبانی نظری و ریاضیات کاوش الگوهای با مطلوبیت بالا",
    theoryLead: "کاوش الگوهای با مطلوبیت بالا (HUIM) تعمیم‌یافته کاوش الگوهای مکرر است که هم <strong>تعداد اقلام خریداری‌شده</strong> و هم <strong>سود یا وزن واحد هر کالا</strong> را در نظر می‌گیرد و نقص بنیادین الگوریتم‌های سنتی را برطرف می‌سازد.",
    mathItemUtilTitle: "۱. مطلوبیت آیتم در تراکنش",
    mathItemUtilDesc: "مطلوبیت آیتم <em>i</em> در تراکنش <em>T</em> برابر حاصل‌ضرب تعداد خریداری‌شده <em>q(i, T)</em> در سود واحد کالا <em>p(i)</em> است.",
    mathTUTitle: "۲. مطلوبیت تراکنش (TU)",
    mathTUDesc: "مجموع مطلوبیت‌های تمامی اقلام موجود در یک تراکنش <em>T</em>.",
    mathTWUTitle: "۳. مطلوبیت وزن‌دار تراکنش (TWU)",
    mathTWUDesc: "مجموع TU تمامی تراکنش‌هایی که شامل مجموعه‌آیتم <em>X</em> هستند. از این شاخص به عنوان کران بالای قطعی برای مطلوبیت حقیقی استفاده می‌شود.",
    mathDownwardTitle: "۴. خاصیت بسته رو به پایین TWU",
    mathDownwardDesc: "بر خلاف مطلوبیت دقیق، <strong>شاخص TWU یکنوا است</strong>. اگر <em>TWU(X) < min_utility</em> باشد، هیچ زیرمجموعه یا ابرمجموعه‌ای از <em>X</em> نمی‌تواند با مطلوبیت بالا باشد؛ بنابراین بدون هیچ‌گونه ریزش کاذب، فضای جستجو هرس می‌شود!",
    workflowHeading: "معماری دوفازی مبتنی بر درخت UP-Tree",
    flowStep1Badge: "فاز ۱",
    flowStep1Title: "هرس سراسری با TWU",
    flowStep1Desc: "حذف کلیه اقلام غیرامیدبخش که <code>TWU(i) < min_utility</code> دارند.",
    flowStep2Badge: "فاز ۱",
    flowStep2Title: "ساخت ساختار UP-Tree",
    flowStep2Desc: "درج تراکنش‌های مرتب‌شده با مطلوبیت بازسازمان‌یافته (RTU).",
    flowStep3Badge: "فاز ۱",
    flowStep3Title: "درخت‌های شرطی UP-Tree",
    flowStep3Desc: "پیمایش پایین‌به‌بالای جدول سرآیند برای تولید کاندیدهای بالقوه (PHUI).",
    flowStep4Badge: "فاز ۲",
    flowStep4Title: "راستی‌آزمایی دقیق مطلوبیت",
    flowStep4Desc: "اشتراک‌گیری سریع شناسه‌های تراکنش در نمایه معکوس جهت اعتبارسنجی <code>u(X) ≥ min_utility</code>.",
    dguDluTitle: "استراتژی‌های هرس DGU و DLU",
    dguDesc: "<strong>DGU (حذف اقلام غیرامیدبخش سراسری):</strong> هنگام ساخت درخت UP-Tree، مطلوبیت اقلامی که TWU سراسری کمتر از حد آستانه دارند از مطلوبیت تراکنش کسر می‌شود تا کران بالای گره‌های درخت بسیار فشرده‌تر و دقیق‌تر گردد.",
    dluDesc: "<strong>DLU (حذف اقلام غیرامیدبخش محلی):</strong> در درخت‌های شرطی، اقلامی که در پایگاه الگوی شرطی غیرامیدبخش هستند از مسیر حذف می‌شوند تا از حجیم‌شدن درخت جلوگیری شده و سرعت پیمایش بازگشتی چند برابر شود.",

    // Datasets
    dsEcommerce: "خرده‌فروشی آنلاین (اقلام نام‌گذاری‌شده)",
    dsFoodmart: "تراکنش‌های خواربارفروشی فودمارت (Foodmart)",
  },
};

// Global Application State
const state = {
  datasets: [],
  selectedDataset: null,
  thresholdMode: "percentage", // "percentage" or "absolute"
  currentResult: null,
  lang: localStorage.getItem("hup_lang") || "en", // "en" or "fa"
  tableState: {
    search: "",
    lengthFilter: "all",
    sortBy: "utility-desc",
    currentPage: 1,
    pageSize: 25,
    filteredPatterns: [],
  },
  charts: {
    topPatterns: null,
    scatter: null,
    kDist: null,
    funnel: null,
  },
  theme: localStorage.getItem("hup_theme") || "dark",
};

// DOM Element References
const dom = {
  langToggleBtn: document.getElementById("langToggleBtn"),
  langBtnText: document.getElementById("langBtnText"),
  themeToggleBtn: document.getElementById("themeToggleBtn"),
  datasetSelect: document.getElementById("datasetSelect"),
  navDatasetName: document.getElementById("navDatasetName"),
  briefTxCount: document.getElementById("briefTxCount"),
  briefItemsCount: document.getElementById("briefItemsCount"),
  dropzone: document.getElementById("dropzone"),
  customFileInput: document.getElementById("customFileInput"),
  uploadStatus: document.getElementById("uploadStatus"),
  dropzonePrompt: document.getElementById("dropzonePrompt"),

  thresholdModeToggle: document.getElementById("thresholdModeToggle"),
  minUtilitySlider: document.getElementById("minUtilitySlider"),
  minUtilityInput: document.getElementById("minUtilityInput"),
  thresholdUnitLabel: document.getElementById("thresholdUnitLabel"),
  effectiveAbsVal: document.getElementById("effectiveAbsVal"),
  maxLenSelect: document.getElementById("maxLenSelect"),
  runMiningBtn: document.getElementById("runMiningBtn"),

  // KPIs
  kpiTransactions: document.getElementById("kpiTransactions"),
  kpiTotalUtility: document.getElementById("kpiTotalUtility"),
  kpiPromisingItems: document.getElementById("kpiPromisingItems"),
  kpiTotalItems: document.getElementById("kpiTotalItems"),
  kpiVerifiedHuis: document.getElementById("kpiVerifiedHuis"),
  kpiCandidatesCount: document.getElementById("kpiCandidatesCount"),
  kpiTopUtility: document.getElementById("kpiTopUtility"),
  kpiTopPatternName: document.getElementById("kpiTopPatternName"),
  kpiExecutionTime: document.getElementById("kpiExecutionTime"),
  kpiPruningEff: document.getElementById("kpiPruningEff"),

  // Table & Controls
  tabCount: document.getElementById("tabCount"),
  gemsCount: document.getElementById("gemsCount"),
  patternSearchInput: document.getElementById("patternSearchInput"),
  filterLengthSelect: document.getElementById("filterLengthSelect"),
  sortBySelect: document.getElementById("sortBySelect"),
  downloadCsvBtn: document.getElementById("downloadCsvBtn"),
  patternsTableBody: document.getElementById("patternsTableBody"),
  pageStart: document.getElementById("pageStart"),
  pageEnd: document.getElementById("pageEnd"),
  pageTotal: document.getElementById("pageTotal"),
  pageSizeSelect: document.getElementById("pageSizeSelect"),
  prevPageBtn: document.getElementById("prevPageBtn"),
  nextPageBtn: document.getElementById("nextPageBtn"),
  pageCurrentDisplay: document.getElementById("pageCurrentDisplay"),

  // Tabs
  tabButtons: document.querySelectorAll(".tab-btn"),
  tabPanes: document.querySelectorAll(".tab-pane"),

  // Hidden Gems
  gemsListContainer: document.getElementById("gemsListContainer"),

  // Presets
  presetButtons: document.querySelectorAll(".preset-btn"),
};

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
  applyTheme(state.theme);
  setLanguage(state.lang, false);
  setupEventListeners();
  await loadDatasets();
});

// Setup Event Listeners
function setupEventListeners() {
  // Language Switcher Toggle
  dom.langToggleBtn.addEventListener("click", () => {
    const newLang = state.lang === "en" ? "fa" : "en";
    setLanguage(newLang, true);
  });

  // Theme Toggle
  dom.themeToggleBtn.addEventListener("click", () => {
    state.theme = state.theme === "dark" ? "light" : "dark";
    localStorage.setItem("hup_theme", state.theme);
    applyTheme(state.theme);
    updateChartTheme();
  });

  // Dataset Selection
  dom.datasetSelect.addEventListener("change", (e) => {
    onDatasetChanged(e.target.value);
  });

  // Threshold Mode Segmented Toggle
  dom.thresholdModeToggle.querySelectorAll(".segment-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const mode = btn.dataset.mode;
      if (mode !== state.thresholdMode) {
        setThresholdMode(mode);
      }
    });
  });

  // Slider & Number Input Sync
  dom.minUtilitySlider.addEventListener("input", (e) => {
    dom.minUtilityInput.value = e.target.value;
    updateEffectivePreview();
  });

  dom.minUtilityInput.addEventListener("input", (e) => {
    dom.minUtilitySlider.value = e.target.value;
    updateEffectivePreview();
  });

  // Threshold Preset Buttons
  dom.presetButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      dom.presetButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      applyPreset(btn.dataset.preset);
    });
  });

  // Run Mining Button
  dom.runMiningBtn.addEventListener("click", runMining);

  // Custom File Upload
  dom.dropzone.addEventListener("click", () => dom.customFileInput.click());
  dom.customFileInput.addEventListener("change", handleFileUpload);

  // Drag & drop handlers
  ["dragenter", "dragover"].forEach((eventName) => {
    dom.dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dom.dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dom.dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dom.dropzone.classList.remove("dragover");
    });
  });

  dom.dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadFile(files[0]);
    }
  });

  // Tabs Navigation
  dom.tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.tab;
      dom.tabButtons.forEach((b) => b.classList.remove("active"));
      dom.tabPanes.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");

      // Trigger resize on charts when tab becomes visible
      if (targetId === "tab-analytics") {
        resizeCharts();
      }
    });
  });

  // Table Controls
  dom.patternSearchInput.addEventListener("input", (e) => {
    state.tableState.search = e.target.value.trim().toLowerCase();
    state.tableState.currentPage = 1;
    applyTableFilterAndRender();
  });

  dom.filterLengthSelect.addEventListener("change", (e) => {
    state.tableState.lengthFilter = e.target.value;
    state.tableState.currentPage = 1;
    applyTableFilterAndRender();
  });

  dom.sortBySelect.addEventListener("change", (e) => {
    state.tableState.sortBy = e.target.value;
    applyTableFilterAndRender();
  });

  dom.pageSizeSelect.addEventListener("change", (e) => {
    state.tableState.pageSize = parseInt(e.target.value, 10);
    state.tableState.currentPage = 1;
    applyTableFilterAndRender();
  });

  dom.prevPageBtn.addEventListener("click", () => {
    if (state.tableState.currentPage > 1) {
      state.tableState.currentPage--;
      renderTable();
    }
  });

  dom.nextPageBtn.addEventListener("click", () => {
    const maxPage = Math.ceil(
      state.tableState.filteredPatterns.length / state.tableState.pageSize
    );
    if (state.tableState.currentPage < maxPage) {
      state.tableState.currentPage++;
      renderTable();
    }
  });

  // Download CSV
  dom.downloadCsvBtn.addEventListener("click", downloadCsv);
}

// Set Application Language (EN / FA)
function setLanguage(lang, rerender = true) {
  state.lang = lang;
  localStorage.setItem("hup_lang", lang);

  const isRTL = lang === "fa";
  document.documentElement.setAttribute("lang", lang);
  document.documentElement.setAttribute("dir", isRTL ? "rtl" : "ltr");

  dom.langBtnText.textContent = I18N[lang].langName;

  // Translate all elements with data-i18n
  const dict = I18N[lang];
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.innerHTML = dict[key];
    }
  });

  // Translate placeholders
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key]) {
      el.placeholder = dict[key];
    }
  });

  // Translate Dataset Options
  updateDatasetSelectOptions();

  // Update Dynamic Text and Previews
  updateEffectivePreview();

  if (rerender && state.currentResult) {
    updateKPIs(state.currentResult);
    applyTableFilterAndRender();
    updateCharts(state.currentResult);
    updateHiddenGems(state.currentResult.hidden_gems);
  }
}

// Update Dataset Dropdown Options with Localized Names
function updateDatasetSelectOptions() {
  const isFa = state.lang === "fa";
  Array.from(dom.datasetSelect.options).forEach((opt) => {
    if (opt.value === "ecommerce_utility") {
      opt.textContent = isFa ? I18N.fa.dsEcommerce : I18N.en.dsEcommerce;
    } else if (opt.value === "foodmart_utility") {
      opt.textContent = isFa ? I18N.fa.dsFoodmart : I18N.en.dsFoodmart;
    }
  });

  if (state.selectedDataset) {
    dom.navDatasetName.textContent = getLocalizedDatasetName(state.selectedDataset.dataset_id, state.selectedDataset.name);
  }
}

function getLocalizedDatasetName(datasetId, fallbackName) {
  if (state.lang === "fa") {
    if (datasetId === "ecommerce_utility") return I18N.fa.dsEcommerce;
    if (datasetId === "foodmart_utility") return I18N.fa.dsFoodmart;
  }
  return fallbackName;
}

// Apply Theme
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
}

// Load Datasets List
async function loadDatasets() {
  try {
    const res = await fetch("/api/datasets");
    const data = await res.json();
    state.datasets = data.datasets || [];

    dom.datasetSelect.innerHTML = "";
    state.datasets.forEach((ds) => {
      const opt = document.createElement("option");
      opt.value = ds.dataset_id;
      opt.textContent = getLocalizedDatasetName(ds.dataset_id, ds.name);
      dom.datasetSelect.appendChild(opt);
    });

    if (state.datasets.length > 0) {
      onDatasetChanged(state.datasets[0].dataset_id);
      // Run automatic initial mining for quick onboarding
      runMining();
    }
  } catch (err) {
    console.error("Failed to load datasets:", err);
  }
}

// Dataset Changed
function onDatasetChanged(datasetId) {
  const ds = state.datasets.find((d) => d.dataset_id === datasetId);
  if (!ds) return;

  state.selectedDataset = ds;
  dom.navDatasetName.textContent = getLocalizedDatasetName(ds.dataset_id, ds.name);
  const txWord = state.lang === "fa" ? "تراکنش" : "txs";
  const itemWord = state.lang === "fa" ? "قلم‌کالا" : "items";
  dom.briefTxCount.textContent = `${ds.total_transactions.toLocaleString()} ${txWord}`;
  dom.briefItemsCount.textContent = `${ds.unique_items.toLocaleString()} ${itemWord}`;

  // Reset preset button
  dom.presetButtons.forEach((b) => b.classList.remove("active"));
  const defaultPresetBtn = document.querySelector('.preset-btn[data-preset="default"]');
  if (defaultPresetBtn) defaultPresetBtn.classList.add("active");

  applyPreset("default");
}

// Set Threshold Mode (Percentage vs Absolute)
function setThresholdMode(mode) {
  state.thresholdMode = mode;
  dom.thresholdModeToggle.querySelectorAll(".segment-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });

  const ds = state.selectedDataset;
  if (!ds) return;

  if (mode === "percentage") {
    dom.thresholdUnitLabel.textContent = "%";
    dom.minUtilitySlider.min = "0.01";
    dom.minUtilitySlider.max = "3.0";
    dom.minUtilitySlider.step = "0.01";
    dom.minUtilityInput.step = "0.01";

    const sugPct = ds.suggested_min_utility_pct || 0.35;
    dom.minUtilitySlider.value = sugPct;
    dom.minUtilityInput.value = sugPct;
  } else {
    dom.thresholdUnitLabel.textContent = state.lang === "fa" ? "مطلوبیت" : "utility";
    const totalU = ds.total_utility;
    const maxVal = Math.round(totalU * 0.05);
    dom.minUtilitySlider.min = "100";
    dom.minUtilitySlider.max = maxVal.toString();
    dom.minUtilitySlider.step = "100";
    dom.minUtilityInput.step = "100";

    const sugAbs = ds.suggested_min_utility_abs || Math.round(totalU * 0.0035);
    dom.minUtilitySlider.value = sugAbs;
    dom.minUtilityInput.value = sugAbs;
  }

  updateEffectivePreview();
}

// Preset Handler
function applyPreset(preset) {
  const ds = state.selectedDataset;
  if (!ds) return;

  const basePct = ds.suggested_min_utility_pct || 0.35;
  let targetPct = basePct;

  if (preset === "low") {
    targetPct = Math.max(0.02, +(basePct * 0.6).toFixed(3));
  } else if (preset === "high") {
    targetPct = +(basePct * 1.8).toFixed(3);
  } else {
    targetPct = basePct;
  }

  if (state.thresholdMode === "percentage") {
    dom.minUtilitySlider.value = targetPct;
    dom.minUtilityInput.value = targetPct;
  } else {
    const absVal = Math.round(ds.total_utility * (targetPct / 100.0));
    dom.minUtilitySlider.value = absVal;
    dom.minUtilityInput.value = absVal;
  }

  updateEffectivePreview();
}

// Update Effective Absolute Utility Preview Text
function updateEffectivePreview() {
  const ds = state.selectedDataset;
  if (!ds) return;

  const isFa = state.lang === "fa";
  const inputVal = parseFloat(dom.minUtilityInput.value) || 0;
  if (state.thresholdMode === "percentage") {
    const absVal = (inputVal / 100.0) * ds.total_utility;
    const unit = isFa ? "واحد مطلوبیت" : "utility";
    dom.effectiveAbsVal.textContent = `≈ ${absVal.toLocaleString(undefined, {
      maximumFractionDigits: 1,
    })} ${unit}`;
  } else {
    const pctVal = (inputVal / ds.total_utility) * 100.0;
    const desc = isFa ? "٪ از کل مطلوبیت پایگاه‌داده" : "% of total utility";
    dom.effectiveAbsVal.textContent = `≈ ${pctVal.toFixed(3)}${desc}`;
  }
}

// Execute Mining Algorithm via Backend API
async function runMining() {
  const ds = state.selectedDataset;
  if (!ds) return;

  const minUtilVal = parseFloat(dom.minUtilityInput.value);
  if (isNaN(minUtilVal) || minUtilVal <= 0) {
    alert(state.lang === "fa" ? "لطفاً یک مقدار آستانه معتبر و مثبت وارد کنید." : "Please specify a valid positive threshold.");
    return;
  }

  const maxLenVal = parseInt(dom.maxLenSelect.value, 10);

  // Set button loading state
  dom.runMiningBtn.disabled = true;
  dom.runMiningBtn.querySelector(".btn-text").style.display = "none";
  dom.runMiningBtn.querySelector(".btn-spinner").style.display = "flex";

  try {
    const res = await fetch("/api/mine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataset_id: ds.dataset_id,
        min_utility: minUtilVal,
        threshold_mode: state.thresholdMode,
        max_len: maxLenVal,
      }),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Mining failed");
    }

    const data = await res.json();
    state.currentResult = data;

    // Update Dashboard UI
    updateKPIs(data);
    updatePatternsTable(data.patterns);
    updateCharts(data);
    updateHiddenGems(data.hidden_gems);
  } catch (err) {
    console.error("Mining error:", err);
    alert(`Error: ${err.message}`);
  } finally {
    dom.runMiningBtn.disabled = false;
    dom.runMiningBtn.querySelector(".btn-text").style.display = "flex";
    dom.runMiningBtn.querySelector(".btn-spinner").style.display = "none";
  }
}

// Update KPI Display Cards
function updateKPIs(data) {
  const kpis = data.kpis;
  const diag = data.diagnostics;
  const isFa = state.lang === "fa";

  dom.kpiTransactions.textContent = kpis.total_transactions.toLocaleString();
  dom.kpiTotalUtility.textContent = isFa
    ? `مطلوبیت کل: ${kpis.total_database_utility.toLocaleString()}`
    : `Total Utility: ${kpis.total_database_utility.toLocaleString()}`;

  dom.kpiPromisingItems.textContent = diag.promising_items_count.toLocaleString();
  dom.kpiTotalItems.textContent = isFa
    ? `از مجموع ${diag.total_items_count.toLocaleString()} قلم کالا`
    : `from ${diag.total_items_count.toLocaleString()} total items`;

  dom.kpiVerifiedHuis.textContent = diag.phase2_verified_count.toLocaleString();
  dom.kpiCandidatesCount.textContent = isFa
    ? `از میان ${diag.phase1_candidates_count.toLocaleString()} کاندید فاز ۱`
    : `from ${diag.phase1_candidates_count.toLocaleString()} Phase 1 PHUIs`;

  dom.kpiTopUtility.textContent = kpis.top_pattern_utility.toLocaleString();
  dom.kpiTopPatternName.textContent = kpis.top_pattern_name;

  dom.kpiExecutionTime.textContent = `${diag.total_ms} ms`;
  dom.kpiPruningEff.textContent = isFa
    ? `نرخ هرس: ${diag.pruning_efficiency_pct}٪`
    : `Pruned: ${diag.pruning_efficiency_pct}%`;

  dom.tabCount.textContent = data.patterns.length;
}

// Update Patterns Table
function updatePatternsTable(patterns) {
  state.tableState.currentPage = 1;
  applyTableFilterAndRender();
}

function applyTableFilterAndRender() {
  if (!state.currentResult) return;

  let list = [...state.currentResult.patterns];

  // 1. Search Query Filter
  if (state.tableState.search) {
    const q = state.tableState.search;
    list = list.filter((h) => {
      return (
        h.pattern_names.some((name) => name.toLowerCase().includes(q)) ||
        h.pattern.some((id) => id.toString().includes(q))
      );
    });
  }

  // 2. Length Filter
  if (state.tableState.lengthFilter !== "all") {
    const targetK = parseInt(state.tableState.lengthFilter, 10);
    if (targetK === 5) {
      list = list.filter((h) => h.length >= 5);
    } else {
      list = list.filter((h) => h.length === targetK);
    }
  }

  // 3. Sorting
  const sortMode = state.tableState.sortBy;
  list.sort((a, b) => {
    switch (sortMode) {
      case "utility-desc":
        return b.exact_utility - a.exact_utility;
      case "utility-asc":
        return a.exact_utility - b.exact_utility;
      case "support-desc":
        return b.support_count - a.support_count;
      case "avg-desc":
        return b.avg_utility_per_tx - a.avg_utility_per_tx;
      case "length-desc":
        return b.length - a.length;
      default:
        return b.exact_utility - a.exact_utility;
    }
  });

  state.tableState.filteredPatterns = list;
  renderTable();
}

function renderTable() {
  const patterns = state.tableState.filteredPatterns;
  const tbody = dom.patternsTableBody;
  tbody.innerHTML = "";

  const isFa = state.lang === "fa";

  if (patterns.length === 0) {
    const msg = isFa ? I18N.fa.tableNoMatch : I18N.en.tableNoMatch;
    tbody.innerHTML = `<tr><td colspan="8" class="empty-state">${msg}</td></tr>`;
    dom.pageStart.textContent = "0";
    dom.pageEnd.textContent = "0";
    dom.pageTotal.textContent = "0";
    dom.pageCurrentDisplay.textContent = isFa ? "صفحه ۰ از ۰" : "Page 0 of 0";
    dom.prevPageBtn.disabled = true;
    dom.nextPageBtn.disabled = true;
    return;
  }

  const { currentPage, pageSize } = state.tableState;
  const maxPage = Math.ceil(patterns.length / pageSize);
  const startIdx = (currentPage - 1) * pageSize;
  const endIdx = Math.min(startIdx + pageSize, patterns.length);
  const pageItems = patterns.slice(startIdx, endIdx);

  const maxUtilInResult = state.currentResult.patterns[0]?.exact_utility || 1.0;

  pageItems.forEach((h, idx) => {
    const rowIdx = startIdx + idx + 1;
    const tr = document.createElement("tr");

    // Item pills
    const badgesHtml = h.pattern_names
      .map(
        (name, i) =>
          `<span class="item-pill" title="ID: ${h.pattern[i]}">${escapeHtml(
            name
          )}</span>`
      )
      .join('<span class="item-plus">+</span>');

    const barPct = Math.min(100, (h.exact_utility / maxUtilInResult) * 100);

    tr.innerHTML = `
      <td class="col-index mono-val">${rowIdx}</td>
      <td class="col-k"><span class="k-badge">k = ${h.length}</span></td>
      <td><div class="pattern-badges-wrap">${badgesHtml}</div></td>
      <td class="mono-val">${h.support_count.toLocaleString()}</td>
      <td class="mono-val">${h.support_pct.toFixed(2)}%</td>
      <td>
        <div class="util-cell-wrap">
          <span class="util-val-text">${h.exact_utility.toLocaleString()}</span>
          <div class="util-bar-track">
            <div class="util-bar-fill" style="width: ${barPct}%;"></div>
          </div>
        </div>
      </td>
      <td class="mono-val">${h.avg_utility_per_tx.toLocaleString(undefined, {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      })}</td>
      <td class="mono-val">${h.utility_share_pct.toFixed(2)}%</td>
    `;
    tbody.appendChild(tr);
  });

  // Update Pagination Controls
  dom.pageStart.textContent = (startIdx + 1).toLocaleString();
  dom.pageEnd.textContent = endIdx.toLocaleString();
  dom.pageTotal.textContent = patterns.length.toLocaleString();
  dom.pageCurrentDisplay.textContent = isFa
    ? `صفحه ${currentPage} از ${maxPage}`
    : `Page ${currentPage} of ${maxPage}`;
  dom.prevPageBtn.disabled = currentPage <= 1;
  dom.nextPageBtn.disabled = currentPage >= maxPage;
}

// Download Table Patterns as CSV
function downloadCsv() {
  const patterns = state.tableState.filteredPatterns;
  if (!patterns || patterns.length === 0) {
    alert(state.lang === "fa" ? "هیچ الگویی برای خروجی وجود ندارد." : "No patterns available to export.");
    return;
  }

  const headers = [
    "rank",
    "k_size",
    "item_ids",
    "item_names",
    "support_count",
    "support_pct",
    "exact_utility",
    "avg_utility_per_tx",
    "utility_share_pct",
  ];

  const rows = patterns.map((h, i) => [
    i + 1,
    h.length,
    `"${h.pattern.join(", ")}"`,
    `"${h.pattern_names.join(" + ").replace(/"/g, '""')}"`,
    h.support_count,
    h.support_pct,
    h.exact_utility,
    h.avg_utility_per_tx,
    h.utility_share_pct,
  ]);

  const csvContent =
    "data:text/csv;charset=utf-8," +
    [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  const dsName = state.selectedDataset ? state.selectedDataset.dataset_id : "huim";
  link.setAttribute("download", `${dsName}_high_utility_patterns.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Update Chart.js Visualizations
function updateCharts(data) {
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";
  const textColor = isDark ? "#9CA3AF" : "#475569";
  const isFa = state.lang === "fa";
  const dict = I18N[state.lang];

  // 1. Top Patterns Chart (Horizontal Bar Chart)
  const topData = data.top_patterns_chart;
  if (state.charts.topPatterns) state.charts.topPatterns.destroy();

  const ctxTop = document.getElementById("topPatternsChartCanvas").getContext("2d");
  state.charts.topPatterns = new Chart(ctxTop, {
    type: "bar",
    data: {
      labels: topData.labels,
      datasets: [
        {
          label: dict.chartUtilAxisLabel,
          data: topData.utilities,
          backgroundColor: "rgba(99, 102, 241, 0.8)",
          borderColor: "#6366F1",
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => topData.full_names[items[0].dataIndex] || items[0].label,
            afterLabel: (item) => {
              const supWord = isFa ? "تکرار پشتیبان" : "Support";
              const orderWord = isFa ? "سفارش" : "orders";
              return `${supWord}: ${topData.supports[item.dataIndex]} ${orderWord} (${topData.support_pcts[item.dataIndex]}%)`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor },
        },
        y: {
          grid: { display: false },
          ticks: { color: textColor, font: { size: 11 } },
        },
      },
    },
  });

  // 2. Scatter Plot: Support % vs Exact Utility
  const scatterData = data.scatter_data;
  if (state.charts.scatter) state.charts.scatter.destroy();

  const ctxScatter = document.getElementById("scatterChartCanvas").getContext("2d");
  state.charts.scatter = new Chart(ctxScatter, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: isFa ? "مجموعه‌آیتم‌ها" : "Itemsets",
          data: scatterData.map((d) => ({ x: d.x, y: d.y, raw: d })),
          backgroundColor: "rgba(16, 185, 129, 0.75)",
          borderColor: "#10B981",
          borderWidth: 1,
          pointRadius: 6,
          pointHoverRadius: 9,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const raw = ctx.raw.raw;
              if (isFa) {
                return [
                  `الگو: ${raw.label}`,
                  `مطلوبیت: ${raw.y.toLocaleString()}`,
                  `پشتیبان: ${raw.support_count} (${raw.x}٪)`,
                  `میانگین در سفارش: ${raw.avg_utility}`,
                ];
              }
              return [
                `Pattern: ${raw.label}`,
                `Utility: ${raw.y.toLocaleString()}`,
                `Support: ${raw.support_count} (${raw.x}%)`,
                `Avg/Tx: ${raw.avg_utility}`,
              ];
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: dict.chartSupportAxisLabel, color: textColor },
          grid: { color: gridColor },
          ticks: { color: textColor },
        },
        y: {
          title: { display: true, text: dict.chartUtilAxisLabel, color: textColor },
          grid: { color: gridColor },
          ticks: { color: textColor },
        },
      },
    },
  });

  // 3. Pattern Size (k) Distribution Bar Chart
  const kDist = data.k_distribution;
  if (state.charts.kDist) state.charts.kDist.destroy();

  const ctxK = document.getElementById("kDistChartCanvas").getContext("2d");
  state.charts.kDist = new Chart(ctxK, {
    type: "bar",
    data: {
      labels: kDist.labels,
      datasets: [
        {
          label: dict.chartItemsetsAxisLabel,
          data: kDist.counts,
          backgroundColor: "rgba(139, 92, 246, 0.8)",
          borderColor: "#8B5CF6",
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: textColor } },
        y: { grid: { color: gridColor }, ticks: { color: textColor } },
      },
    },
  });

  // 4. Two-Phase Pruning Funnel
  const funnel = data.pruning_funnel;
  if (state.charts.funnel) state.charts.funnel.destroy();

  const ctxFunnel = document.getElementById("pruningFunnelChartCanvas").getContext("2d");
  state.charts.funnel = new Chart(ctxFunnel, {
    type: "bar",
    data: {
      labels: [
        dict.funnelStep1,
        dict.funnelStep2,
        dict.funnelStep3,
        dict.funnelStep4,
      ],
      datasets: [
        {
          label: isFa ? "تعداد نامزدها" : "Candidate Count",
          data: [
            funnel.total_items,
            funnel.promising_items,
            funnel.phase1_candidates,
            funnel.phase2_verified,
          ],
          backgroundColor: [
            "rgba(59, 130, 246, 0.7)",
            "rgba(139, 92, 246, 0.7)",
            "rgba(245, 158, 11, 0.7)",
            "rgba(16, 185, 129, 0.85)",
          ],
          borderColor: ["#3B82F6", "#8B5CF6", "#F59E0B", "#10B981"],
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: textColor, font: { size: 11 } } },
        y: {
          type: "logarithmic",
          grid: { color: gridColor },
          ticks: { color: textColor },
        },
      },
    },
  });
}

function updateChartTheme() {
  if (state.currentResult) {
    updateCharts(state.currentResult);
  }
}

function resizeCharts() {
  Object.values(state.charts).forEach((chart) => {
    if (chart) chart.resize();
  });
}

// Update Hidden Gems Cards
function updateHiddenGems(gems) {
  const container = dom.gemsListContainer;
  container.innerHTML = "";

  const isFa = state.lang === "fa";
  const dict = I18N[state.lang];
  dom.gemsCount.textContent = (gems || []).length;

  if (!gems || gems.length === 0) {
    container.innerHTML = `<div class="empty-state">${dict.gemsEmptyState}</div>`;
    return;
  }

  gems.forEach((gem, idx) => {
    const card = document.createElement("div");
    card.className = "gem-card";

    const gemTagText = isFa ? `💎 گوهر پنهان #${idx + 1}` : `💎 Hidden Gem #${idx + 1}`;
    const scoreText = `${dict.gemScoreLabel} ${gem.gem_ratio}x`;

    const insightText = isFa
      ? `نرخ رخداد پایین (تنها در ${gem.support_pct}٪ از کل تراکنش‌ها)، اما تولیدکننده ${gem.exact_utility.toLocaleString()} مطلوبیت سودآور (میانگین ${gem.avg_utility_per_tx.toLocaleString()} به ازای هر سفارش). الگوریتم سنتی FP-Growth این الگو را به اشتباه به عنوان کم‌تکرار دور می‌انداخت!`
      : gem.insight;

    card.innerHTML = `
      <div class="gem-header">
        <span class="gem-tag">${gemTagText}</span>
        <span class="gem-ratio-score">${scoreText}</span>
      </div>
      <div class="gem-pattern-name">${escapeHtml(gem.pattern_str)}</div>
      <div class="gem-metrics-row">
        <div class="gem-metric-item">
          <span>${dict.gemSupportLabel}</span>
          <span>${gem.support_count} (${gem.support_pct}%)</span>
        </div>
        <div class="gem-metric-item">
          <span>${dict.gemExactUtilLabel}</span>
          <span>${gem.exact_utility.toLocaleString()}</span>
        </div>
        <div class="gem-metric-item">
          <span>${dict.gemAvgOrderLabel}</span>
          <span>${gem.avg_utility_per_tx.toLocaleString()}</span>
        </div>
      </div>
      <div class="gem-insight">${escapeHtml(insightText)}</div>
    `;
    container.appendChild(card);
  });
}

// Handle Custom File Upload
function handleFileUpload(e) {
  const file = e.target.files[0];
  if (file) {
    uploadFile(file);
  }
}

async function uploadFile(file) {
  const isFa = state.lang === "fa";
  const formData = new FormData();
  formData.append("file", file);

  dom.dropzonePrompt.style.display = "none";
  dom.uploadStatus.style.display = "block";
  dom.uploadStatus.textContent = isFa
    ? `در حال بارگذاری و تحلیل ${file.name}...`
    : `Uploading & parsing ${file.name}...`;

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Upload failed");
    }

    const data = await res.json();
    dom.uploadStatus.textContent = isFa
      ? `✓ دیتاست ${data.dataset.name} با موفقیت بارگذاری شد`
      : `✓ Loaded ${data.dataset.name}`;

    // Add to datasets list and select
    state.datasets.push(data.dataset);
    const opt = document.createElement("option");
    opt.value = data.dataset.dataset_id;
    opt.textContent = data.dataset.name;
    dom.datasetSelect.appendChild(opt);
    dom.datasetSelect.value = data.dataset.dataset_id;

    onDatasetChanged(data.dataset.dataset_id);
    runMining();
  } catch (err) {
    dom.uploadStatus.textContent = `${isFa ? "خطا در بارگذاری: " : "Upload error: "} ${err.message}`;
    dom.uploadStatus.style.color = "var(--accent-rose)";
    console.error("Upload error:", err);
  } finally {
    setTimeout(() => {
      dom.dropzonePrompt.style.display = "flex";
      dom.uploadStatus.style.display = "none";
      dom.uploadStatus.style.color = "var(--accent-emerald)";
    }, 4000);
  }
}

// Utility: HTML Escaping
function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
