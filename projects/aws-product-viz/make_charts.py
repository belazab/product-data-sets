#!/usr/bin/env python3
"""
AWS Product Data — quick charts
Run: python make_charts.py
Assumes CSVs are in ./data-sets/*.csv (you can change DATA_GLOB below).
Saves figures into ./figures/
"""
import glob, os, math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DATA_GLOB = os.environ.get("AWS_DATA_GLOB", "data-sets/*.csv")
OUT_DIR = "figures"
os.makedirs(OUT_DIR, exist_ok=True)

def load_all(glob_path):
    files = glob.glob(glob_path)
    if not files:
        raise SystemExit(f"No CSV files found at {glob_path}. Put your files under data-sets/ or set AWS_DATA_GLOB.")
    frames = []
    for f in files:
        try:
            df = pd.read_csv(f)
        except UnicodeDecodeError:
            df = pd.read_csv(f, encoding="utf-8-sig")
        df["__source_file"] = os.path.basename(f)
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    return df

def standardize_columns(df):
    # Lowercase, strip spaces, unify common names
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # Try to infer common fields
    colmap = {}
    # date
    for cand in ["date", "day", "timestamp", "ds"]:
        if cand in df.columns:
            colmap["date"] = cand; break
    # product
    for cand in ["product", "service", "sku", "feature"]:
        if "product" in colmap: break
        if cand in df.columns:
            colmap["product"] = cand; break
    # user/account id
    for cand in ["user_id", "account_id", "customer_id", "client_id"]:
        if cand in df.columns:
            colmap["user_id"] = cand; break
    # region
    for cand in ["region", "geo", "country", "market"]:
        if cand in df.columns:
            colmap["region"] = cand; break
    # value fields
    numeric_candidates = [c for c in df.columns if df[c].dtype.kind in "if"]
    # helpful aliases for value columns if exist
    for name, aliases in {
        "revenue": ["revenue", "amount", "gmv", "arr", "mrr", "net_sales"],
        "cost": ["cost", "cogs", "expense"],
        "requests": ["requests", "calls", "api_calls", "hits"],
        "active_users": ["active_users", "maus", "daus", "users_active"],
        "errors": ["errors", "error_count", "failures"],
        "duration": ["duration", "time_sec", "time_ms", "latency_ms", "latency"],
        "gb": ["gb", "gigabytes", "data_gb", "bandwidth_gb"]
    }.items():
        for a in aliases:
            if a in df.columns:
                colmap[name] = a; break

    # Apply mappings via a normalized dataframe
    out = df.rename(columns=colmap)
    # Parse date if present
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return out

def safe_sum(series):
    return pd.to_numeric(series, errors="coerce").fillna(0).sum()

def plot_bar(series, title, fname):
    plt.figure()
    series.sort_values(ascending=False)[:10].plot(kind="bar")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, fname))
    plt.close()

def plot_line(df, x, y, title, fname):
    plt.figure()
    g = df.groupby(x)[y].sum().sort_index()
    g.plot(kind="line")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, fname))
    plt.close()

def plot_stacked_area(df, x, stack, y, title, fname):
    pivot = df.pivot_table(index=x, columns=stack, values=y, aggfunc="sum").fillna(0).sort_index()
    plt.figure()
    pivot.plot(kind="area", stacked=True)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, fname))
    plt.close()

def plot_scatter(df, x, y, title, fname):
    plt.figure()
    plt.scatter(df[x], df[y])
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, fname))
    plt.close()

def cohort_heatmap(df, user_col="user_id", date_col="date", fname="cohort_retention.png"):
    # Requires user_id + date
    if user_col not in df or date_col not in df:
        return
    d = df[[user_col, date_col]].dropna().copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d["month"] = d[date_col].dt.to_period("M").dt.to_timestamp()
    first = d.groupby(user_col)["month"].min()
    d = d.join(first, on=user_col, rsuffix="_first")
    d["cohort"] = d["month_first"]
    d["period"] = ((d["month"] - d["cohort"]) / np.timedelta64(1, "M")).round().astype(int)
    cohort = d.groupby(["cohort", "period"])[user_col].nunique().unstack(fill_value=0)
    # Normalize by cohort size
    cohort_size = cohort.iloc[:, 0].replace(0, 1)
    retention = cohort.divide(cohort_size, axis=0)
    # Simple imshow without explicit colors
    import matplotlib.pyplot as plt
    plt.figure()
    plt.imshow(retention.values, aspect='auto')
    plt.title("Cohort Retention (users)")
    plt.xlabel("Months since first month")
    plt.ylabel("Cohort (YYYY-MM)")
    plt.yticks(range(len(retention.index)), [c.strftime("%Y-%m") for c in retention.index])
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, fname))
    plt.close()

def main():
    df = load_all(DATA_GLOB)
    df = standardize_columns(df)

    # Basic summaries
    # Top products by revenue/usage
    if "product" in df.columns:
        if "revenue" in df.columns:
            plot_bar(df.groupby("product")["revenue"].sum(), "Top Products by Revenue", "top_products_revenue.png")
        # try to find a generic usage column
        usage_col = None
        for c in ["requests", "active_users", "gb", "duration"]:
            if c in df.columns:
                usage_col = c; break
        if usage_col:
            plot_bar(df.groupby("product")[usage_col].sum(), f"Top Products by {usage_col}", f"top_products_{usage_col}.png")

    # Trend lines
    if "date" in df.columns:
        if "revenue" in df.columns:
            plot_line(df, "date", "revenue", "Revenue over Time", "revenue_trend.png")
        for c in ["requests", "active_users"]:
            if c in df.columns:
                plot_line(df, "date", c, f"{c} over Time", f"{c}_trend.png")

    # Product mix over time
    if "date" in df.columns and "product" in df.columns:
        # pick a Y column
        y = "revenue" if "revenue" in df.columns else ("requests" if "requests" in df.columns else None)
        if y:
            plot_stacked_area(df, "date", "product", y, f"Product Mix over Time ({y})", "product_mix.png")

    # Reliability: error rate vs traffic if both exist
    if "errors" in df.columns:
        x = None
        for c in ["requests", "active_users"]:
            if c in df.columns:
                x = c; break
        if x:
            # aggregate per day
            if "date" in df.columns:
                agg = df.groupby("date")[[x, "errors"]].sum().reset_index()
            else:
                agg = df[[x, "errors"]].copy()
            plot_scatter(agg, x, "errors", f"Errors vs {x}", "errors_vs_traffic.png")

    # Cohort retention (if we have user_id + date)
    if ("user_id" in df.columns) and ("date" in df.columns):
        cohort_heatmap(df)

    print(f"Saved charts to {OUT_DIR}/")

if __name__ == "__main__":
    main()
