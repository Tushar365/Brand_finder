import streamlit as st
import pandas as pd
import io
import re
import os

def find_brand_name(product_name, brand_data):
    """
    Find the brand name for a given product by matching it against a reference dataset
    """
    if pd.isna(product_name):
        return "Unknown"
    
    product_name = str(product_name).strip().upper()
    
    # Exact match
    matching_rows = brand_data[brand_data['Product_Name'].str.upper() == product_name]
    if not matching_rows.empty:
        return matching_rows.iloc[0].get('Brand_Name', "Unknown")
    
    # Partial match - check if brand name appears in product name
    for _, row in brand_data.iterrows():
        brand_name = str(row.get('Brand_Name', '')).strip()
        if brand_name and brand_name.upper() in product_name:
            return brand_name
    
    # Partial match - check if product names are similar
    for _, row in brand_data.iterrows():
        ref_product = str(row.get('Product_Name', '')).strip().upper()
        if ref_product and (ref_product in product_name or product_name in ref_product):
            return row.get('Brand_Name', "Unknown")
    
    return "Unknown"

def find_mrp(product_name, brand_name, brand_data):
    """
    Find the MRP for a given product and brand by matching against reference dataset
    """
    if pd.isna(product_name):
        return "Unknown"
    
    product_name = str(product_name).strip().upper()
    brand_name = str(brand_name).strip().upper()
    
    # First try exact product name match
    matching_rows = brand_data[brand_data['Product_Name'].str.upper() == product_name]
    if not matching_rows.empty:
        return matching_rows.iloc[0].get('MRP', "Unknown")
    
    # Then try brand name match
    if brand_name != "UNKNOWN":
        brand_matching_rows = brand_data[brand_data['Brand_Name'].str.upper() == brand_name]
        if not brand_matching_rows.empty:
            return brand_matching_rows.iloc[0].get('MRP', "Unknown")
    
    # Partial match for product name
    for _, row in brand_data.iterrows():
        ref_product = str(row.get('Product_Name', '')).strip().upper()
        if ref_product and (ref_product in product_name or product_name in ref_product):
            return row.get('MRP', "Unknown")
    
    return "Unknown"

def process_dataframe_sequential(df_to_fill, df_products):
    """
    Process dataframe by finding brands first, then MRP
    """
    product_col = 'Product_Name' if 'Product_Name' in df_to_fill.columns else df_to_fill.columns[0]
    result_df = df_to_fill.copy()
    
    # Step 1: Find brand names
    st.write("Step 1: Finding brand names...")
    progress_bar = st.progress(0)
    
    brands = []
    for i, product_name in enumerate(result_df[product_col]):
        brand = find_brand_name(product_name, df_products)
        brands.append(brand)
        progress_bar.progress((i + 1) / len(result_df))
    
    result_df['Brand_Name'] = brands
    
    # Step 2: Find MRP
    st.write("Step 2: Finding MRP values...")
    progress_bar = st.progress(0)
    
    mrps = []
    for i, (product_name, brand_name) in enumerate(zip(result_df[product_col], result_df['Brand_Name'])):
        mrp = find_mrp(product_name, brand_name, df_products)
        mrps.append(mrp)
        progress_bar.progress((i + 1) / len(result_df))
    
    result_df['MRP'] = mrps
    
    return result_df

# Set page title and description
st.set_page_config(page_title="Brand Finder App", layout="wide")
st.title("🔍 Brand Finder App")
st.write("""
Upload a CSV file with product names that need brand identification and MRP lookup.
The app will use the reference dataset from 'public/products.csv' to identify brands and MRP in two sequential steps.
""")

# Load reference dataset from fixed location
reference_path = 'public/products.csv'
df_reference = None

