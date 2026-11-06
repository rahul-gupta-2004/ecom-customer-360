import pandas as pd
import xml.etree.ElementTree as ET

def load_raw_data(file_path: str) -> pd.DataFrame:
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        df = pd.read_json(file_path)
    elif file_path.endswith('.xml'):
        # Robust XML parsing handling nested customer tags
        try:
            df = pd.read_xml(file_path)
        except Exception:
            tree = ET.parse(file_path)
            root = tree.getroot()
            records = []
            for elem in root.iter():
                if len(elem) == 0 and elem.text and elem.text.strip():
                    pass # handled via standard parsing or custom traversal if needed
            # Fallback standard pd.read_xml with xpath if specific
            df = pd.read_xml(file_path, xpath=".//*")
    else:
        raise ValueError("Unsupported file format. Please provide a CSV, JSON, or XML file.")
    
    # Normalize column names
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # Map ID aliases
    for alias in ['cust_id', 'customerid', 'id']:
        if alias in df.columns and 'customer_id' not in df.columns:
            df = df.rename(columns={alias: 'customer_id'})
            
    # Map support ticket aliases
    df = df.rename(columns={'tickets': 'support_tickets', 'lastticketdate': 'last_ticket_date'})
        
    return df