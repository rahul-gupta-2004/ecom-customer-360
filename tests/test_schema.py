import pandas as pd
import pytest
from src.ingest import load_raw_data

def test_load_raw_data_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_raw_data("unsupported_file.txt")