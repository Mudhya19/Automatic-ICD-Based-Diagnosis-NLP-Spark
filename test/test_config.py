#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_config.py
Description: Basic configuration testing for the ICD Diagnosis Extraction Project
"""

import json
import os
import sys

def test_config_file():
    """Test that the config file exists and contains expected keys"""
    config_path = "./config/config.json"
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"❌ Config file not found at {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check for required keys
        required_keys = ["project_name", "version", "spark_config", "nlp_config", "data_config"]
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"❌ Missing required keys in config: {missing_keys}")
            return False
        
        # Check specific configuration values
        if config["project_name"] != "Automatic-ICD-Based-Diagnosis-NLP-Spark":
            print(f"❌ Unexpected project name: {config['project_name']}")
            return False
        
        print("✅ Config file exists and contains all required keys")
        return True
        
    except json.JSONDecodeError:
        print("❌ Config file is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading config file: {str(e)}")
        return False

def test_directories():
    """Test that required directories exist"""
    required_dirs = [
        "./database",
        "./output", 
        "./models",
        "./src",
        "./notebooks",
        "./image",
        "./test",
        "./config"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print(f"✅ All required directories exist")
    return True

def main():
    print("Running basic tests for ICD Diagnosis Extraction Project...")
    print("-" * 60)
    
    config_ok = test_config_file()
    dirs_ok = test_directories()
    
    print("-" * 60)
    if config_ok and dirs_ok:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())