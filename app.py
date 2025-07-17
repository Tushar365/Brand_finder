import streamlit as st
import pandas as pd
import io
import re
import os

def find_brand_and_mrp(product_name, brand_data):
    """
    Find the brand name and MRP for a given product by matching it against a reference dataset
    """
    if pd.isna(product_name):
        return "Unknown", "Unknown"
    product_name = str(product_name).strip().upper()
    # Exact match
    matching_rows = brand_data[brand_data['Product_Name'].str.upper() == product_name]
    if not matching_rows.empty:
        return (
            matching_rows.iloc[0].get('Brand_Name', "Unknown"),
            matching_rows.iloc[0].get('MRP', "Unknown")
        )
    # Partial match
    for _, row in brand_data.iterrows():
        brand_name = str(row.get('Brand_Name', '')).strip()
        ref_product = str(row.get('Product_Name', '')).strip().upper()
        if brand_name and brand_name.upper() in product_name:
            return (brand_name, row.get('MRP', "Unknown"))
        if ref_product and (ref_product in product_name or product_name in ref_product):
            return (
                row.get('Brand_Name', "Unknown"),
                row.get('MRP', "Unknown")
            )
    return "Unknown", "Unknown"

def process_dataframe(df_to_fill, df_products):
    product_col = 'Product_Name' if 'Product_Name' in df_to_fill.columns else df_to_fill.columns[0]
    result_df = df_to_fill.copy()
    result = result_df[product_col].apply(lambda x: find_brand_and_mrp(x, df_products))
    result_df['Brand_Name'] = result.apply(lambda x: x[0])
    result_df['MRP'] = result.apply(lambda x: x[1])
    return result_df

# Set page title and description
st.set_page_config(page_title="Brand Finder App", layout="wide")
st.title("Brand Finder App")
st.write("""
Upload a CSV file with product names that need brand identification.
The app will use the reference dataset from 'public/products.csv' to identify brands.
""")

# Load reference dataset from fixed location
reference_path = 'public/products.csv'
df_reference = None

try:
    if os.path.exists(reference_path):
        df_reference = pd.read_csv(reference_path)
        st.success(f"Successfully loaded reference data from {reference_path}")
        st.subheader("Reference Dataset Preview")
        st.dataframe(df_reference.head())
    else:
        st.error(f"Reference file not found at {reference_path}")
except Exception as e:
    st.error(f"Error loading reference file: {e}")

# File upload section for products to identify
st.header("Upload Your Products File")
st.write("Upload a CSV file containing product names that need brand identification.")
product_file = st.file_uploader("Choose products CSV file", type="csv", key="products")

# Add options for column mapping
if df_reference is not None and product_file is not None:
    # Load data
    try:
        df_products_to_fill = pd.read_csv(product_file)
        
        # Display preview of uploaded files
        st.subheader("Products Dataset Preview")
        st.dataframe(df_products_to_fill.head())
        
        # Column selection for reference data
        st.header("Select Columns")
        
        reference_cols = df_reference.columns.tolist()
        product_name_col = st.selectbox("Select Product Name column in reference data", reference_cols, 
                                       index=reference_cols.index('Product_Name') if 'Product_Name' in reference_cols else 0)
        brand_name_col = st.selectbox("Select Brand Name column in reference data", reference_cols,
                                     index=reference_cols.index('Brand_Name') if 'Brand_Name' in reference_cols else 0)
        
        # Column selection for reference data
        st.header("Select Columns")
        
        reference_cols = df_reference.columns.tolist()
        product_name_col = st.selectbox(
            "Select Product Name column in reference data", 
            reference_cols, 
            index=reference_cols.index('Product_Name') if 'Product_Name' in reference_cols else 0
        )
        brand_name_col = st.selectbox(
            "Select Brand Name column in reference data", 
            reference_cols,
            index=reference_cols.index('Brand_Name') if 'Brand_Name' in reference_cols else 0
        )
        mrp_col = st.selectbox(
            "Select MRP column in reference data",
            reference_cols,
            index=reference_cols.index('MRP') if 'MRP' in reference_cols else 0
        )
        
        # Column selection for product data
        product_cols = df_products_to_fill.columns.tolist()
        product_col_to_match = st.selectbox("Select Product Name column in your data", product_cols)
        
        # Process button
        if st.button("Find Brands and MRP"):
            # Create a structured reference dataframe with standard column names
            df_reference_std = df_reference.rename(columns={
                product_name_col: 'Product_Name',
                brand_name_col: 'Brand_Name',
                mrp_col: 'MRP'
            })
            # Create a structured product dataframe with standard column names
            df_products_std = df_products_to_fill.rename(columns={
                product_col_to_match: 'Product_Name'
            })
            # Process data to find brands and MRP
            result_df = process_dataframe(df_products_std, df_reference_std)
            # Rename back to original column names and keep the Brand_Name and MRP column
            result_df = result_df.rename(columns={'Product_Name': product_col_to_match})
            # Display results
            st.header("Results")
            st.dataframe(result_df)
            # Generate download link
            csv = result_df.to_csv(index=False)
            st.download_button(
                label="Download Results CSV",
                data=csv,
                file_name="products_with_brands_and_mrp.csv",
                mime="text/csv"
            )
            # Show statistics
            st.subheader("Statistics")
            total_products = len(result_df)
            identified_brands = len(result_df[result_df['Brand_Name'] != 'Unknown'])
            st.write(f"Total products: {total_products}")
            st.write(f"Products with identified brands: {identified_brands} ({identified_brands/total_products:.1%})")
            st.write(f"Products with unknown brands: {total_products - identified_brands} ({(total_products - identified_brands)/total_products:.1%})")ified_brands/total_products:.1%})")
            
    except Exception as e:
        st.error(f"Error processing files: {e}")
        st.write("Please make sure your CSV files are properly formatted.")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.write("""
### How to use this app:
1. The app automatically uses the product reference data from 'public/products.csv'
2. Upload your product CSV file that needs brand identification
3. Select the appropriate columns from each file
4. Click 'Find Brands' to process the data
5. Download the resulting CSV with brand information
""")

# About
st.sidebar.header("About")
st.sidebar.write("""
This app helps identify brand names for products by matching them against the reference dataset.
It uses both exact and partial matching techniques to identify the most likely brand for each product.

The app expects a file named 'products.csv' in the 'public' folder containing the reference product and brand data.
""")
