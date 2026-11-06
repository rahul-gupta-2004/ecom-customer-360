import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_database_engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        user = os.getenv("POSTGRES_USER", "postgres_user")
        password = os.getenv("POSTGRES_PASSWORD", "secure_password_123")
        db = os.getenv("POSTGRES_DB", "pipeline_db")
        db_url = f"postgresql://{user}:{password}@localhost:5432/{db}"
    
    return create_engine(db_url)

def load_data_to_postgres(df, table_name="customer_360_pipeline_data"):
    engine = get_database_engine()
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)