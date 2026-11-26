# ID3-Gini Decision Tree Classifier & Analytics Studio

A pure-Python implementation of the **ID3 Decision Tree Classifier using the Gini Index split criterion** (`ID3-Gini`), grounded in *Chapter 6 of "Data Mining: Concepts and Techniques" (Han, Pei, Tong)*, paired with a FastAPI REST backend and an interactive HTML5/CSS3/Vanilla JS + D3.js visualization dashboard.

## Mathematical Foundation

Unlike standard ID3 (which uses Information Gain) or CART (which performs binary splits with Gini), **ID3-Gini** retains ID3's **multiway discrete attribute splitting** (removing each chosen attribute from child candidate lists) while using **Gini impurity reduction** as the attribute selection measure:

1. **Node Impurity** for partition $D$ over $n$ classes with relative frequencies $p_j = \frac{|C_{j,D}|}{|D|}$:
   $$\text{Gini}(D) = 1 - \sum_{j=1}^{n} p_j^2$$

2. **Weighted Split Impurity** for discrete attribute $A$ with distinct values $v \in \text{values}(A)$:
   $$\text{Gini}_A(D) = \sum_{v \in \text{values}(A)} \frac{|D_v|}{|D|} \text{Gini}(D_v)$$

3. **Gini Impurity Reduction**:
   $$\Delta\text{Gini}(A) = \text{Gini}(D) - \text{Gini}_A(D)$$

At each internal node, the classifier selects the candidate attribute $A^*$ minimizing $\text{Gini}_A(D)$ (equivalently maximizing $\Delta\text{Gini}(A)$).

## Key Engineering Features

- **Column-Count Independence**: Dynamically adapts to any discrete/categorical CSV dataset with any number of feature columns and any user-selected target column.
- **Header & Target Auto-Detection**: Automatically assigns standard column names (`['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety', 'class']`) when headerless `car_evaluation.csv` is loaded, auto-detects `class` / `target` / `label` columns (including col 0 in `mushrooms.csv`), and supports full user override.
- **Zero External ML Tree Dependencies**: Impurity engine, stratified train/test splitter, recursive tree induction, unseen-value majority fallback, IF-THEN rule extraction, and confusion matrix / macro F1 evaluation are written from scratch in pure Python.
- **Interactive Analytics Dashboard**:
  - Pan & zoom collapsible D3.js tree diagram with node inspector and predicted-path highlighting
  - Dynamic Live Sample Predictor form generated from active dataset columns
  - Confusion Matrix heatmap & per-class Precision / Recall / F1 table
  - Searchable, downloadable (`TXT` / `CSV`) IF-THEN rule explorer
  - Dark / Light theme toggle

## Project Structure

```text
ID3-Gini-DecisionTree/
├── datasets/
│   ├── car_evaluation.csv     # 6 features, 4 classes (unacc, acc, good, vgood)
│   └── mushrooms.csv          # 22 features, 2 classes (e, p)
├── src/
│   ├── __init__.py
│   ├── loader.py              # Dynamic CSV loader, header auto-check, stratified split
│   ├── gini.py                # Gini(D), Gini_A(D), and ΔGini(A) engine
│   ├── id3_tree.py            # Recursive ID3-Gini classifier, prediction trace & rules
│   └── evaluator.py           # Pure-Python accuracy, precision/recall/F1 & confusion matrix
├── static/
│   ├── index.html             # Single-page analytics & tree visualization dashboard
│   ├── styles.css             # Custom responsive CSS3 (Dark/Light mode)
│   └── app.js                 # Fetch API integration, D3.js tree viewer, live predictor
├── tests/
│   └── test_id3_gini.py       # Unit & FastAPI integration test suite
├── app.py                     # FastAPI backend & static asset server
├── requirements.txt
└── README.md
```

## Setup & Running

1. Install dependencies (or activate the project virtual environment):
   ```bash
   pip install -r requirements.txt
   ```

2. Run the automated test suite:
   ```bash
   pytest tests/test_id3_gini.py -v
   ```

3. Start the FastAPI web server:
   ```bash
   uvicorn app:app --reload
   ```
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## REST API Endpoints

- `GET /api/datasets` — Lists built-in and uploaded CSV datasets with columns, row counts, default target, and unique values per column.
- `POST /api/upload` — Uploads a custom `.csv` file with any number of discrete columns.
- `POST /api/train` — Trains `ID3GiniClassifier` with configurable `dataset_id`, `target_column`, `test_size`, `random_seed`, `max_depth`, and `min_samples_split`.
- `POST /api/predict` — Predicts the class for a JSON feature dictionary and returns the root-to-leaf decision path.
