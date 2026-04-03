import streamlit as st
import pandas as pd

st.set_page_config(page_title="SG Supplier Database", layout="centered")

@st.cache_data
def load_data():
    df = pd.read_csv("sample_database.csv")
    df.columns = df.columns.str.strip()
    df["Item"] = df["Item"].astype(str).str.strip()
    df["Size"] = df["Size"].astype(str).str.strip().replace("nan", "")
    df["Supplier"] = df["Supplier"].astype(str).str.strip()
    return df

df = load_data()
all_items = sorted(df["Item"].unique().tolist())

st.title("SG Supplier Database")
st.markdown("Search for an item to see all suppliers and their prices.")

selected_item = st.selectbox(
    "Search item",
    options=all_items,
    index=None,
    placeholder="Start typing to search...",
)

if selected_item:
    results = df[df["Item"] == selected_item][["Supplier", "Size", "Price"]].sort_values("Price").reset_index(drop=True)

    if results.empty:
        st.info("No suppliers found for this item.")
    else:
        best = df[df["Item"] == selected_item].copy()
        best_idx = best["Price"].idxmin()
        best_supplier = best.loc[best_idx, "Supplier"]
        best_price = best.loc[best_idx, "Price"]
        st.success(f"Best price: **{best_supplier}** at **${best_price:,.2f}**")

        results["Price"] = results["Price"].apply(
            lambda p: f"${p:,.2f}" if pd.notna(p) else "N/A"
        )
        results.insert(0, "Select", False)

        edited = st.data_editor(
            results,
            column_config={
                "Select": st.column_config.CheckboxColumn("✓", default=False, width="small"),
            },
            hide_index=True,
            use_container_width=True,
        )

        selected_rows = edited[edited["Select"]]
        if not selected_rows.empty:
            st.markdown("#### Copy selection:")
            for _, row in selected_rows.iterrows():
                st.code(f"{row['Supplier']}\t1\t{selected_item}\t{row['Size']}\t{row['Price']}", language=None)
