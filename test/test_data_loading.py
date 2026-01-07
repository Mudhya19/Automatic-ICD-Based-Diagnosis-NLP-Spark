import pandas as pd
import os

def test_data_loading():
    """Test script to verify data loading from various possible paths"""
    
    possible_paths = [
        'database/data/diagnosis_icd_2025.csv',    # Path relatif dari root proyek
        './database/data/diagnosis_icd_2025.csv', # Path relatif ke current directory
        '../database/data/diagnosis_icd_2025.csv', # Path relatif ke parent directory
        '../../database/data/diagnosis_icd_2025.csv', # Path relatif ke grandparent directory
        '/app/database/data/diagnosis_icd_2025.csv', # Path untuk container deployment
        'data/diagnosis_icd_2025.csv',             # Alternatif path di folder data
        './data/diagnosis_icd_2025.csv',           # Alternatif path relatif
        'diagnosis_icd_2025.csv',                  # File langsung di root
        os.path.join('database', 'data', 'diagnosis_icd_2025.csv'),  # Cross-platform path
        os.path.join('.', 'database', 'data', 'diagnosis_icd_2025.csv'),  # Cross-platform path with current dir
        os.path.join('..', 'database', 'data', 'diagnosis_icd_2025.csv'),  # Cross-platform path with parent dir
        os.path.join('data', 'diagnosis_icd_2025.csv'),  # Cross-platform path in data dir
    ]
    
    print("Testing data file loading from possible paths...")
    print(f"Current working directory: {os.getcwd()}")
    print()
    
    for i, path in enumerate(possible_paths):
        print(f"{i+1}. Trying path: {path}")
        try:
            df = pd.read_csv(path)
            print(f"   SUCCESS: Loaded {len(df)} rows from {path}")
            print(f"   Columns: {list(df.columns)}")
            print()
            # If successful, return the path that worked
            return path
        except FileNotFoundError:
            print(f"   File not found")
            print()
        except Exception as e:
            print(f"   Error: {str(e)}")
            print()
    
    print("❌ Could not load data from any of the possible paths.")
    return None

if __name__ == "__main__":
    test_data_loading()