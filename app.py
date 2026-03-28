import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bid Helper", layout="centered")

@st.cache_data
def load_data():
    df = pd.read_excel("sample_database2.xlsx")
    df.columns = df.columns.str.strip()
    df["Item"] = df["Item"].astype(str).str.strip()
    df["Supplier"] = df["Supplier"].astype(str).str.strip()
    return df

df = load_data()
all_items = sorted(df["Item"].unique().tolist())

st.title("Bid Helper")
st.markdown("Search for an item to see all suppliers and their prices.")

selected_item = st.selectbox(
    "Search item",
    options=all_items,
    index=None,
    placeholder="Start typing to search...",
)

if selected_item:
    results = df[df["Item"] == selected_item][["Supplier", "Price"]].reset_index(drop=True)
    results.index += 1

    st.markdown(f"### Suppliers for: *{selected_item}*")

    if results.empty:
        st.info("No suppliers found for this item.")
    else:
        results["Price"] = results["Price"].apply(
            lambda p: f"${p:,.2f}" if pd.notna(p) else "N/A"
        )
        st.table(results)

        best = df[df["Item"] == selected_item].copy()
        best_idx = best["Price"].idxmin()
        best_supplier = best.loc[best_idx, "Supplier"]
        best_price = best.loc[best_idx, "Price"]
        st.success(f"Best price: **{best_supplier}** at **${best_price:,.2f}**")
