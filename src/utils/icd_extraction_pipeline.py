"""
ICD Diagnosis Extraction Pipeline using Spark NLP
"""

import sparknlp
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from sparknlp.base import DocumentAssembler
from sparknlp.annotator import Tokenizer, NerDLModel, NerConverter
import pandas as pd
from typing import Optional
import logging
from .utils import ICD10Mapper


class ICDDiagnosisExtractor:
    """
    Class for extracting ICD diagnoses from medical records using Spark NLP
    """
    
    def __init__(self, spark_session: Optional[SparkSession] = None):
        """
        Initialize the ICD Diagnosis Extractor
        
        Args:
            spark_session: Optional Spark session, if None will create a new one
        """
        self.spark = spark_session or sparknlp.start()
        self.pipeline = None
        self.icd_mapper = ICD10Mapper()
        self.logger = logging.getLogger(__name__)
        
        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
    
    def build_pipeline(self, input_col: str = "rekam_medis_narasi", 
                      output_col: str = "entities") -> Pipeline:
        """
        Build the Spark NLP pipeline for clinical NER
        
        Args:
            input_col: Input column name containing medical text
            output_col: Output column name for extracted entities
        
        Returns:
            Spark ML Pipeline object
        """
        # Document assembler
        document_assembler = DocumentAssembler() \
            .setInputCol(input_col) \
            .setOutputCol("document")
        
        # Tokenizer
        tokenizer = Tokenizer() \
            .setInputCols(["document"]) \
            .setOutputCol("token")
        
        # Load clinical NER model
        ner_model = NerDLModel.pretrained("ner_dl_clinical", "en") \
            .setInputCols(["document", "token"]) \
            .setOutputCol("ner")
        
        # Convert NER output to entities
        ner_converter = NerConverter() \
            .setInputCols(["document", "token", "ner"]) \
            .setOutputCol(output_col)
        
        # Create pipeline
        self.pipeline = Pipeline(stages=[
            document_assembler,
            tokenizer,
            ner_model,
            ner_converter
        ])
        
        return self.pipeline
    
    def extract_diagnoses(self, df, input_col: str = "rekam_medis_narasi", 
                         output_col: str = "entities_detected") -> pd.DataFrame:
        """
        Extract diagnoses from medical records DataFrame
        
        Args:
            df: Spark DataFrame containing medical records
            input_col: Input column name containing medical text
            output_col: Output column name for extracted entities
        
        Returns:
            Pandas DataFrame with extracted diagnoses
        """
        # Build pipeline
        pipeline = self.build_pipeline(input_col, output_col)
        
        # Fit and transform the data
        self.logger.info("Fitting and transforming data...")
        model = pipeline.fit(df)
        results = model.transform(df)
        
        # Select relevant columns
        results_selected = results.selectExpr(
            "id_pasien",
            "nm_pasien",
            "jk",
            "umur_pasien", 
            "id_kunjungan",
            "tgl_registrasi",
            "nm_dokter",
            "rekam_medis_narasi",
            f"{output_col}.result as {output_col}",
            "diagnosis_structured as diagnosis_ground_truth"
        )
        
        # Convert to Pandas for further processing
        results_pd = results_selected.toPandas()
        
        # Map to ICD-10 codes
        results_pd['icd10_codes'] = results_pd[output_col].apply(
            lambda x: self.icd_mapper.map_terms_to_codes(x) if x else []
        )
        
        return results_pd
    
    def evaluate_extraction(self, results_df: pd.DataFrame,
                           entities_col: str = "entities_detected",
                           ground_truth_col: str = "diagnosis_ground_truth") -> dict:
        """
        Evaluate the quality of diagnosis extraction
        
        Args:
            results_df: DataFrame with extraction results
            entities_col: Column name with extracted entities
            ground_truth_col: Column name with ground truth diagnoses
        
        Returns:
            Dictionary with evaluation metrics
        """
        total_records = len(results_df)
        if total_records == 0:
            return {"accuracy": 0.0, "total_records": 0}
        
        # Calculate matches
        matches = 0
        for _, row in results_df.iterrows():
            entities = row[entities_col]
            ground_truth = str(row[ground_truth_col]).lower() if pd.notna(row[ground_truth_col]) else ""
            
            if entities is not None and isinstance(entities, list) and len(entities) > 0:
                for entity in entities:
                    if entity and entity.lower() in ground_truth:
                        matches += 1
                        break  # Count as one match per record if any entity matches
        
        accuracy = (matches / total_records) * 100 if total_records > 0 else 0.0
        
        return {
            "accuracy": accuracy,
            "total_records": total_records,
            "correctly_matched_records": matches,
            "incorrectly_matched_records": total_records - matches
        }


