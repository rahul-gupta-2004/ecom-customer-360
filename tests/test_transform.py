import pandas as pd
from src.transform import apply_transformations, merge_customer_data

def test_merge_customer_data():
    df_orders = pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "total_orders": [5.0, 2.0],
        "lifetime_value": [250.0, 100.0]
    })
    df_crm = pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "name": ["Alice", "Bob"],
        "city": ["Mumbai", "Bengaluru"]
    })
    
    merged = merge_customer_data([df_orders, df_crm])
    assert len(merged) == 2
    assert "name" in merged.columns
    assert "total_orders" in merged.columns

def test_apply_transformations_full_customer_360():
    df_orders = pd.DataFrame({
        "cust_id": ["C001"],
        "total_orders": [3.0],
        "lifetime_value": [150.0]
    })
    df_crm = pd.DataFrame({
        "customer_id": ["C001"],
        "name": ["Rahul"],
        "email": ["rahul@example.com"],
        "city": ["Bengaluru"]
    })
    df_support = pd.DataFrame({
        "customerId": ["C001"],
        "tickets": [2.0]
    })
    
    transformed = apply_transformations([df_orders, df_crm, df_support])
    
    # Check shape and final Customer 360 columns
    assert len(transformed) == 1
    assert "customer_id" in transformed.columns
    assert "name" in transformed.columns
    assert "total_orders" in transformed.columns
    assert "support_tickets" in transformed.columns
    assert transformed.iloc[0]["total_orders"] == 3.0
    assert transformed.iloc[0]["support_tickets"] == 2.0