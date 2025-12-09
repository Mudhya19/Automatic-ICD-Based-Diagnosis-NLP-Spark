"""
Main entry point for Automated ICD Diagnosis Extraction application
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import setup_logging, validate_csv_structure
from src.icd_extraction_pipeline import ICDDiagnosisExtractor


def main():
    parser = argparse.ArgumentParser(description="Automated ICD Diagnosis Extraction")
    parser.add_argument("--input", type=str, help="Path to input CSV file", 
                        default="../database/diagnosis_icd_2025.csv")
    parser.add_argument("--output", type=str, help="Path to output directory", 
                        default="../output/")
    parser.add_argument("--log-level", type=str, default="INFO", 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging level")
    parser.add_argument("--input-col", type=str, default="rekam_medis_narasi",
                        help="Name of the input column containing medical text")
    parser.add_argument("--output-col", type=str, default="entities_detected",
                        help="Name of the output column for extracted entities")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("Starting Automated ICD Diagnosis Extraction...")
    
    # Validate input file
    if not os.path.exists(args.input):
        logger.error(f"Input file does not exist: {args.input}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize extractor
        extractor = ICDDiagnosisExtractor()
        
        # Load data
        import pandas as pd
        logger.info(f"Loading data from: {args.input}")
        df = pd.read_csv(args.input)
        
        # Validate structure
        if not validate_csv_structure(df):
            logger.error("CSV structure validation failed")
            sys.exit(1)
        
        # Convert to Spark DataFrame
        spark_df = extractor.spark.createDataFrame(df)
        
        # Extract diagnoses
        logger.info("Extracting diagnoses...")
        results = extractor.extract_diagnoses(spark_df, args.input_col, args.output_col)
        
        # Evaluate results
        logger.info("Evaluating extraction results...")
        eval_metrics = extractor.evaluate_extraction(results)
        
        # Print results
        print(f"\nExtraction Results:")
        print(f"  Accuracy: {eval_metrics['accuracy']:.2f}%")
        print(f"  Total Records Processed: {eval_metrics['total_records']}")
        print(f"  Correctly Matched Records: {eval_metrics['correctly_matched_records']}")
        print(f"  Incorrectly Matched Records: {eval_metrics['incorrectly_matched_records']}")
        
        # Save results
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"{args.output}/hasil_ekstraksi_diagnosis_rsud_{timestamp}.csv"
        results.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")
        
        # Show sample results
        print(f"\nSample Results:")
        print(results[['nm_pasien', args.output_col, 'icd10_codes']].head())
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        sys.exit(1)
    
    logger.info("ICD Diagnosis Extraction completed successfully!")


if __name__ == "__main__":
    main()