import streamlit as st
import pandas as pd

st.set_page_config(page_title="SG Supplier Database", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("master_plant_list_2026.csv")
    df.columns = df.columns.str.strip()
    df["Item"] = df["Item"].astype(str).str.strip()
    df["Size"] = df["Size"].astype(str).str.strip().replace("nan", "")
    df["Supplier"] = df["Supplier"].astype(str).str.strip()
    return df

df = load_data()

st.title("SG Supplier Database")
st.markdown("Search for an item to see all suppliers and their prices.")

query = st.text_input("Search", placeholder="Type to search...")

if query:
    matching_items = sorted(df[df["Item"].str.contains(query, case=False, na=False)]["Item"].unique().tolist())

    if not matching_items:
        st.info("No results found.")
    else:
        refinement = st.selectbox(
            "Suggestions — pick one to narrow results, or leave as 'All'",
            options=["All"] + matching_items,
            index=0,
        )

        if refinement == "All":
            results = df[df["Item"].str.contains(query, case=False, na=False)]
        else:
            results = df[df["Item"] == refinement]

        results = results[["Item", "Supplier", "Size", "Price"]].sort_values(["Item", "Price"]).reset_index(drop=True)

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
