import streamlit as st
import json
import pandas as pd
from classifier import classify_po

st.set_page_config(page_title="PO Category Classifier", layout="wide")

st.title("📦 PO L1–L2–L3 Classifier")

# --- Sidebar for Mode Selection ---
mode = st.sidebar.radio("Select Mode", ["Single Classification", "Batch Processing (CSV/Excel)"])

if mode == "Single Classification":
    st.subheader("Manual Entry")
    po_description = st.text_area("PO Description", height=120, placeholder="e.g., Office desk chairs for HR department")
    supplier = st.text_input("Supplier (optional)")

    if st.button("Classify"):
        if not po_description.strip():
            st.warning("Please enter a PO description.")
        else:
            with st.spinner("Classifying..."):
                result = classify_po(po_description, supplier)
            
            try:
                data = json.loads(result)
                # Display results in pretty columns instead of raw JSON
                col1, col2, col3 = st.columns(3)
                col1.metric("L1 Category", data.get("L1", "N/A"))
                col2.metric("L2 Category", data.get("L2", "N/A"))
                col3.metric("L3 Category", data.get("L3", "N/A"))
                
                with st.expander("View Raw JSON"):
                    st.json(data)
            except Exception:
                st.error("Invalid model response")
                st.text(result)

else:
    st.subheader("Batch Upload")
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.write("Preview of data:", df.head())
        
        column_to_process = st.selectbox("Select the PO Description column", df.columns)
        
        if st.button("Process All"):
            results_list = []
            progress_bar = st.progress(0)
            
            for i, row in df.iterrows():
                # Update progress
                progress_bar.progress((i + 1) / len(df))
                
                # Run classifier
                raw_res = classify_po(str(row[column_to_process]), "")
                try:
                    parsed_res = json.loads(raw_res)
                    results_list.append(parsed_res)
                except:
                    results_list.append({"L1": "Error", "L2": "Error", "L3": "Error"})
            
            # Merge results back to original dataframe
            res_df = pd.concat([df, pd.DataFrame(results_list)], axis=1)
            st.success("Processing Complete!")
            st.dataframe(res_df)
            
            # Download Button
            csv = res_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Classified Data", csv, "classified_pos.csv", "text/csv")
