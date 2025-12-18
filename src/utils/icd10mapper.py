"""
ICD-10 Mapper class for Automated ICD Diagnosis Extraction project
"""

import pandas as pd
from typing import List, Dict, Optional


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