def main():
    """
    Main function to demonstrate the ICD Diagnosis Extraction Pipeline
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize extractor
    extractor = ICDDiagnosisExtractor()
    
    # Load sample data
    logger.info("Loading sample data...")
    try:
        df = pd.read_csv("../database/diagnosis_icd_2025.csv")
        spark_df = extractor.spark.createDataFrame(df)
        
        # Extract diagnoses
        logger.info("Extracting diagnoses...")
        results = extractor.extract_diagnoses(spark_df)
        
        # Evaluate results
        logger.info("Evaluating extraction...")
        eval_metrics = extractor.evaluate_extraction(results)
        
        print(f"Extraction completed!")
        print(f"Accuracy: {eval_metrics['accuracy']:.2f}%")
        print(f"Total records processed: {eval_metrics['total_records']}")
        
        # Save results
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"../output/hasil_ekstraksi_diagnosis_{timestamp}.csv"
        results.to_csv(output_file, index=False)
        print(f"Results saved to: {output_file}")
        
        # Show sample results
        print("\nSample results:")
        print(results[['nm_pasien', 'entities_detected', 'icd10_codes']].head())
        
    except FileNotFoundError:
        logger.error("Sample data file not found. Please ensure database/diagnosis_icd_2025.csv exists.")
        # Create a sample file for demonstration
        sample_data = {
            'id_pasien': ['153284', '153285', '153286'],
            'nm_pasien': ['H. KURSANI Tn', 'Siti Nurhaliza', 'Budi Santoso'],
            'jk': ['L', 'P', 'L'],
            'umur_pasien': [71, 55, 45],
            'id_kunjungan': ['2025/01/01/000004', '2025/01/02/000005', '2025/01/03/000006'],
            'tgl_registrasi': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'nm_dokter': ['dr. Resti Riyandina Mujiarto', 'dr. Bambang Sutrisno', 'dr. Rina Widyaningsih'],
            'rekam_medis_narasi': [
                'Patient: H. KURSANI Tn, Age: 71 years old. Chief Complaint: nosebleed since 10 PM last night. Physical Examination: Blood pressure 180/110 mmHg. Assessment: Hypertensive emergency with epistaxis. Diagnosis: Essential hypertension, Epistaxis.',
                'Patient: Siti Nurhaliza, Age: 55 years old. Chief Complaint: Shortness of breath for 1 day, cough. Physical Examination: SpO2 92%, bilateral lung crackles. Assessment: Community-acquired pneumonia. Diagnosis: Community-acquired pneumonia, Hypertension.',
                'Patient: Budi Santoso, Age: 45 years old. Post-operative day 3 appendectomy. Physical Examination: Surgical wound healing well, no infection. Assessment: Recovery from surgery. Diagnosis: Status post-appendectomy, Overweight.'
            ],
            'diagnosis_structured': [
                'Essential (primary) hypertension, Epistaxis',
                'Community-acquired pneumonia, Hypertension stage 2, Type 2 diabetes mellitus',
                'Status post-appendectomy, Overweight, Hypertension'
            ]
        }
        
        sample_df = pd.DataFrame(sample_data)
        sample_df.to_csv("../database/diagnosis_icd_2025.csv", index=False)
        print("Created sample data file. Please run the extraction again.")


if __name__ == "__main__":
    main()