try:
    if os.path.exists(reference_path):
        df_reference = pd.read_csv(reference_path)
        st.success(f"✅ Successfully loaded reference data from {reference_path}")
        st.subheader("Reference Dataset Preview")
        st.dataframe(df_reference.head())
        
        # Show dataset statistics
        st.write(f"**Dataset Statistics:**")
        st.write(f"- Total products: {len(df_reference)}")
        st.write(f"- Unique brands: {df_reference['Brand_Name'].nunique() if 'Brand_Name' in df_reference.columns else 'N/A'}")
        
    else:
        st.error(f"❌ Reference file not found at {reference_path}")
        st.write("Please ensure you have a 'products.csv' file in the 'public' folder.")
except Exception as e:
    st.error(f"❌ Error loading reference file: {e}")

# File upload section for products to identify
st.header("📁 Upload Your Products File")
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
        st.write(f"**Uploaded file statistics:** {len(df_products_to_fill)} products")
        
        # Column selection for reference data
        st.header("🔧 Configure Column Mapping")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Reference Data Columns")
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
        
        with col2:
            st.subheader("Your Data Columns")
            product_cols = df_products_to_fill.columns.tolist()
            product_col_to_match = st.selectbox("Select Product Name column in your data", product_cols)
        
        # Process button
        if st.button("🚀 Find Brands and MRP", type="primary"):
            with st.spinner("Processing data..."):
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
                
                # Process data to find brands and MRP sequentially
                result_df = process_dataframe_sequential(df_products_std, df_reference_std)
                
                # Rename back to original column names and keep the Brand_Name and MRP column
                result_df = result_df.rename(columns={'Product_Name': product_col_to_match})
                
                # Display results
                st.header("📊 Results")
                st.dataframe(result_df)
                
                # Generate download link
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results CSV",
                    data=csv,
                    file_name="products_with_brands_and_mrp.csv",
                    mime="text/csv"
                )
                
                # Show detailed statistics
                st.subheader("📈 Processing Statistics")
                total_products = len(result_df)
                identified_brands = len(result_df[result_df['Brand_Name'] != 'Unknown'])
                identified_mrp = len(result_df[result_df['MRP'] != 'Unknown'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Products", total_products)
                
                with col2:
                    st.metric(
                        "Brands Identified", 
                        f"{identified_brands} ({identified_brands/total_products:.1%})"
                    )
                
                with col3:
                    st.metric(
                        "MRP Found", 
                        f"{identified_mrp} ({identified_mrp/total_products:.1%})"
                    )
                
                # Show unknown products for debugging
                unknown_brands = result_df[result_df['Brand_Name'] == 'Unknown']
                if not unknown_brands.empty:
                    st.subheader("🔍 Products with Unknown Brands")
                    st.dataframe(unknown_brands[[product_col_to_match]])
                    st.write(f"Consider adding these products to your reference dataset to improve matching.")
                
    except Exception as e:
        st.error(f"❌ Error processing files: {e}")
        st.write("Please make sure your CSV files are properly formatted.")
        st.write("**Common issues:**")
        st.write("- Missing or empty columns")
        st.write("- Incorrect file encoding")
        st.write("- Malformed CSV structure")

# Instructions
st.sidebar.header("📋 Instructions")
st.sidebar.write("""
### How to use this app:
1. **Setup**: Place your reference data in `public/products.csv`
2. **Upload**: Upload your product CSV file
3. **Configure**: Select the correct columns for mapping
4. **Process**: Click 'Find Brands and MRP' to start processing
5. **Download**: Get the results with brand and MRP information

### Processing Steps:
- **Step 1**: Find brand names using exact and partial matching
- **Step 2**: Find MRP values based on product and brand matches
""")

# About
st.sidebar.header("ℹ️ About")
st.sidebar.write("""
This app helps identify brand names and MRP for products by matching them against a reference dataset.

**Matching Strategy:**
- Exact product name match (highest priority)
- Brand name contains in product name
- Partial product name matching
- Brand-based MRP lookup

**File Requirements:**
- Reference file: `public/products.csv`
- Must contain: Product_Name, Brand_Name, MRP columns
""")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Made with ❤️ using Streamlit by Tushar")
