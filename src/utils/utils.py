"""
Utility functions for Automated ICD Diagnosis Extraction project
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
    
    Returns:
        Configured logger object
    """
    logger = logging.getLogger("icd_extraction")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler if specified
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger


def validate_csv_structure(df: pd.DataFrame) -> bool:
    """
    Validate that the CSV has the required structure for ICD diagnosis extraction
    
    Args:
        df: DataFrame to validate
    
    Returns:
        True if structure is valid, False otherwise
    """
    required_columns = [
        'id_pasien',
        'nm_pasien', 
        'jk',
        'umur_pasien',
        'id_kunjungan',
        'tgl_registrasi',
        'nm_dokter',
        'rekam_medis_narasi',
        'diagnosis_structured'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        return False
    
    return True


def map_diagnosis_to_icd10(entities: List[str], mapping_dict: Dict[str, str]) -> List[str]:
    """
    Map diagnosis entities to ICD-10 codes based on a mapping dictionary
    
    Args:
        entities: List of diagnosis entities detected
        mapping_dict: Dictionary mapping terms to ICD-10 codes
    
    Returns:
        List of corresponding ICD-10 codes
    """
    icd_codes = []
    if entities:
        for entity in entities:
            entity_lower = entity.lower()
            for key, code in mapping_dict.items():
                if key in entity_lower and code not in icd_codes:
                    icd_codes.append(code)
    return list(set(icd_codes))


def calculate_simple_accuracy(predicted: List[str], ground_truth: str) -> float:
    """
    Calculate simple accuracy by checking if any predicted entity appears in ground truth
    
    Args:
        predicted: List of predicted entities
        ground_truth: Ground truth diagnosis string
    
    Returns:
        Accuracy score between 0 and 1
    """
    if not predicted or not ground_truth:
        return 0.0
    
    ground_truth_lower = str(ground_truth).lower()
    matches = sum(1 for entity in predicted if entity.lower() in ground_truth_lower)
    
    return matches / len(predicted) if predicted else 0.0


def format_results_for_output(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format results DataFrame for standardized output
    
    Args:
        results_df: Raw results DataFrame
    
    Returns:
        Formatted DataFrame ready for export
    """
    # Ensure consistent column ordering
    expected_cols = [
        'id_pasien',
        'nm_pasien',
        'jk',
        'umur_pasien',
        'id_kunjungan',
        'tgl_registrasi',
        'nm_dokter',
        'rekam_medis_narasi',
        'entities_detected',
        'diagnosis_ground_truth',
        'icd10_codes',
        'match_ground_truth'
    ]
    
    # Add missing columns with default values
    for col in expected_cols:
        if col not in results_df.columns:
            if col == 'icd10_codes':
                results_df[col] = [[] for _ in range(len(results_df))]
            elif col == 'match_ground_truth':
                results_df[col] = [False for _ in range(len(results_df))]
            elif col in ['entities_detected', 'diagnosis_ground_truth']:
                results_df[col] = [None for _ in range(len(results_df))]
            else:
                results_df[col] = [None for _ in range(len(results_df))]
    
    # Return only expected columns in the right order
    return results_df[expected_cols]


class ICD10Mapper:
    """
    Class for mapping diagnosis terms to ICD-10 codes
    """
    
    def __init__(self):
        self.mapping = {
            # Common conditions
            "hypertension": "I10",
            "essential (primary) hypertension": "I10",
            "secondary hypertension": "I15",
            "hypertensive heart disease": "I11",
            "hypertensive chronic kidney disease": "I12",
            "hypertensive heart and chronic kidney disease": "I13",
            "hypertensive crisis": "I16",
            
            # Heart diseases
            "heart failure": "I50",
            "acute myocardial infarction": "I21",
            "chronic ischemic heart disease": "I25",
            "angina pectoris": "I20",
            "atrial fibrillation": "I48",
            "cardiac arrhythmia": "I49",
            
            # Respiratory conditions
            "pneumonia": "J18.9",
            "community-acquired pneumonia": "J18.9", 
            "chronic obstructive pulmonary disease": "J44",
            "asthma": "J45",
            "acute bronchitis": "J20.9",
            "influenza": "J11.1",
            
            # Endocrine disorders
            "type 1 diabetes mellitus": "E10",
            "type 2 diabetes mellitus": "E11",
            "diabetes mellitus": "E14",
            "diabetes with neurological complications": "E10.4",
            "diabetes with renal complications": "E10.2",
            "diabetes with ophthalmic complications": "E10.3",
            "thyroid disorder": "E07.9",
            
            # Neurological conditions
            "stroke": "I63",
            "cerebral infarction": "I63",
            "hemorrhagic stroke": "I61",
            "transient ischemic attack": "G45.9",
            "epilepsy": "G40",
            "dementia": "F03",
            "alzheimer disease": "G30.9",
            
            # Kidney disorders
            "chronic kidney disease": "N18",
            "acute kidney failure": "N17",
            "kidney failure": "N19",
            "nephritis": "N05",
            
            # Mental health
            "major depressive disorder": "F33",
            "depression": "F33",
            "anxiety disorder": "F41.9",
            "generalized anxiety disorder": "F41.1",
            "schizophrenia": "F20",
            
            # Musculoskeletal
            "osteoarthritis": "M19.9",
            "rheumatoid arthritis": "M06.9",
            "back pain": "M54.5",
            "neck pain": "M54.2",
            
            # Digestive system
            "gastroesophageal reflux disease": "K21.9",
            "peptic ulcer": "K27.9",
            "gastritis": "K29.7",
            "cirrhosis": "K74.6",
            
            # Infections
            "sepsis": "A41.9",
            "urinary tract infection": "N39.0",
            "cellulitis": "L03.9",
            "osteomyelitis": "M86.9",
            
            # Cancer
            "lung cancer": "C34.9",
            "breast cancer": "C50.9",
            "colon cancer": "C18.9",
            "prostate cancer": "C61",
            "skin cancer": "C44.9",
            
            # Symptoms and signs
            "fever": "R50.9",
            "headache": "R51",
            "chest pain": "R06.02",
            "shortness of breath": "R06.02",
            "cough": "R05",
            "abdominal pain": "R10.13",
            "fatigue": "R53.83",
            "nausea": "R11.0",
            "vomiting": "R11.10",
            
            # Procedures/tests
            "electrocardiogram": "Z51.89",
            "chest x-ray": "Z03.89",
            "blood test": "Z03.89",
            
            # Other common terms
            "epistaxis": "R04.0",  # nosebleed
            "syncope": "R55",  # fainting
            "dizziness": "R42",
            "insomnia": "G47.00",
            "constipation": "K59.00",
            "diarrhea": "K59.1",
            "obesity": "E66.9",
            "overweight": "E66.3",
            "malnutrition": "E46",
            "anemia": "D64.9",
            "hyperlipidemia": "E78.5",
            "hypothyroidism": "E03.9",
            "hyperthyroidism": "E05.90",
        }
    
    def get_icd10_code(self, term: str) -> Optional[str]:
        """
        Get ICD-10 code for a specific term
        
        Args:
            term: Medical term to look up
        
        Returns:
            ICD-10 code if found, None otherwise
        """
        term_lower = term.lower()
        for key, code in self.mapping.items():
            if key in term_lower:
                return code
        return None
    
    def map_terms_to_codes(self, terms: List[str]) -> List[str]:
        """
        Map a list of terms to ICD-10 codes
        
        Args:
            terms: List of medical terms
        
        Returns:
            List of corresponding ICD-10 codes
        """
        codes = []
        for term in terms:
            term_lower = term.lower()
            for key, code in self.mapping.items():
                if key in term_lower and code not in codes:
                    codes.append(code)
        return codes
