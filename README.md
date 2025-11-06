# AWS Product Usage — Data Visualization Project

This mini-project turns your **Amazon AWS product data** into a clean, repeatable visualization workflow you can run locally or in GitHub Codespaces.

## What’s inside
- `aws_product_viz.ipynb` – an interactive notebook with step‑by‑step EDA & charts
- `make_charts.py` – a runnable script that saves PNG charts to `figures/`
- `requirements.txt` – lightweight deps (pandas + matplotlib + numpy + jupyter)
- `figures/` – images output folder (created by the script)
- `data-sets/` – **put your CSVs here** (or symlink to your existing `product-data-sets/data-sets` folder)

## Expected columns (the code is resilient, but these help unlock all charts)
- `date` – daily or monthly timestamp
- `product` – product name/sku
- `account_id` or `user_id` – (optional) enables cohort/retention analysis
- `region` – (optional) for geo drilldowns
- Usage/value columns like: `requests`, `active_users`, `revenue`, `cost`, `duration`, `gb`, `errors`

> If your CSVs use different names, the notebook shows how to map them in one place.

## Quickstart (Local)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Put CSVs into data-sets/ (or edit paths)
python make_charts.py  # saves charts into figures/
# OR open the notebook
jupyter lab aws_product_viz.ipynb
```

## Quickstart (GitHub Codespaces)
1. Open this folder in a Codespace.
2. In the terminal:
   ```bash
   pip install -r requirements.txt
   python make_charts.py
   ```

## Suggested repo path
Add this folder to your repo under:
```
product-data-sets/projects/aws-product-viz/
```

---

## Portfolio‑ready screenshots
After running `make_charts.py`, upload the PNGs from `figures/` to your README or GitHub Pages. Aim to include:
- Top products by revenue/usage (bar)
- Trend of total usage/revenue (line)
- Product mix over time (stacked area)
- Error rate vs. traffic (scatter)
- Cohort retention heatmap (if `user_id` + `date` exists)

## License & credit
MIT • Created by Brenda S. Elazab. Feel free to fork and adapt.
