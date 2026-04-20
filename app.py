import streamlit as st
import pandas as pd
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="SG Supplier Database", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("master_plant_list_2026.csv")
    df.columns = df.columns.str.strip()
    df["Item"] = df["Item"].astype(str).str.strip()
    df["Size"] = df["Size"].astype(str).str.strip().replace("nan", "")
    df["Supplier"] = df["Supplier"].astype(str).str.strip()
    df["Label"] = df.astype(str).agg(", ".join, axis=1)
    return df.sort_values("Item")

df = load_data()
all_items = sorted(df["Item"].unique().tolist())
all_labels = df["Label"].tolist()

def search_items(searchterm: str) -> list:
    if not searchterm:
        return []
    matches = [item for item in all_items if searchterm.lower() in item.lower()]
    if not matches:
        return []
    return [f'Keyword search "{searchterm}"'] + matches

def search_labels(searchterm: str) -> list:
    if not searchterm:
        return []
    matches = [label for label in all_labels if searchterm.lower() in label.lower()]
    if not matches:
        return []
    return [f'Keyword search "{searchterm}"'] + matches

st.title("SG Supplier Database")
st.markdown("Search for an item to see all suppliers and their prices.")

selected = st_searchbox(
    search_labels,
    placeholder="Start typing to search...",
    key="plant_search",
)

if selected:
    if isinstance(selected, str) and selected.startswith("Keyword search "):
        query = selected.split('"')[1]
        results = df[df["Item"].str.contains(query, case=False, na=False)][["Item", "Supplier", "Size", "Price"]].sort_values(["Item", "Price"]).reset_index(drop=True)
    else:
        row_id = all_labels.index(selected)
        selected_item = df["Item"].iloc[row_id]
        results = df[df["Item"] == selected_item][["Item", "Supplier", "Size", "Price"]].sort_values("Price").reset_index(drop=True)

    if results.empty:
        st.info("No results found.")
    else:
        best_idx = results["Price"].idxmin()
        best_item = results.loc[best_idx, "Item"]
        best_supplier = results.loc[best_idx, "Supplier"]
        best_price = results.loc[best_idx, "Price"]
        st.success(f"Best price: **{best_item}** from **{best_supplier}** at **${best_price:,.2f}**")

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
                st.code(f"{row['Supplier']}\t1\t{row['Item']}\t{row['Size']}\t{row['Price']}", language=None)
