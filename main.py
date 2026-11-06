import streamlit as st
import pandas as pd
import os
import json
import tempfile
import altair as alt
from sqlalchemy import text
from src.ingest import load_raw_data
from src.transform import apply_transformations
from src.load import load_data_to_postgres, get_database_engine

st.set_page_config(page_title="Customer 360 Data Pipeline & Analytics", layout="wide")

st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox(
    "Choose a Section",
    ["Upload & Process Files", "Data Quality Checks", "View Database", "Analytics Dashboard"]
)

# ---------------------------------------------------------
# SECTION 1: UPLOAD & PROCESS FILES
# ---------------------------------------------------------
if app_mode == "Upload & Process Files":
    st.title("Multi-File Ingestion & Processing Pipeline")
    st.write("Upload all raw data files (CSV, JSON, XML) simultaneously to merge them into the unified Customer 360 dataset.")

    uploaded_files = st.file_uploader(
        "Choose CSV, JSON, or XML files", 
        type=["csv", "json", "xml"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info(f"Loaded {len(uploaded_files)} file(s) ready for batch execution.")
        
        if st.button("Run Full Pipeline for All Files"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            raw_dfs = []
            total_files = len(uploaded_files)
            pipeline_logs = []

            for i, uploaded_file in enumerate(uploaded_files):
                file_name = uploaded_file.name
                status_text.text(f"Ingesting [{i+1}/{total_files}]: {file_name}...")
                pipeline_logs.append({"Step": "Ingestion", "File": file_name, "Status": "Success"})
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                try:
                    df = load_raw_data(tmp_path)
                    raw_dfs.append(df)
                except Exception as e:
                    st.error(f"Error processing {file_name}: {e}")
                    pipeline_logs.append({"Step": "Ingestion Error", "File": file_name, "Status": str(e)})
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

                progress_bar.progress((i + 1) / total_files)

            if raw_dfs:
                status_text.text("Merging sources and applying transformations into Customer 360 dataset...")
                pipeline_logs.append({"Step": "Transformation", "File": "All Files", "Status": "Merged & Cleaned"})
                try:
                    master_customer_360_df = apply_transformations(raw_dfs)
                    
                    status_text.text("Loading unified Customer 360 dataset into PostgreSQL...")
                    load_data_to_postgres(master_customer_360_df, table_name="customer_360_pipeline_data")
                    pipeline_logs.append({"Step": "Database Load", "File": "PostgreSQL", "Status": "Loaded Successfully"})
                    
                    # Save execution logs
                    os.makedirs("data/processed", exist_ok=True)
                    with open("data/processed/pipeline_logs.json", "w") as log_f:
                        json.dump(pipeline_logs, log_f, indent=4)
                    
                    status_text.text("Pipeline execution completed successfully!")
                    st.success("All files successfully ingested, merged, and loaded into PostgreSQL as Customer 360!")

                    st.subheader("Unified Customer 360 Dataset Preview")
                    with st.expander(f"Master Dataset ({len(master_customer_360_df)} records)", expanded=True):
                        st.dataframe(master_customer_360_df, use_container_width=True)
                except Exception as e:
                    st.error(f"Error during merge and load: {e}")

# ---------------------------------------------------------
# SECTION 2: DATA QUALITY CHECKS
# ---------------------------------------------------------
elif app_mode == "Data Quality Checks":
    st.title("Data Quality & Schema Validation Report")
    st.write("Inspect data hygiene metrics, missing value percentages, and audit check results stored in `data/processed/data_quality_report.json`.")

    report_path = "data/processed/data_quality_report.json"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            dq_report = json.load(f)
            
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Duplicate Customers", dq_report.get("duplicate_customers_count", 0))
        col2.metric("Invalid Emails", dq_report.get("invalid_emails_count", 0))
        col3.metric("Negative Revenue", dq_report.get("negative_revenue_count", 0))
        col4.metric("Invalid Customer IDs", dq_report.get("invalid_customer_ids_count", 0))
        
        st.subheader("Raw Data Quality JSON Report")
        st.json(dq_report)
    else:
        st.warning("No data quality report found. Please run the pipeline via the 'Upload & Process Files' tab first.")

    try:
        engine = get_database_engine()
        query = "SELECT * FROM customer_360_pipeline_data;"
        df_db = pd.read_sql(query, con=engine)

        if not df_db.empty:
            st.subheader("Database Missing Values Breakdown")
            missing_df = df_db.isnull().sum().reset_index()
            missing_df.columns = ['Column Name', 'Missing Count']
            st.dataframe(missing_df, use_container_width=True)
    except Exception:
        pass

# ---------------------------------------------------------
# SECTION 3: VIEW DATABASE
# ---------------------------------------------------------
elif app_mode == "View Database":
    st.title("PostgreSQL Database Viewer")
    try:
        engine = get_database_engine()
        df_table = pd.read_sql("SELECT * FROM customer_360_pipeline_data", con=engine)
        st.write(f"Displaying table: **customer_360_pipeline_data** ({len(df_table)} rows)")
        st.dataframe(df_table, use_container_width=True)
    except Exception as e:
        st.error(f"Could not connect to database or query tables: {e}")

# ---------------------------------------------------------
# SECTION 4: DISPLAY DASHBOARD (BUSINESS INSIGHTS & REPORTS)
# ---------------------------------------------------------
elif app_mode == "Analytics Dashboard":
    st.title("Customer 360 Business Intelligence & Analytics Dashboard")
    st.write("Comprehensive executive reporting covering revenue analytics, support operations, regional trends, and customer segmentation.")

    try:
        engine = get_database_engine()
        df_dash = pd.read_sql("SELECT * FROM customer_360_pipeline_data;", con=engine)

        if not df_dash.empty:
            # Dynamic Customer Segmentation Logic
            def assign_segment(row):
                ltv = row.get('lifetime_value', 0)
                orders = row.get('total_orders', 0)
                if ltv > 150000 or orders > 15:
                    return "VIP"
                elif ltv > 75000 or orders > 8:
                    return "Regular"
                else:
                    return "At-Risk"

            df_dash['customer_segment'] = df_dash.apply(assign_segment, axis=1)

            # ---------------------------------------------------------
            # 4 Key Performance Indicators (KPIs)
            # ---------------------------------------------------------
            total_revenue = df_dash['lifetime_value'].sum()
            total_customers = len(df_dash)
            avg_order_val = (total_revenue / df_dash['total_orders'].sum()) if df_dash['total_orders'].sum() > 0 else 0
            total_tickets = df_dash['support_tickets'].sum()

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total Revenue (LTV)", f"₹{total_revenue:,.2f}")
            kpi2.metric("Total Customers", f"{total_customers:,}")
            kpi3.metric("Avg Order Value (AOV)", f"₹{avg_order_val:,.2f}")
            kpi4.metric("Total Support Tickets", f"{int(total_tickets):,}")

            st.markdown("---")

            # ---------------------------------------------------------
            # 2x2 Grid of 4 Colorful Simple Charts (using Altair for rich color palettes)
            # ---------------------------------------------------------
            st.header("Visual Analytics Overview")

            r1_c1, r1_c2 = st.columns(2)
            with r1_c1:
                st.markdown("**1. Revenue by City**")
                if 'city' in df_dash.columns and 'lifetime_value' in df_dash.columns:
                    city_revenue = df_dash.groupby('city')['lifetime_value'].sum().reset_index()
                    chart1 = alt.Chart(city_revenue).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                        x=alt.X('city:N', sort='-y', title='City'),
                        y=alt.Y('lifetime_value:Q', title='Total Revenue (₹)'),
                        color=alt.Color('city:N', legend=None, scale=alt.Scale(scheme='category20'))
                    ).properties(height=300)
                    st.altair_chart(chart1, use_container_width=True)

            with r1_c2:
                st.markdown("**2. Customer Segment Breakdown**")
                segment_counts = df_dash['customer_segment'].value_counts().reset_index()
                segment_counts.columns = ['Segment', 'Count']
                chart2 = alt.Chart(segment_counts).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                    x=alt.X('Segment:N', title='Customer Segment'),
                    y=alt.Y('Count:Q', title='Customer Count'),
                    color=alt.Color('Segment:N', legend=None, scale=alt.Scale(scheme='set2'))
                ).properties(height=300)
                st.altair_chart(chart2, use_container_width=True)

            r2_c1, r2_c2 = st.columns(2)
            with r2_c1:
                st.markdown("**3. Average Support Tickets by Segment (Simple)**")
                if 'customer_segment' in df_dash.columns and 'support_tickets' in df_dash.columns:
                    seg_tickets = df_dash.groupby('customer_segment')['support_tickets'].mean().reset_index()
                    seg_tickets.columns = ['Segment', 'Avg_Tickets']
                    chart3 = alt.Chart(seg_tickets).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                        x=alt.X('Segment:N', title='Customer Segment'),
                        y=alt.Y('Avg_Tickets:Q', title='Average Support Tickets'),
                        color=alt.Color('Segment:N', legend=None, scale=alt.Scale(scheme='pastel1'))
                    ).properties(height=300)
                    st.altair_chart(chart3, use_container_width=True)

            with r2_c2:
                st.markdown("**4. Average Order Value by City**")
                if 'city' in df_dash.columns and 'lifetime_value' in df_dash.columns and 'total_orders' in df_dash.columns:
                    city_grouped = df_dash.groupby('city')[['lifetime_value', 'total_orders']].sum().reset_index()
                    city_grouped['avg_order_value'] = city_grouped['lifetime_value'] / city_grouped['total_orders'].replace(0, 1)
                    chart4 = alt.Chart(city_grouped).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                        x=alt.X('city:N', sort='-y', title='City'),
                        y=alt.Y('avg_order_value:Q', title='Avg Order Value (₹)'),
                        color=alt.Color('city:N', legend=None, scale=alt.Scale(scheme='tableau10'))
                    ).properties(height=300)
                    st.altair_chart(chart4, use_container_width=True)

            st.markdown("---")

            # ---------------------------------------------------------
            # Separate Section for Support Insights
            # ---------------------------------------------------------
            st.header("Support Insights & Operations")
            st.write("Operational analysis of customer support tickets and issue resolution volume.")
            
            sup_col1, sup_col2, sup_col3 = st.columns(3)
            avg_tickets = df_dash['support_tickets'].mean()
            max_tickets = df_dash['support_tickets'].max()
            sup_col1.metric("Average Tickets per Customer", f"{avg_tickets:.2f}")
            sup_col2.metric("Max Tickets by a Customer", f"{int(max_tickets)}")
            sup_col3.metric("Support Load Status", "Normal" if avg_tickets < 5 else "High Load")

            st.markdown("---")

            # ---------------------------------------------------------
            # Detailed Reports & Metric Tables (All expanded=True)
            # ---------------------------------------------------------
            st.header("Detailed Reports & Metric Tables")

            with st.expander("Customer Segmentation Summary Table", expanded=True):
                st.write("Detailed breakdown of customer distribution across VIP, Regular, and At-Risk tiers.")
                seg_summary = df_dash.groupby('customer_segment').agg(
                    Customer_Count=('customer_id', 'count'),
                    Total_Revenue=('lifetime_value', 'sum'),
                    Avg_Orders=('total_orders', 'mean'),
                    Avg_Support_Tickets=('support_tickets', 'mean')
                ).reset_index()
                seg_summary['Total_Revenue'] = seg_summary['Total_Revenue'].round(2)
                seg_summary['Avg_Orders'] = seg_summary['Avg_Orders'].round(2)
                seg_summary['Avg_Support_Tickets'] = seg_summary['Avg_Support_Tickets'].round(2)
                st.dataframe(seg_summary, use_container_width=True)

            with st.expander("Data Quality & Hygiene Metrics Summary", expanded=True):
                st.write("Audit results loaded from quality check reports.")
                report_path = "data/processed/data_quality_report.json"
                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        dq = json.load(f)
                    dq_data = {
                        "Metric": ["Duplicate Customers", "Invalid Emails", "Negative Revenue Records", "Invalid Customer IDs"],
                        "Count": [
                            dq.get("duplicate_customers_count", 0),
                            dq.get("invalid_emails_count", 0),
                            dq.get("negative_revenue_count", 0),
                            dq.get("invalid_customer_ids_count", 0)
                        ]
                    }
                    st.dataframe(pd.DataFrame(dq_data), use_container_width=True)
                else:
                    st.info("No data quality report found.")

            with st.expander("Database Missing Values Breakdown", expanded=True):
                st.write("Null count per column in the master database table.")
                missing_df = df_dash.isnull().sum().reset_index()
                missing_df.columns = ['Column Name', 'Missing Count']
                st.dataframe(missing_df, use_container_width=True)

            with st.expander("Pipeline Execution & Logging Table", expanded=True):
                st.write("Recent execution logs stored during batch file ingestion and processing.")
                log_path = "data/processed/pipeline_logs.json"
                if os.path.exists(log_path):
                    with open(log_path, "r") as log_f:
                        logs = json.load(log_f)
                    st.dataframe(pd.DataFrame(logs), use_container_width=True)
                else:
                    st.info("No pipeline execution logs found. Run the pipeline upload first.")

        else:
            st.warning("No data available for visualization. Please process your source files in the 'Upload & Process Files' tab first.")
    except Exception as e:
        st.info(f"Database table is empty or uninitialized. Run the pipeline to populate analytics. Details: {e}")