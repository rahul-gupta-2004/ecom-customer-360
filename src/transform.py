import pandas as pd
import json
import os
import re

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(col).strip().lower() for col in df.columns]
    for alias in ['cust_id', 'customerid', 'id']:
        if alias in df.columns and 'customer_id' not in df.columns:
            df = df.rename(columns={alias: 'customer_id'})
    df = df.rename(columns={'tickets': 'support_tickets', 'lastticketdate': 'last_ticket_date'})
    return df

def merge_customer_data(dfs: list) -> pd.DataFrame:
    if not dfs:
        return pd.DataFrame()
    
    # Filter out empty dataframes or dataframes missing customer_id
    valid_dfs = []
    for df in dfs:
        norm_df = normalize_columns(df)
        if 'customer_id' in norm_df.columns:
            valid_dfs.append(norm_df)
            
    if not valid_dfs:
        return pd.DataFrame()
    
    consolidated_df = valid_dfs[0]
    for next_df in valid_dfs[1:]:
        consolidated_df = pd.merge(
            consolidated_df, 
            next_df, 
            on='customer_id', 
            how='outer',
            suffixes=('', '_dup')
        )
        dup_cols = [col for col in consolidated_df.columns if col.endswith('_dup')]
        consolidated_df = consolidated_df.drop(columns=dup_cols)
        
    return consolidated_df

def run_data_quality_checks(df: pd.DataFrame) -> dict:
    """
    Performs data quality checks for:
    - Duplicate customers
    - Invalid emails
    - Missing mandatory fields
    - Negative revenue / lifetime values
    - Invalid customer IDs
    """
    report = {}
    
    # 1. Duplicate customers based on customer_id
    duplicates = df[df.duplicated(subset=['customer_id'], keep=False)] if 'customer_id' in df.columns else pd.DataFrame()
    report['duplicate_customers_count'] = int(duplicates.shape[0])
    report['duplicate_customer_ids'] = duplicates['customer_id'].tolist() if not duplicates.empty else []
    
    # 2. Invalid emails (basic regex check)
    if 'email' in df.columns:
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        invalid_emails = df[~df['email'].astype(str).str.match(email_regex, na=False)]
        report['invalid_emails_count'] = int(invalid_emails.shape[0])
        report['invalid_emails'] = invalid_emails['email'].tolist()
    else:
        report['invalid_emails_count'] = 0
        report['invalid_emails'] = []
        
    # 3. Missing mandatory fields (e.g., customer_id or name missing)
    mandatory_fields = ['customer_id']
    missing_mandatory = df[df[mandatory_fields].isnull().any(axis=1)] if 'customer_id' in df.columns else df
    report['missing_mandatory_fields_count'] = int(missing_mandatory.shape[0])
    
    # 4. Negative revenue values (lifetime_value < 0)
    if 'lifetime_value' in df.columns:
        neg_revenue = df[pd.to_numeric(df['lifetime_value'], errors='coerce') < 0]
        report['negative_revenue_count'] = int(neg_revenue.shape[0])
        report['negative_revenue_customers'] = neg_revenue['customer_id'].tolist() if 'customer_id' in neg_revenue.columns else []
    else:
        report['negative_revenue_count'] = 0
        
    # 5. Invalid customer IDs (e.g., null, empty string, or incorrect format like missing 'C')
    if 'customer_id' in df.columns:
        invalid_ids = df[df['customer_id'].isnull() | (df['customer_id'].astype(str).str.strip() == "")]
        report['invalid_customer_ids_count'] = int(invalid_ids.shape[0])
    else:
        report['invalid_customer_ids_count'] = int(df.shape[0])
        
    # Ensure processed directory exists and save report
    os.makedirs("data/processed", exist_ok=True)
    report_path = "data/processed/data_quality_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
        
    report['report_file_path'] = report_path
    return report

def apply_transformations(dfs: list) -> pd.DataFrame:
    master_df = merge_customer_data(dfs)
    
    target_columns = [
        'customer_id', 'name', 'email', 'city', 'registration_date', 
        'total_orders', 'lifetime_value', 'last_order_date', 
        'support_tickets', 'last_ticket_date'
    ]
    
    for col in target_columns:
        if col not in master_df.columns:
            if 'date' in col:
                master_df[col] = None
            elif col in ['total_orders', 'lifetime_value', 'support_tickets']:
                master_df[col] = 0.0
            else:
                master_df[col] = "Unknown"
                
    # Clean numeric columns and fix negative values
    numeric_cols = ['total_orders', 'lifetime_value', 'support_tickets']
    for col in numeric_cols:
        master_df[col] = pd.to_numeric(master_df[col], errors='coerce').fillna(0.0)
        if col == 'lifetime_value':
            master_df[col] = master_df[col].abs() # Correct negative anomalies
            
    # Drop rows without valid customer id
    master_df = master_df.dropna(subset=['customer_id'])
    master_df = master_df[target_columns]
    
    # Run and save data quality report
    run_data_quality_checks(master_df)
    
    return master_df