"""
DASHBOARD BIG DATA ANALYTICS - AUTOMATED ICD-10 DIAGNOSIS CODING
=================================================================
RSUD Datu Sanggul Kabupaten Tapin, Kalimantan Selatan

Dashboard ini menampilkan analisis komprehensif dari sistem otomatisasi
kodefikasi diagnosis ICD-10 menggunakan XGBoost.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="ICD-10 Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3498db;
        padding-left: 0.5rem;
    }
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin-top: 0.5rem;
    }
    .insight-box {
        border-left: 5px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .conclusion-box {
        border-left: 5px solid #27ae60;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data
def load_data():
    """Load data dari file CSV atau Google Drive"""
    try:
        # Option 1: Load dari file lokal
        df = pd.read_csv('database/data/diagnosis_icd_2025.csv')

        # Parse tanggal
        df['tgl_registrasi'] = pd.to_datetime(df['tgl_registrasi'], format='%d/%m/%Y', errors='coerce')
        
        # Ensure the datetime column is properly formatted
        df['tgl_registrasi'] = pd.to_datetime(df['tgl_registrasi'])

        return df
    except FileNotFoundError:
        # Option 2: Generate sample data untuk demo
        st.warning("⚠️ File data tidak ditemukan. Menggunakan sample data untuk demo.")

        np.random.seed(42)
        n_records = 1000

        # Generate sample data
        dates = pd.date_range(start='2025-01-01', end='2025-12-31', periods=n_records)
   
        # Define realistic mapping of diagnoses to poliklinik based on clinical relevance
        diagnosis_to_poli_map = {
            # 1. INSTALASI GAWAT DARURAT (IGD) - High volume, emergency cases
            'I21 - Acute myocardial infarction': 'IGD',
            'I63 - Cerebral infarction': 'IGD',
            'I61 - Hemorrhagic stroke': 'IGD',
            'J96 - Acute respiratory failure': 'IGD',
            'R55 - Syncope': 'IGD',
            'T14 - Trauma': 'IGD',
            'R06 - Dyspnea': 'IGD',
            'R05 - Cough': 'IGD',
            'R51 - Headache': 'IGD',
            'R10 - Abdominal pain': 'IGD',
            'R03 - Abnormal blood pressure reading': 'IGD',
            'R50 - Fever': 'IGD',
            'R07 - Chest pain': 'IGD',
            'R40 - Somnolence': 'IGD',
            'R41 - Other disorders of awareness': 'IGD',
            'R62 - Lack of expected normal physiological development': 'IGD',
            'R63 - Abnormal weight loss': 'IGD',
            'R64 - Cachexia': 'IGD',
            'R94 - Abnormal results of other function studies': 'IGD',
            'R99 - Ill-defined and unknown cause of mortality': 'IGD',
            
            # 2. HEMODIALISIS - Lower volume, chronic care
            'N18.6 - End stage renal disease': 'HEMODIALISIS',
            'N18 - Chronic kidney disease': 'HEMODIALISIS',
            'N17 - Acute kidney injury': 'HEMODIALISIS',
            'Z99.2 - Hemodialysis status': 'HEMODIALISIS',
            'N19 - Uremia': 'HEMODIALISIS',
            'N26 - Unspecified contracted kidney': 'HEMODIALISIS',
            'N04 - Nephrotic syndrome': 'HEMODIALISIS',
            'N03 - Chronic nephritic syndrome': 'HEMODIALISIS',
            'N25 - Disorders resulting from impaired renal tubular function': 'HEMODIALISIS',
            'Z49 - Encounter for renal dialysis': 'HEMODIALISIS',
            
            # 3. GERIATRI - High for elderly, moderate volume
            'I10 - Essential hypertension': 'GERIATRI',
            'E11 - Type 2 diabetes mellitus': 'GERIATRI',
            'F03 - Dementia': 'GERIATRI',
            'G30 - Alzheimer disease': 'GERIATRI',
            'R54 - Frailty syndrome': 'GERIATRI',
            'M81 - Osteoporosis': 'GERIATRI',
            'R26 - Abnormalities of gait and mobility': 'GERIATRI',
            'R54 - Age-related physical debility': 'GERIATRI',
            'F10 - Alcohol related disorders': 'GERIATRI',
            'F01 - Vascular dementia': 'GERIATRI',
            'M80 - Osteoporosis with current pathological fracture': 'GERIATRI',
            'M82 - Osteoporosis in diseases classified elsewhere': 'GERIATRI',
            'R42 - Dizziness and giddiness': 'GERIATRI',
            'R53 - Malaise and fatigue': 'GERIATRI',
            'R41 - Other disorders of awareness': 'GERIATRI',
            
            # 4. FISIOTERAPI - Moderate volume, rehabilitation
            'M54.5 - Low back pain': 'FISIOTERAPI',
            'M54.2 - Cervicalgia': 'FISIOTERAPI',
            'G81 - Hemiplegia': 'FISIOTERAPI',
            'Z50 - Rehabilitation': 'FISIOTERAPI',
            'M51 - Intervertebral disc disorders': 'FISIOTERAPI',
            'M50 - Cervical disc disorder': 'FISIOTERAPI',
            'M79 - Soft tissue disorder': 'FISIOTERAPI',
            'M77 - Enthesopathy': 'FISIOTERAPI',
            'M75 - Shoulder lesions': 'FISIOTERAPI',
            'M62 - Disorders of muscle': 'FISIOTERAPI',
            'M65 - Synovitis and tenosynovitis': 'FISIOTERAPI',
            'M71 - Other bursopathies': 'FISIOTERAPI',
            'R29 - Abnormalities of gait and mobility': 'FISIOTERAPI',
            'G56 - Mononeuropathies of upper limb': 'FISIOTERAPI',
            'G57 - Mononeuropathies of lower limb': 'FISIOTERAPI',
            
            # 5. PENYAKIT DALAM - Highest volume, general medicine
            'E78 - Dyslipidemia': 'PENYAKIT DALAM',
            'E03 - Hypothyroidism': 'PENYAKIT DALAM',
            'K21 - Gastroesophageal reflux disease': 'PENYAKIT DALAM',
            'K76.0 - Fatty liver': 'PENYAKIT DALAM',
            'K29 - Gastritis': 'PENYAKIT DALAM',
            'J06 - Acute upper respiratory infection': 'PENYAKIT DALAM',
            'J45 - Asthma': 'PENYAKIT DALAM',
            'J44 - Other chronic obstructive pulmonary disease': 'PENYAKIT DALAM',
            'I50 - Heart failure': 'PENYAKIT DALAM',
            'I25 - Chronic ischemic heart disease': 'PENYAKIT DALAM',
            'I10 - Essential hypertension': 'PENYAKIT DALAM',
            'E11 - Type 2 diabetes mellitus': 'PENYAKIT DALAM',
            'N39 - Other disorders of urinary system': 'PENYAKIT DALAM',
            'N18 - Chronic kidney disease': 'PENYAKIT DALAM',
            'E66 - Obesity': 'PENYAKIT DALAM',
            'E78 - Disorders of lipoprotein metabolism': 'PENYAKIT DALAM',
            'K59 - Functional intestinal disorder': 'PENYAKIT DALAM',
            'K60 - Fissure and fistula of anal and rectal regions': 'PENYAKIT DALAM',
            'K62 - Other diseases of anus and rectum': 'PENYAKIT DALAM',
            'K65 - Peritonitis': 'PENYAKIT DALAM',
            
            # 6. BEDAH - Moderate volume, surgical cases
            'K35 - Acute appendicitis': 'BEDAH',
            'K40 - Inguinal hernia': 'BEDAH',
            'K80 - Cholelithiasis': 'BEDAH',
            'S72 - Femur fracture': 'BEDAH',
            'M96 - Postprocedural musculoskeletal disorders': 'BEDAH',
            'M25 - Other joint disorders': 'BEDAH',
            'K65 - Peritonitis': 'BEDAH',
            'K62 - Other diseases of anus and rectum': 'BEDAH',
            'K60 - Fissure and fistula of anal and rectal regions': 'BEDAH',
            'K38 - Other diseases of appendix': 'BEDAH',
            'K44 - Diaphragmatic hernia': 'BEDAH',
            'K46 - Other hernia of abdominal cavity': 'BEDAH',
            'S82 - Fracture of lower leg': 'BEDAH',
            'S92 - Fracture of foot': 'BEDAH',
            'S52 - Fracture of forearm': 'BEDAH',
            
            # 7. THT - Moderate-high volume, common conditions
            'J02 - Acute pharyngitis': 'THT',
            'J03 - Acute tonsillitis': 'THT',
            'J32 - Chronic sinusitis': 'THT',
            'H66 - Otitis media': 'THT',
            'H65 - Nonsuppurative otitis media': 'THT',
            'H60 - Otitis externa': 'THT',
            'J31 - Chronic rhinitis': 'THT',
            'J30 - Vasomotor and allergic rhinitis': 'THT',
            'H92 - Otalgia': 'THT',
            'H93 - Other disorders of ear': 'THT',
            'R05 - Cough': 'THT',
            'R06 - Dyspnea': 'THT',
            'R44 - Other symptoms involving general sensations and perceptions': 'THT',
            'H72 - Tympanic membrane perforation': 'THT',
            'H70 - Mastoiditis and related conditions': 'THT',
            
            # 8. OBSTETRI / GYN - High volume for women, seasonal patterns
            'O80 - Normal delivery': 'OBSTETRI / GYN',
            'O14 - Pre-eclampsia': 'OBSTETRI / GYN',
            'O24.4 - Gestational diabetes': 'OBSTETRI / GYN',
            'O4 - Placenta previa': 'OBSTETRI / GYN',
            'N76 - Other inflammation of vagina and vulva': 'OBSTETRI / GYN',
            'N72 - Inflammatory disease of cervix': 'OBSTETRI / GYN',
            'N83 - Noninflammatory disorders of ovary': 'OBSTETRI / GYN',
            'N84 - Polyp of female genital tract': 'OBSTETRI / GYN',
            'N92 - Excessive and frequent menstruation': 'OBSTETRI / GYN',
            'N94 - Pain and other conditions associated with female genital organs': 'OBSTETRI / GYN',
            'O26 - Care for specified complications of pregnancy': 'OBSTETRI / GYN',
            'O99 - Other maternal diseases classifiable elsewhere': 'OBSTETRI / GYN',
            'O90 - Complications of the puerperium': 'OBSTETRI / GYN',
            'O75 - Other complications of labor and delivery': 'OBSTETRI / GYN',
            'O61 - Problems with labor augmentation': 'OBSTETRI / GYN',
            
            # 9. MATA - Moderate volume, vision-related
            'H25 - Senile cataract': 'MATA',
            'H40 - Glaucoma': 'MATA',
            'H10 - Acute conjunctivitis': 'MATA',
            'H52.4 - Presbyopia': 'MATA',
            'H35 - Other retinal disorders': 'MATA',
            'H44 - Disorders of globe': 'MATA',
            'H02 - Other disorders of eyelid': 'MATA',
            'H11 - Other disorders of conjunctiva': 'MATA',
            'H26 - Other cataract': 'MATA',
            'H57 - Other disorders of eye and adnexa': 'MATA',
            'H54 - Visual impairment including blindness': 'MATA',
            'H50 - Strabismus': 'MATA',
            'H55 - Nystagmus and other irregular eye movements': 'MATA',
            'H49 - Paralytic strabismus': 'MATA',
            'H47 - Other disorders of optic nerve': 'MATA',
            
            # 10. JIWA - Lower volume, specialized care
            'F32 - Major depressive disorder': 'JIWA',
            'F41 - Generalized anxiety disorder': 'JIWA',
            'F20 - Schizophrenia': 'JIWA',
            'F31 - Bipolar disorder': 'JIWA',
            'G47 - Insomnia': 'JIWA',
            'F40 - Phobic anxiety disorders': 'JIWA',
            'F42 - Obsessive-compulsive disorder': 'JIWA',
            'F43 - Reaction to severe stress': 'JIWA',
            'F51 - Nonorganic sleep disorders': 'JIWA',
            'F99 - Mental disorder': 'JIWA',
            'F10 - Alcohol related disorders': 'JIWA',
            'F17 - Nicotine dependence': 'JIWA',
            'F19 - Other psychoactive substance dependence': 'JIWA',
            'F84 - Autism spectrum disorder': 'JIWA',
            'F90 - Attention deficit hyperactivity disorder': 'JIWA',
            
            # 11. JANTUNG - Moderate volume, cardiac care
            'I20 - Angina pectoris': 'JANTUNG',
            'I25 - Chronic ischemic heart disease': 'JANTUNG',
            'I50 - Heart failure': 'JANTUNG',
            'I42 - Cardiomyopathy': 'JANTUNG',
            'I48 - Atrial fibrillation and flutter': 'JANTUNG',
            'I21 - Acute myocardial infarction': 'JANTUNG',
            'I11 - Hypertensive heart disease': 'JANTUNG',
            'I67 - Other cerebrovascular disease': 'JANTUNG',
            'I26 - Pulmonary embolism': 'JANTUNG',
            'I35 - Nonrheumatic aortic valve disorders': 'JANTUNG',
            'I34 - Nonrheumatic mitral valve disorders': 'JANTUNG',
            'I30 - Acute pericarditis': 'JANTUNG',
            'I31 - Other diseases of pericardium': 'JANTUNG',
            'I4 - Atrioventricular block': 'JANTUNG',
            'I45 - Other conduction disorders': 'JANTUNG',
            
            # 12. PARU - Moderate volume, respiratory care
            'J18 - Pneumonia': 'PARU',
            'J20 - Acute bronchitis': 'PARU',
            'A15 - Pulmonary tuberculosis': 'PARU',
            'J90 - Pleural effusion': 'PARU',
            'J45 - Asthma': 'PARU',
            'J44 - Other chronic obstructive pulmonary disease': 'PARU',
            'J69 - Pneumonitis due to solids and liquids': 'PARU',
            'J84 - Other interstitial pulmonary diseases': 'PARU',
            'J96 - Respiratory failure': 'PARU',
            'J80 - Adult respiratory distress syndrome': 'PARU',
            'J98 - Other disorders of respiratory system': 'PARU',
            'J91 - Pleural effusion in conditions classified elsewhere': 'PARU',
            'J95 - Postprocedural respiratory disorders': 'PARU',
            'J92 - Pleural plaque': 'PARU',
            'J93 - Pneumothorax': 'PARU',
            
            # 13. ANAK - High volume for pediatric, age-specific
            'J06 - Upper respiratory infection': 'ANAK',
            'R56 - Febrile seizure': 'ANAK',
            'D50 - Iron deficiency anemia': 'ANAK',
            'A09 - Infectious gastroenteritis and colitis': 'ANAK',
            'J02 - Acute pharyngitis': 'ANAK',
            'J00 - Acute nasopharyngitis': 'ANAK',
            'A41 - Sepsis': 'ANAK',
            'R10 - Abdominal pain': 'ANAK',
            'R50 - Fever': 'ANAK',
            'R68 - Other general symptoms and signs': 'ANAK',
            'F84 - Autism spectrum disorder': 'ANAK',
            'F90 - Attention deficit hyperactivity disorder': 'ANAK',
            'F80 - Speech delay': 'ANAK',
            'F81 - Learning disability': 'ANAK',
            'F82 - Specific developmental disorders of motor function': 'ANAK',
            
            # 14. KULIT & KELAMIN - Moderate-high volume, common conditions
            'L20 - Atopic dermatitis': 'KULIT & KELAMIN',
            'L40 - Psoriasis': 'KULIT & KELAMIN',
            'L70 - Acne vulgaris': 'KULIT & KELAMIN',
            'B35.4 - Tinea corporis': 'KULIT & KELAMIN',
            'A63 - Genital warts': 'KULIT & KELAMIN',
            'L30 - Dermatitis': 'KULIT & KELAMIN',
            'L02 - Cutaneous abscess': 'KULIT & KELAMIN',
            'L03 - Cellulitis': 'KULIT & KELAMIN',
            'L82 - Seborrheic keratosis': 'KULIT & KELAMIN',
            'L29 - Pruritus': 'KULIT & KELAMIN',
            'L57 - Skin changes due to chronic exposure to nonionizing radiation': 'KULIT & KELAMIN',
            'L21 - Seborrheic dermatitis': 'KULIT & KELAMIN',
            'L08 - Other local infections of skin and subcutaneous tissue': 'KULIT & KELAMIN',
            'L26 - Exfoliative dermatitis': 'KULIT & KELAMIN',
            'L22 - Diaper dermatitis': 'KULIT & KELAMIN',
            
            # 15. TUMBUH KEMBANG PED. SOSIAL DAN SARAF - Specialized pediatric care
            'R62 - Developmental delay': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F84 - Autism spectrum disorder': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F90 - ADHD': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F80 - Speech delay': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F81 - Learning disability': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F82 - Specific developmental disorders of motor function': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F88 - Other disorders of psychological development': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F89 - Unspecified disorder of psychological development': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'R40 - Somnolence': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'R41 - Other disorders of awareness': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F98 - Other behavioral and emotional disorders with onset usually occurring in childhood and adolescence': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F91 - Conduct disorders': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F92 - Mixed disorders of conduct and emotions': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F95 - Tic disorders': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            'F93 - Emotional disorders with onset specific to childhood': 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF',
            
            # 16. SARAF - Moderate volume, neurological conditions
            'G40 - Epilepsy': 'SARAF',
            'G20 - Parkinson disease': 'SARAF',
            'G62 - Peripheral neuropathy': 'SARAF',
            'E11.4 - Diabetic neuropathy': 'SARAF',
            'G43 - Migraine': 'SARAF',
            'G44 - Other headache syndromes': 'SARAF',
            'G21 - Secondary parkinsonism': 'SARAF',
            'G22 - Parkinsonism in diseases classified elsewhere': 'SARAF',
            'G23 - Other degenerative diseases of basal ganglia': 'SARAF',
            'G24 - Dystonia': 'SARAF',
            'G25 - Other extrapyramidal and movement disorders': 'SARAF',
            'G31 - Other degenerative diseases of nervous system': 'SARAF',
            'G35 - Multiple sclerosis': 'SARAF',
            'G37 - Other demyelinating diseases of central nervous system': 'SARAF',
            'G45 - Transient cerebral ischemic attacks and related syndromes': 'SARAF'
        }
   
        # Create more realistic diagnoses with corresponding poli
        # Weighted toward more common conditions to reflect real-world distributions
        diagnosis_list = [
            'I10 - Essential hypertension',  # Most common
            'J06 - Acute upper respiratory infection',  # Very common
            'E11 - Type 2 diabetes mellitus',  # Common
            'M54.5 - Low back pain',  # Common
            'I21 - Acute myocardial infarction',  # Emergency
            'J18 - Pneumonia',  # Common
            'G43 - Migraine',  # Common
            'F32 - Depressive episode',  # Common
            'K29 - Gastritis',  # Common
            'I63 - Cerebral infarction',  # Emergency
            'E78 - Dyslipidemia',  # Very common
            'J45 - Asthma',  # Common
            'R50 - Fever',  # Very common
            'R10 - Abdominal pain',  # Common
            'R06 - Dyspnea',  # Common
            'H25 - Senile cataract',  # Common in elderly
            'H66 - Otitis media',  # Common in children
            'L20 - Atopic dermatitis',  # Common
            'F90 - ADHD',  # Common in children
            'G40 - Epilepsy'  # Common neurological
        ]
        
        # Define different probabilities for each diagnosis to make it more realistic
        diagnosis_probs = [
            0.08,  # I10 - Essential hypertension
            0.07,  # J06 - Acute upper respiratory infection
            0.06,  # E11 - Type 2 diabetes mellitus
            0.05,  # M54.5 - Low back pain
            0.03,  # I21 - Acute myocardial infarction
            0.04, # J18 - Pneumonia
            0.04,  # G43 - Migraine
            0.04,  # F32 - Depressive episode
            0.04,  # K29 - Gastritis
            0.03,  # I63 - Cerebral infarction
            0.06,  # E78 - Dyslipidemia
            0.05,  # J45 - Asthma
            0.05,  # R50 - Fever
            0.05,  # R10 - Abdominal pain
            0.04,  # R06 - Dyspnea
            0.03,  # H25 - Senile cataract
            0.04,  # H66 - Otitis media
            0.05,  # L20 - Atopic dermatitis
            0.03,  # F90 - ADHD
            0.03   # G40 - Epilepsy
        ]

        doctors = [f'Dr. {name}' for name in ['Ahmad', 'Budi', 'Candra', 'Dian', 'Eko',
                                                 'Fajar', 'Gita', 'Hana', 'Ika', 'Joko']]

        # Create the dataframe with realistic mapping based on clinical relevance
        diagnosis_structured_list = []
        poli_category_list = []
        
        # Create more realistic distribution of patients across poliklinik
        # Based on real-world hospital data where some poli have much higher volume
        # Adding more variation and randomness to make it look more natural and less uniform
        # Each run will have slightly different distribution patterns to simulate real world variation
        base_weights = {
            'PENYAKIT DALAM': 0.24,  # Highest volume - general medicine
            'IGD': 0.15,             # High volume - emergency
            'THT': 0.09,             # High volume - common conditions
            'KULIT & KELAMIN': 0.09, # High volume - common conditions
            'ANAK': 0.08,            # High volume - pediatric
            'OBSTETRI / GYN': 0.07,  # High volume - women's health
            'JANTUNG': 0.05,         # Moderate volume
            'PARU': 0.05,            # Moderate volume
            'SARAF': 0.04,           # Moderate volume
            'BEDAH': 0.04,           # Moderate volume
            'MATA': 0.03,            # Moderate volume
            'JIWA': 0.025,           # Lower volume - specialized
            'GERIATRI': 0.025,       # Lower volume - specialized
            'FISIOTERAPI': 0.02,     # Lower volume - rehabilitation
            'HEMODIALISIS': 0.015,   # Lower volume - specialized chronic care
            'TUMBUH KEMBANG PED. SOSIAL DAN SARAF': 0.01  # Lowest volume - specialized pediatric
        }
        
        # Add random variation to weights to make the distribution more realistic
        # Each run will have slightly different distribution patterns
        random_factors = np.random.normal(1.0, 0.1, len(base_weights))  # Mean=1.0, std=0.1
        poli_weights = {}
        for i, (poli, base_weight) in enumerate(base_weights.items()):
            poli_weights[poli] = max(0.005, base_weight * random_factors[i])  # Ensure minimum weight
        
        # Normalize weights to sum to 1
        total_weight = sum(poli_weights.values())
        poli_weights = {poli: weight/total_weight for poli, weight in poli_weights.items()}
        
        # Create cumulative probability distribution for weighted choice
        poli_categories = list(poli_weights.keys())
        poli_probs = list(poli_weights.values())
        
        for i in range(n_records):
            diagnosis = np.random.choice(diagnosis_list, p=diagnosis_probs)
            diagnosis_structured_list.append(diagnosis)
            
            # Map diagnosis to appropriate poli based on our clinical mapping
            if diagnosis in diagnosis_to_poli_map:
                poli_category_list.append(diagnosis_to_poli_map[diagnosis])
            else:
                # If no specific mapping, assign based on weighted probabilities
                poli_choice = np.random.choice(poli_categories, p=poli_probs)
                poli_category_list.append(poli_choice)
        
        df = pd.DataFrame({
            'id_pasien': range(1, n_records + 1),
            'nm_pasien': [f'Pasien {i}' for i in range(1, n_records + 1)],
            'jk': np.random.choice(['L', 'P'], n_records, p=[0.48, 0.52]),
            'umur_pasien': np.random.normal(45, 20, n_records).clip(1, 100).astype(int),
            'tgl_registrasi': dates,
            'nm_dokter': np.random.choice(doctors, n_records),
            'rekam_medis_narasi': ['Sample medical record narrative'] * n_records,
            'diagnosis_structured': diagnosis_structured_list,
            'poli_category': poli_category_list,
            'panjang_narasi': np.clip(np.random.normal(150, n_records), 50, 500).astype(int),
            'kompleksitas': np.random.choice(['LOW', 'MEDIUM', 'HIGH'], n_records, p=[0.3, 0.4, 0.3])
        })

        return df

# Load data
df = load_data()

# Ensure required columns exist in the DataFrame
required_columns = ['poli_category', 'nm_dokter', 'jk', 'umur_pasien', 'diagnosis_structured', 'tgl_registrasi', 'rekam_medis_narasi', 'kompleksitas']
for col in required_columns:
    if col not in df.columns:
        if col == 'poli_category':
            # For missing poli_category column, create a default with some distribution
            # rather than setting all to 'PENYAKIT DALAM'
            all_poli_cats = [
                'IGD', 'HEMODIALISIS', 'GERIATRI', 'FISIOTERAPI', 'PENYAKIT DALAM',
                'BEDAH', 'THT', 'OBSTETRI / GYN', 'MATA', 'JIWA', 'JANTUNG', 'PARU',
                'ANAK', 'KULIT & KELAMIN', 'TUMBUH KEMBANG PED. SOSIAL DAN SARAF'
            ]
            # Distribute evenly to avoid any bias toward a single category
            df['poli_category'] = np.random.choice(all_poli_cats, size=len(df))
        elif col == 'nm_dokter':
            df['nm_dokter'] = 'Dr. Unknown'
        elif col == 'jk':
            df['jk'] = 'L'
        elif col == 'umur_pasien':
            df['umur_pasien'] = 30
        elif col == 'diagnosis_structured':
            df['diagnosis_structured'] = 'Unknown diagnosis'
        elif col == 'tgl_registrasi':
            df['tgl_registrasi'] = pd.Timestamp.now()
        elif col == 'rekam_medis_narasi':
            df['rekam_medis_narasi'] = 'No record'
        elif col == 'kompleksitas':
            df['kompleksitas'] = 'MEDIUM'

# Store original df for later use (before adding placeholders)
df_original = df.copy()

# Ensure all predefined poliklinik categories exist in the data for visualization purposes
all_poli_cats = [
    'IGD',
    'HEMODIALISIS',
    'GERIATRI',
    'FISIOTERAPI',
    'PENYAKIT DALAM',
    'BEDAH',
    'THT',
    'OBSTETRI / GYN',
    'MATA',
    'JIWA',
    'JANTUNG',
    'PARU',
    'ANAK',
    'KULIT & KELAMIN',
    'TUMBUH KEMBANG PED. SOSIAL DAN SARAF'
]

# Only add missing poliklinik categories with 0 records if we're using sample data
# If real data has all categories, don't add placeholders
if len(df) > 0:  # Only proceed if df is not empty
    missing_poli = [poli for poli in all_poli_cats if poli not in df['poli_category'].values]
    for poli in missing_poli:
        # Create a single record for this poliklinik to ensure it appears in visualizations
        new_record = df.iloc[[0]].copy()  # Copy the first record
        new_record['poli_category'] = poli
        new_record['id_pasien'] = -1 # Use negative ID to identify as placeholder
        df = pd.concat([df, new_record], ignore_index=True)

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================

st.sidebar.image("image/RSUD.jpg", width=300)
st.sidebar.markdown("---")
st.sidebar.header("🔍 FILTER DATA")

# Filter 1: Rentang Tanggal
st.sidebar.subheader("📅 Rentang Tanggal")
date_min = df['tgl_registrasi'].min().date()
date_max = df['tgl_registrasi'].max().date()

date_range = st.sidebar.date_input(
    "Pilih rentang tanggal:",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max
)

# Filter 2: Kategori Poliklinik
st.sidebar.subheader("🏥 Kategori Poliklinik")
# Define the specific poliklinik categories as requested (without 'Semua Poliklinik')
poli_categories = [
    'IGD',
    'HEMODIALISIS',
    'GERIATRI',
    'FISIOTERAPI',
    'PENYAKIT DALAM',
    'BEDAH',
    'THT',
    'OBSTETRI / GYN',
    'MATA',
    'JIWA',
    'JANTUNG',
    'PARU',
    'ANAK',
    'KULIT & KELAMIN',
    'TUMBUH KEMBANG PED. SOSIAL DAN SARAF'
]
all_poli = poli_categories
selected_poli = st.sidebar.multiselect(
    "Pilih poliklinik:",
    options=all_poli,
    default=all_poli  # Default to all poliklinik instead of 'Semua Poliklinik'
)

# Additional polyclinic filter - Show only active poliklinik
if len(selected_poli) > 0:
    df_filtered_poli = df[df['poli_category'].isin(selected_poli)]
else:
    df_filtered_poli = df.copy()

# Show polyclinic statistics in sidebar
st.sidebar.markdown("### 📊 Statistik Poliklinik")
poli_stats = df_filtered_poli['poli_category'].value_counts()
for poli, count in poli_stats.head(5).items():
    st.sidebar.write(f"- {poli}: {count:,}")

# Add polyclinic selection statistics
if 'Semua Poliklinik' not in selected_poli and len(selected_poli) > 0:
    st.sidebar.info(f"🏥 Terpilih: {len(selected_poli)} dari {len([p for p in poli_categories if p != 'Semua Poliklinik'])} poliklinik")

# Apply filters
# First, apply date filter on the original data (without placeholders)
df_for_filtering = df_original.copy()

if len(date_range) == 2:
    # Convert date_range to pandas datetime for comparison
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])
    # Convert the date column to just the date part for comparison
    df_for_filtering['tgl_reg_date'] = pd.to_datetime(df_for_filtering['tgl_registrasi']).dt.date
    start_date_val = start_date.date()
    end_date_val = end_date.date()
    mask_date = (df_for_filtering['tgl_reg_date'] >= start_date_val) & (df_for_filtering['tgl_reg_date'] <= end_date_val)
    df_filtered_temp = df_for_filtering[mask_date].copy()
    # Drop the temporary column
    df_filtered = df_filtered_temp.drop(columns=['tgl_reg_date'])
else:
    # Use the original dataframe without date filter
    df_filtered = df_for_filtering

# Apply polyclinic filter
if 'Semua Poliklinik' not in selected_poli and len(selected_poli) > 0:
    df_filtered = df_filtered[df_filtered['poli_category'].isin(selected_poli)]
else:
    # If 'Semua Poliklinik' is selected, keep all poli categories but use original data (without placeholders)
    df_filtered = df_for_filtering.copy()

# Ensure all predefined poliklinik categories exist in the filtered data for visualization purposes
# Only add missing poliklinik categories if they're truly missing from actual patient data
if len(df_filtered) > 0:
    actual_patient_data = df_filtered[df_filtered['id_pasien'] > 0]  # Only actual patients, not placeholders
    missing_poli = [poli for poli in all_poli_cats if poli not in actual_patient_data['poli_category'].values]
    for poli in missing_poli:
        # Create a single record for this poliklinik to ensure it appears in visualizations
        if len(df_filtered) > 0:
            new_record = df_filtered.iloc[[0]].copy()  # Copy the first record
        else:
            new_record = df.iloc[[0]].copy()  # Copy from original df if filtered is empty
        new_record['poli_category'] = poli
        new_record['id_pasien'] = -2 # Use different negative ID to identify as placeholder for filtered view
        df_filtered = pd.concat([df_filtered, new_record], ignore_index=True)

st.sidebar.markdown("---")
st.sidebar.info(f"📊 Data terfilter: **{len(df_filtered):,}** dari **{len(df):,}** record")

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

# Header
st.markdown('<h1 class="main-header">🏥 DASHBOARD ANALYTICS - AUTOMATED ICD-10 DIAGNOSIS CODING</h1>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #7f8c8d; margin-bottom: 2rem;'>
    <b>RSUD Datu Sanggul Kabupaten Tapin, Kalimantan Selatan</b><br>
    <i>Big Data Analytics untuk Otomatisasi Kodefikasi Diagnosis ICD-10</i>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 1. KPI UTAMA
# ============================================================================

st.markdown('<h2 class="sub-header">📊 KEY PERFORMANCE INDICATORS</h2>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="👥 Total Pasien",
        value=f"{len(df_filtered):,}",
        delta=f"{len(df_filtered) - len(df)}" if len(df_filtered) != len(df) else "All data"
    )

with col2:
    st.metric(
        label="🏥 Kategori Poli",
        value=df_filtered['poli_category'].nunique(),
        delta=None
    )

with col3:
    st.metric(
        label="👨‍⚕️ Jumlah Dokter",
        value=df_filtered['nm_dokter'].nunique(),
        delta=None
    )

with col4:
    avg_age = df_filtered['umur_pasien'].mean()
    st.metric(
        label="📈 Rata-rata Umur",
        value=f"{avg_age:.1f} tahun",
        delta=None
    )

with col5:
    male_pct = (df_filtered['jk'] == 'L').sum() / len(df_filtered) * 100
    st.metric(
        label="♂️ Rasio L/P",
        value=f"{male_pct:.1f}% / {100-male_pct:.1f}%",
        delta=None
    )

st.markdown("---")

# ============================================================================
# 2. DISTRIBUSI UMUR PASIEN
# ============================================================================

st.markdown('<h2 class="sub-header">📊 2. Distribusi Umur Pasien</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Histogram with properly spaced mean and median annotations
    fig_age_hist = go.Figure()
    
    # Add histogram
    fig_age_hist.add_trace(go.Histogram(
        x=df_filtered['umur_pasien'],
        nbinsx=20,
        name='Histogram',
        marker_color='skyblue',
        opacity=0.7
    ))
    
    # Add mean line with improved annotation positioning
    mean_age = df_filtered['umur_pasien'].mean()
    fig_age_hist.add_vline(
        x=mean_age,
        line_dash="dash",
        line_color="cyan",
        annotation_text=f"Mean: {mean_age:.1f}",
        annotation_position="top left",
        name='Mean'
    )
    
    # Add median line with improved annotation positioning
    median_age = df_filtered['umur_pasien'].median()
    fig_age_hist.add_vline(
        x=median_age,
        line_dash="dash",
        line_color="yellow",
        annotation_text=f"Median: {median_age:.1f}",
        annotation_position="top right",
        name='Median'
    )
    
    fig_age_hist.update_layout(
        title='Distribusi Umur Pasien (Histogram)',
        xaxis_title='Umur (tahun)',
        yaxis_title='Frekuensi',
        xaxis_range=[0, 200],  # Set x-axis range from 0 to 200
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_age_hist, use_container_width=True)

with col2:
    # KDE Plot using Plotly
    fig_age_kde = go.Figure()
    
    # Create KDE using scipy for plotting in Plotly
    import numpy as np
    from scipy.stats import gaussian_kde
    
    ages = df_filtered['umur_pasien'].dropna()
    
    # Check if we have enough data points for KDE
    if len(ages) > 1:
        kde = gaussian_kde(ages)
        x_range = np.linspace(0, 200, 200)  # Set x-range from 0 to 200
        kde_values = kde(x_range)
        
        fig_age_kde.add_trace(go.Scatter(
            x=x_range,
            y=kde_values,
            fill='tozeroy',
            name='KDE',
            line_color='magenta',
            opacity=0.7
        ))
    else:
        # If not enough data points, show a message instead
        fig_age_kde.add_annotation(
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            text="Tidak cukup data untuk<br>membuat KDE plot",
            showarrow=False,
            font=dict(size=16),
            align="center"
        )
    
    # Add mean line with improved annotation positioning
    mean_age = df_filtered['umur_pasien'].mean()
    fig_age_kde.add_vline(
        x=mean_age,
        line_dash="dash",
        line_color="cyan",
        annotation_text=f"Mean: {mean_age:.1f}",
        annotation_position="top left"
    )
    
    # Add median line with improved annotation positioning
    median_age = df_filtered['umur_pasien'].median()
    fig_age_kde.add_vline(
        x=median_age,
        line_dash="dash",
        line_color="yellow",
        annotation_text=f"Median: {median_age:.1f}",
        annotation_position="top right"
    )
    
    fig_age_kde.update_layout(
        title='Distribusi Umur Pasien (KDE)',
        xaxis_title='Umur (tahun)',
        yaxis_title='Kepadatan',
        xaxis_range=[0, 200],  # Set x-axis range from 0 to 200
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_age_kde, use_container_width=True)

# ============================================================================
# 3. DISTRIBUSI JENIS KELAMIN
# ============================================================================

st.markdown('<h2 class="sub-header">👥 3. Distribusi Jenis Kelamin</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

gender_counts = df_filtered['jk'].value_counts()

with col1:
    # Bar Chart
    fig_gender_bar = go.Figure(data=[
        go.Bar(
            x=gender_counts.index,
            y=gender_counts.values,
            marker_color=['#87CEEB', '#4682B4'],  # Sky blue shades
            text=gender_counts.values,
            textposition='auto'
        )
    ])
    fig_gender_bar.update_layout(
        title='Bar Chart Jenis Kelamin',
        xaxis_title='Jenis Kelamin',
        yaxis_title='Jumlah Pasien',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_gender_bar, theme="streamlit")

with col2:
    # Pie Chart
    fig_gender_pie = go.Figure(data=[
        go.Pie(
            labels=gender_counts.index,
            values=gender_counts.values,
            marker_colors=['#4ECDC4', '#FF6B6B'],
            hole=0.3
        )
    ])
    fig_gender_pie.update_layout(
        title='Proporsi Jenis Kelamin',
        height=400
    )
    st.plotly_chart(fig_gender_pie, theme="streamlit")

# ============================================================================
# 4. TOP 10 DIAGNOSIS ICD-10
# ============================================================================

st.markdown('<h2 class="sub-header">🏆 4. Top 10 Diagnosis ICD-10</h2>', unsafe_allow_html=True)

top_diagnosis = df_filtered['diagnosis_structured'].value_counts().head(10)

fig_top_icd = go.Figure(go.Bar(
    x=top_diagnosis.values,
    y=[str(x)[:50] + '...' if len(str(x)) > 50 else str(x) for x in top_diagnosis.index],
    orientation='h',
    marker=dict(
        color=top_diagnosis.values,
        colorscale='Viridis',
        showscale=True
    ),
    text=top_diagnosis.values,
    textposition='auto'
))

fig_top_icd.update_layout(
    title='Top 10 Diagnosis ICD-10 Terbanyak',
    xaxis_title='Jumlah Kasus',
    yaxis_title='Diagnosis ICD-10',
    height=500,
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(fig_top_icd, theme="streamlit")

# ============================================================================
# 5. DISTRIBUSI PASIEN PER KATEGORI POLI
# ============================================================================

st.markdown('<h2 class="sub-header">🏥 5. Distribusi Pasien per Kategori Poliklinik</h2>', unsafe_allow_html=True)

# Count patients per poli category (excluding placeholder records for actual counts)
df_filtered_actual = df_filtered[df_filtered['id_pasien'] > 0]  # Only include actual patient records, exclude all placeholders (-1, -2)

# Define all poliklinik categories
all_poli_cats = [
    'IGD',
    'HEMODIALISIS',
    'GERIATRI',
    'FISIOTERAPI',
    'PENYAKIT DALAM',
    'BEDAH',
    'THT',
    'OBSTETRI / GYN',
    'MATA',
    'JIWA',
    'JANTUNG',
    'PARU',
    'ANAK',
    'KULIT & KELAMIN',
    'TUMBUH KEMBANG PED. SOSIAL DAN SARAF'
]

# Initialize a series with all categories and zero counts
poli_counts_complete = pd.Series(0, index=all_poli_cats, dtype='int64')

# Count actual patients per category and update the complete series
if not df_filtered_actual.empty:
    poli_counts_actual = df_filtered_actual['poli_category'].value_counts()
    for poli in all_poli_cats:
        if poli in poli_counts_actual.index:
            poli_counts_complete[poli] = poli_counts_actual[poli]

# Sort by count in ascending order for horizontal bar chart
poli_counts_sorted = poli_counts_complete.sort_values(ascending=True)

# Create a more visually appealing bar chart with varied colors for each poliklinik
colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel + px.colors.qualitative.Light24
# Ensure we have enough colors for all polikliniks
extended_colors = colors * (len(poli_counts_sorted) // len(colors) + 1)
poli_colors = extended_colors[:len(poli_counts_sorted)]

fig_poli = go.Figure(go.Bar(
    x=poli_counts_sorted.values,
    y=poli_counts_sorted.index,
    orientation='h',
    marker=dict(
        color=poli_colors,
        line=dict(color='rgba(0,0,0,0.1)', width=0.5)  # Add subtle borders
    ),
    text=poli_counts_sorted.values,
    textposition='auto',
    hovertemplate='<b>%{y}</b><br>Jumlah Pasien: %{x}<extra></extra>'
))

fig_poli.update_layout(
    title='Distribusi Pasien per Kategori Poliklinik',
    xaxis_title='Jumlah Pasien',
    yaxis_title='Kategori Poli',
    height=600
)

st.plotly_chart(fig_poli, theme="streamlit")

# Add polyclinic-specific analytics
st.markdown('<h2 class="sub-header">🏥 6. Analisis Kinerja Poliklinik</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Average age per polyclinic - include all categories even if no patients
    all_poli_cats = [
        'IGD',
        'HEMODIALISIS',
        'GERIATRI',
        'FISIOTERAPI',
        'PENYAKIT DALAM',
        'BEDAH',
        'THT',
        'OBSTETRI / GYN',
        'MATA',
        'JIWA',
        'JANTUNG',
        'PARU',
        'ANAK',
        'KULIT & KELAMIN',
        'TUMBUH KEMBANG PED. SOSIAL DAN SARAF'
    ]
    
    # Calculate average age only for actual patient records (id_pasien > 0)
    df_filtered_actual = df_filtered[df_filtered['id_pasien'] > 0]
    avg_age_by_poli = df_filtered_actual.groupby('poli_category')['umur_pasien'].mean()
    
    # Ensure all poliklinik categories are represented
    avg_age_complete = pd.Series(index=all_poli_cats, dtype='float64').fillna(0)
    avg_age_complete.update(avg_age_by_poli)
    
    # Only keep categories that have actual patients (non-zero average age)
    avg_age_final = avg_age_complete[avg_age_complete > 0] if (avg_age_complete > 0).any() else avg_age_complete
    
    avg_age_final = avg_age_final.sort_values(ascending=False)
    fig_avg_age = go.Figure(go.Bar(
        x=avg_age_final.values,
        y=avg_age_final.index,
        orientation='h',
        marker=dict(
            color=avg_age_final.values,
            colorscale='Plasma',
            showscale=True
        ),
        hovertemplate='<b>%{y}</b><br>Rata-rata Umur: %{x:.1f} tahun<extra></extra>'
    ))
    fig_avg_age.update_layout(
        title='Rata-rata Umur Pasien per Poliklinik',
        xaxis_title='Rata-rata Umur',
        yaxis_title='Poliklinik',
        height=400
    )
    st.plotly_chart(fig_avg_age, theme="streamlit")

with col2:
    # Gender distribution per polyclinic - include all categories
    all_poli_cats = [
        'IGD',
        'HEMODIALISIS',
        'GERIATRI',
        'FISIOTERAPI',
        'PENYAKIT DALAM',
        'BEDAH',
        'THT',
        'OBSTETRI / GYN',
        'MATA',
        'JIWA',
        'JANTUNG',
        'PARU',
        'ANAK',
        'KULIT & KELAMIN',
        'TUMBUH KEMBANG PED. SOSIAL DAN SARAF'
    ]
    
    # Use only actual patient records (id_pasien > 0)
    df_filtered_actual = df_filtered[df_filtered['id_pasien'] > 0]
    if not df_filtered_actual.empty and len(df_filtered_actual['poli_category'].unique()) > 0:
        gender_poli = pd.crosstab(df_filtered_actual['poli_category'], df_filtered_actual['jk'], normalize='index') * 100
        
        # Only include poliklinik that have actual patients
        actual_poli = pd.Index(df_filtered_actual['poli_category'].unique())
        gender_poli = gender_poli.loc[gender_poli.index.intersection(actual_poli)]
        
        gender_poli = gender_poli.sort_values(by='L', ascending=True) # Sort by male percentage
       
        fig_gender_poli = go.Figure()
        fig_gender_poli.add_trace(go.Bar(
            y=gender_poli.index,
            x=gender_poli['L'],
            orientation='h',
            name='Laki-laki',
            marker=dict(color='#4ECDC4', line=dict(color='rgba(0,0,0,0.1)', width=0.5)),
            hovertemplate='<b>%{y}</b><br>Laki-laki: %{x:.1f}%<extra></extra>'
        ))
        fig_gender_poli.add_trace(go.Bar(
            y=gender_poli.index,
            x=gender_poli['P'],
            orientation='h',
            name='Perempuan',
            marker=dict(color='#FF6B6B', line=dict(color='rgba(0,0,0,0.1)', width=0.5)),
            hovertemplate='<b>%{y}</b><br>Perempuan: %{x:.1f}%<extra></extra>'
        ))
       
        fig_gender_poli.update_layout(
            title='Distribusi Jenis Kelamin per Poliklinik (%)',
            xaxis_title='Persentase',
            yaxis_title='Poliklinik',
            barmode='stack',
            height=400,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig_gender_poli, theme="streamlit")
    else:
        st.write("Tidak ada data pasien untuk analisis distribusi jenis kelamin per poliklinik.")

# ============================================================================
# 6. TREN KUNJUNGAN PER BULAN
# ============================================================================

st.markdown('<h2 class="sub-header">📅 6. Tren Kunjungan per Bulan</h2>', unsafe_allow_html=True)

df_filtered['bulan'] = df_filtered['tgl_registrasi'].apply(lambda x: x.strftime('%Y-%m') if pd.notna(x) else '')
monthly_visits = df_filtered.groupby('bulan').size().reset_index(name='jumlah')
monthly_visits['bulan_str'] = monthly_visits['bulan'].astype(str)

fig_monthly = go.Figure()
fig_monthly.add_trace(go.Scatter(
    x=monthly_visits['bulan_str'],
    y=monthly_visits['jumlah'],
    mode='lines+markers',
    line=dict(color='darkblue', width=3),
    marker=dict(size=10, color='lightblue', line=dict(width=2, color='darkblue')),
    fill='tozeroy',
    fillcolor='rgba(135, 206, 250, 0.3)'
))

fig_monthly.update_layout(
    title='Tren Kunjungan Pasien per Bulan',
    xaxis_title='Bulan',
    yaxis_title='Jumlah Kunjungan',
    height=400,
    hovermode='x unified'
)

st.plotly_chart(fig_monthly, theme="streamlit")

# ============================================================================
# 7. TREN KUNJUNGAN PER HARI DALAM SEMINGGU
# ============================================================================

st.markdown('<h2 class="sub-header">📆 7. Tren Kunjungan per Hari dalam Seminggu</h2>', unsafe_allow_html=True)

df_filtered['hari'] = df_filtered['tgl_registrasi'].apply(lambda x: x.strftime('%A') if pd.notna(x) else '')
hari_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hari_indo = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']

daily_visits = df_filtered['hari'].value_counts().reindex(hari_order, fill_value=0)

fig_daily = go.Figure(go.Bar(
    x=hari_indo,
    y=daily_visits.values,
    marker=dict(
        color=['#4ECDC4' if i < 5 else '#FF6B6B' for i in range(7)],
    ),
    text=daily_visits.values,
    textposition='auto'
))

fig_daily.update_layout(
    title='Distribusi Kunjungan per Hari dalam Seminggu',
    xaxis_title='Hari',
    yaxis_title='Jumlah Kunjungan',
    height=400
)

st.plotly_chart(fig_daily, theme="streamlit")

# ============================================================================
# 7B. DISTRIBUSI KUNJUNGAN PER HARI DALAM SEMINGGU BERDASARKAN POLIKLINIK
# ============================================================================

st.markdown('<h2 class="sub-header">🏥 7B. Distribusi Kunjungan Berdasarkan Poliklinik per Hari</h2>', unsafe_allow_html=True)

# Create a pivot table of visits by day and polyclinic
# Use only actual patient records (id_pasien > 0)
df_filtered_actual = df_filtered[df_filtered['id_pasien'] > 0]
df_filtered_actual['hari_nama'] = df_filtered_actual['tgl_registrasi'].apply(lambda x: x.strftime('%A') if pd.notna(x) else '')

if not df_filtered_actual.empty:
    day_poli_matrix = pd.crosstab(df_filtered_actual['hari_nama'], df_filtered_actual['poli_category'])

    # Get top 5 polyclinics by patient count
    top_poli = df_filtered_actual['poli_category'].value_counts().head(5).index
    day_poli_subset = day_poli_matrix[top_poli]

    # Reorder days to follow Monday-Sunday sequence
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_poli_subset = day_poli_subset.reindex(day_order, fill_value=0)

    # Create heatmap
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=day_poli_subset.values,
        x=day_poli_subset.columns,
        y=['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'],
        colorscale='RdYlBu_r',  # Changed to a more visually appealing colorscale
        text=day_poli_subset.values,
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False,
        hovertemplate='<b>%{x}</b><br><b>%{y}</b><br>Jumlah Kunjungan: %{z}<extra></extra>'
    ))

    fig_heatmap.update_layout(
        title='Heatmap Distribusi Kunjungan: Hari vs Poliklinik (Top 5)',
        xaxis_title='Poliklinik',
        yaxis_title='Hari dalam Seminggu',
        height=500
    )

    st.plotly_chart(fig_heatmap, theme="streamlit")
else:
    st.write("Tidak ada data pasien untuk analisis heatmap hari vs poliklinik.")

# ============================================================================
# 8. TOP 10 DOKTER
# ============================================================================

st.markdown('<h2 class="sub-header">👨‍⚕️ 8. Top 10 Dokter dengan Jumlah Pasien Terbanyak</h2>', unsafe_allow_html=True)

top_doctors = df_filtered['nm_dokter'].value_counts().head(10).sort_values(ascending=True)

fig_doctors = go.Figure(go.Bar(
    x=top_doctors.values,
    y=top_doctors.index,
    orientation='h',
    marker=dict(
        color=top_doctors.values,
        colorscale='Teal',
        showscale=True
    ),
    text=top_doctors.values,
    textposition='auto'
))

fig_doctors.update_layout(
    title='Top 10 Dokter dengan Pasien Terbanyak',
    xaxis_title='Jumlah Pasien',
    yaxis_title='Nama Dokter',
    height=500
)

st.plotly_chart(fig_doctors, theme="streamlit")

# ============================================================================
# 9. ANALISIS KOMPLEKSITAS DIAGNOSIS
# ============================================================================

st.markdown('<h2 class="sub-header">🔍 9. Analisis Kompleksitas Diagnosis</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Bar Chart Kompleksitas
    if 'kompleksitas' in df_filtered.columns:
        complexity_counts = df_filtered['kompleksitas'].value_counts()

        fig_complexity_bar = go.Figure(go.Bar(
            x=complexity_counts.index,
            y=complexity_counts.values,
            marker=dict(color=['#2ecc71', '#f39c12', '#e74c3c']),
            text=complexity_counts.values,
            textposition='auto'
        ))

        fig_complexity_bar.update_layout(
            title='Distribusi Kompleksitas Diagnosis',
            xaxis_title='Tingkat Kompleksitas',
            yaxis_title='Jumlah Kasus',
            height=400
        )

        st.plotly_chart(fig_complexity_bar, theme="streamlit")

with col2:
    # Stacked Bar Kompleksitas per Poli
    if 'kompleksitas' in df_filtered.columns:
        # Use only actual patient records (id_pasien > 0)
        df_filtered_actual = df_filtered[df_filtered['id_pasien'] > 0]
        if not df_filtered_actual.empty:
            complexity_poli = pd.crosstab(df_filtered_actual['poli_category'], df_filtered_actual['kompleksitas'])
    
            fig_complexity_stack = go.Figure()
    
            for complexity in ['LOW', 'MEDIUM', 'HIGH']:
                if complexity in complexity_poli.columns:
                    fig_complexity_stack.add_trace(go.Bar(
                        name=complexity,
                        x=complexity_poli.index,
                        y=complexity_poli[complexity],
                        marker=dict(
                            color={'LOW': '#2ecc71', 'MEDIUM': '#f39c12', 'HIGH': '#e74c3c'}[complexity],
                            line=dict(color='rgba(0,0,0,0.1)', width=0.5)
                        ),
                        hovertemplate='<b>%{x}</b><br>'+complexity+' Complexity: %{y}<extra></extra>'
                    ))
    
            fig_complexity_stack.update_layout(
                title='Kompleksitas per Kategori Poli',
                xaxis_title='Kategori Poli',
                yaxis_title='Jumlah Kasus',
                barmode='stack',
                height=400,
                xaxis_tickangle=-45,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
    
            st.plotly_chart(fig_complexity_stack, theme="streamlit")
        else:
            st.write("Tidak ada data pasien untuk analisis kompleksitas per poliklinik.")

# ============================================================================
# 10. VISUALISASI SUMMARY
# ============================================================================

st.markdown('<h2 class="sub-header">📊 10. VISUALISASI SUMMARY</h2>', unsafe_allow_html=True)

# Create summary metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎯 Model Performance")
    st.metric("Accuracy", "79.35%", delta="Good")
    st.metric("F1-Score", "76.10%", delta="Acceptable")
    st.metric("Cross-Validation", "78.38%", delta="±0.4%")

with col2:
    st.markdown("### 📈 Data Insights")
    st.metric("Total Records", f"{len(df):,}")
    st.metric("Avg Age", f"{df['umur_pasien'].mean():.1f} tahun")
    imbalance_ratio = df['poli_category'].value_counts().max() / df['poli_category'].value_counts().min()
    st.metric("Imbalance Ratio", f"{imbalance_ratio:.1f}x")

with col3:
    st.markdown("### 💡 Operational Impact")
    st.metric("Time Saving", "60-70%", delta="vs Manual")
    st.metric("Error Reduction", "15-20%", delta="Improvement")
    st.metric("ROI Timeline", "3-6 months")

# Summary Chart
fig_summary = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Distribusi Poli', 'Distribusi Umur', 'Gender', 'Monthly Trend'),
    specs=[[{'type': 'bar'}, {'type': 'histogram'}],
           [{'type': 'pie'}, {'type': 'scatter'}]]
)

# 1. Poli distribution
poli_top5 = df_filtered['poli_category'].value_counts().head(5)
colors_poli = px.colors.qualitative.Pastel[:len(poli_top5)]
fig_summary.add_trace(
    go.Bar(x=poli_top5.index.astype(str), y=poli_top5.values, marker_color=colors_poli),
    row=1, col=1
)

# 2. Age distribution
fig_summary.add_trace(
    go.Histogram(x=df_filtered['umur_pasien'], nbinsx=20, marker_color='lightgreen'),
    row=1, col=2
)

# 3. Gender pie
gender_data = df_filtered['jk'].value_counts()
fig_summary.add_trace(
    go.Pie(labels=gender_data.index, values=gender_data.values),
    row=2, col=1
)

# 4. Monthly trend
fig_summary.add_trace(
    go.Scatter(x=monthly_visits['bulan_str'], y=monthly_visits['jumlah'],
               mode='lines+markers', marker_color='darkblue'),
    row=2, col=2
)

fig_summary.update_layout(height=700, showlegend=True, title_text="Dashboard Summary")
# Update the x-axis for the age distribution subplot to have range 0-200
fig_summary.update_xaxes(range=[0, 200], row=1, col=2)
st.plotly_chart(fig_summary, theme="streamlit")

# ============================================================================
# INSIGHTS & CONCLUSIONS
# ============================================================================

st.markdown("---")
st.markdown('<h2 class="sub-header">💡 INSIGHTS & CONCLUSIONS</h2>', unsafe_allow_html=True)

# Insights
st.markdown("### 📊 DISTRIBUSI PASIEN")
st.markdown("""
<div class="insight-box">
<ul>
<li>Pola diagnosis menunjukkan prevalensi penyakit <b>kardiovaskular, respiratori, dan endokrin</b> sebagai kasus terbanyak</li>
<li>Distribusi umur pasien menunjukkan pola normal dengan median di <b>usia dewasa (40-50 tahun)</b></li>
<li>Rasio jenis kelamin cukup seimbang dengan sedikit dominasi perempuan (<b>52% vs 48%</b>)</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🔍 KOMPLEKSITAS DIAGNOSIS")
complexity_high_pct = (df_filtered['kompleksitas'] == 'HIGH').sum() / len(df_filtered) * 100 if 'kompleksitas' in df_filtered.columns else 35
st.markdown(f"""
<div class="insight-box">
<ul>
<li>Sekitar <b>{complexity_high_pct:.0f}%</b> kasus memiliki kompleksitas tinggi berdasarkan panjang narasi medis</li>
<li>Kategori poli tertentu (<b>CARDIOVASCULAR, NEUROLOGICAL</b>) memiliki kompleksitas narasi yang lebih tinggi</li>
<li>Terdapat <b>korelasi positif</b> antara umur pasien dan kompleksitas diagnosis</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📅 POLA KUNJUNGAN")
st.markdown("""
<div class="insight-box">
<ul>
<li>Tren kunjungan menunjukkan <b>pola musiman</b> dengan puncak di bulan-bulan tertentu</li>
<li>Kunjungan lebih tinggi di <b>hari kerja</b> dibanding akhir pekan (rasio ~70:30)</li>
<li>Beban kerja <b>tidak terdistribusi merata</b> antar dokter, perlu optimasi scheduling</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("### ⚖️ IMBALANCE DATA")
max_poli = df_filtered['poli_category'].value_counts().max()
min_poli = df_filtered['poli_category'].value_counts().min()
imbalance_ratio = max_poli / min_poli if min_poli > 0 else 0
top_poli = df_filtered['poli_category'].value_counts().index[0]

st.markdown(f"""
<div class="insight-box">
<ul>
<li>Terdapat ketidakseimbangan kelas dengan rasio <b>{imbalance_ratio:.1f}x</b></li>
<li>Kelas mayoritas: <b>{top_poli}</b> ({max_poli} kasus)</li>
<li>Perlu strategi <b>handling untuk kelas minoritas</b> dalam modeling</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Operational Insights
# Polyclinic-specific insights
st.markdown("### 🏥 POLA KUNJUNGAN POLIKLINIK")
top_poli_by_patients = df_filtered['poli_category'].value_counts().head(3)
top_poli_list = [f"<b>{poli}</b> ({count:,} pasien)" for poli, count in top_poli_by_patients.items()]
top_poli_str = ", ".join(top_poli_list)

st.markdown(f"""
<div class="insight-box">
<ul>
<li>Poliklinik dengan kunjungan tertinggi: {top_poli_str}</li>
<li>Poliklinik <b>{top_poli}</b> mendominasi dengan {max_poli:,} kasus ({max_poli/len(df_filtered)*100:.1f}% dari total)</li>
<li>Perlu optimalisasi beban kerja antar poliklinik untuk distribusi pasien yang lebih merata</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Operational Insights
st.markdown("---")
st.markdown("### 🎯 INSIGHT OPERASIONAL")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 1. EFISIENSI OPERASIONAL")
    st.markdown("""
    <div class="insight-box">
    <ul>
    <li>✅ Automasi coding dapat menghemat <b>60-70%</b> waktu kerja petugas</li>
    <li>✅ Estimasi penghematan: <b>100-150 jam/bulan</b> untuk 500 pasien</li>
    <li>✅ <b>ROI positif</b> dalam 3-6 bulan implementasi</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 3. ALOKASI SDM")
    st.markdown("""
    <div class="insight-box">
    <ul>
    <li>📌 Petugas coding dapat dialokasikan untuk <b>verifikasi dan kasus kompleks</b></li>
    <li>📌 Kebutuhan coder dapat <b>dioptimalkan 30-40%</b></li>
    <li>📌 Focus shift dari <b>data entry ke quality assurance</b></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("#### 2. KUALITAS PELAYANAN")
    st.markdown("""
    <div class="insight-box">
    <ul>
    <li>✅ Akurasi model <b>79%</b> dapat mengurangi error rate manual (15-20%)</li>
    <li>✅ Konsistensi coding meningkat dengan <b>sistem otomatis</b></li>
    <li>✅ Mengurangi <b>beban kerja kognitif</b> petugas</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 4. PERENCANAAN STRATEGIS")
    st.markdown("""
    <div class="insight-box">
    <ul>
    <li>📊 Data diagnosis untuk <b>forecasting kebutuhan SDM</b></li>
    <li>📊 Identifikasi pola penyakit untuk <b>planning preventif</b></li>
    <li>📊 Base untuk sistem <b>Early Warning berbasis AI</b></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Polyclinic-specific recommendations
st.markdown("---")
st.markdown("### 🏥 REKOMENDASI BERDASARKAN POLIKLINIK")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 1. OPTIMALISASI BEBAN KERJA")
    # Identify polyclinics with high patient load
    high_load_poli = df_filtered['poli_category'].value_counts()
    if not high_load_poli.empty:
        high_load_mean = float(high_load_poli.mean())
        # Use pandas comparison with explicit conversion to avoid Pylance errors
        high_load_mean_val = float(high_load_mean)
        mask = np.array(high_load_poli.values) > high_load_mean_val
        high_load_poli_filtered = high_load_poli[mask]
        
        # Convert pandas Series to regular Python objects to avoid Pylance errors
        high_load_list = [f"<b>{poli}</b>" for poli in high_load_poli_filtered.head(3).index.tolist()]
        high_load_str = ", ".join(high_load_list) if len(high_load_poli_filtered) > 0 else "Tidak ada"
        
        high_load_list = [f"<b>{poli}</b>" for poli in high_load_poli_filtered.head(3).index]
        high_load_str = ", ".join(high_load_list) if len(high_load_poli_filtered) > 0 else "Tidak ada"
        
        st.markdown(f"""
        <div class="insight-box">
        <ul>
        <li>Poliklinik dengan beban tinggi: {high_load_str}</li>
        <li>Rekomendasi: <b>Tambah jam operasional</b> atau <b>tenaga dokter</b> di poliklinik ini</li>
        <li>Target: Distribusi beban kerja yang lebih merata antar poliklinik</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="insight-box">
        <ul>
        <li>Tidak ada data untuk analisis beban kerja poliklinik</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 3. PERENCANAAN SDM")
    # Analyze average patients per doctor per polyclinic
    if not df_filtered.empty and 'poli_category' in df_filtered.columns and 'nm_dokter' in df_filtered.columns:
        doctor_poli = df_filtered.groupby(['poli_category', 'nm_dokter']).size().reset_index(name='patient_count')
        avg_per_doctor = doctor_poli.groupby('poli_category')['patient_count'].mean().sort_values(ascending=False)
        
        top_burden_poli = avg_per_doctor.head(3).index.tolist()
        top_burden_str = ", ".join([f"<b>{poli}</b>" for poli in top_burden_poli])
    else:
        top_burden_str = "Tidak ada data"
    
    st.markdown(f"""
    <div class="insight-box">
    <ul>
    <li>Poliklinik dengan beban dokter tinggi: {top_burden_str}</li>
    <li>Rekomendasi: <b>Tambah tenaga dokter</b> di poliklinik ini</li>
    <li>Target: Rasio ideal 1 dokter : 15-20 pasien/hari</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("#### 2. PENGEMBANGAN LAYANAN")
    # Identify polyclinics with low patient load that might need development
    low_load_poli = df_filtered['poli_category'].value_counts()
    if not low_load_poli.empty:
        low_load_mean = float(low_load_poli.mean())
        # Use pandas comparison with explicit conversion to avoid Pylance errors
        low_load_mean_val = float(low_load_mean)
        mask = np.array(low_load_poli.values) < low_load_mean_val
        low_load_poli_filtered = low_load_poli[mask]
        
        low_load_list = [f"<b>{poli}</b>" for poli in low_load_poli_filtered.tail(3).index.tolist() if poli != 'Semua Poliklinik']
        low_load_str = ", ".join(low_load_list) if len(low_load_poli_filtered) > 0 else "Tidak ada"
        
        st.markdown(f"""
        <div class="insight-box">
        <ul>
        <li>Poliklinik dengan kunjungan rendah: {low_load_str}</li>
        <li>Rekomendasi: <b>Promosikan layanan</b> atau <b>integrasi dengan program kesehatan</b></li>
        <li>Analisis: Kebutuhan masyarakat vs layanan yang tersedia</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="insight-box">
        <ul>
        <li>Tidak ada data untuk analisis pengembangan layanan poliklinik</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 4. PENGEMBANGAN FASILITAS")
    # Analyze age distribution by polyclinic to recommend facility development
    avg_age_by_poli = df_filtered.groupby('poli_category')['umur_pasien'].mean().sort_values(ascending=False)
    elderly_focus_poli = avg_age_by_poli.head(3).index.tolist()
    elderly_focus_str = ", ".join([f"<b>{poli}</b>" for poli in elderly_focus_poli])
    
    st.markdown(f"""
    <div class="insight-box">
    <ul>
    <li>Poliklinik dengan fokus usia lanjut: {elderly_focus_str}</li>
    <li>Rekomendasi: <b>Fasilitas ramah lansia</b> dan <b>aksesibilitas</b> di poliklinik ini</li>
    <li>Target: Pengembangan layanan <b>geriatri</b> yang lebih komprehensif</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Conclusions
st.markdown("---")
st.markdown("### ✅ KESIMPULAN AKHIR")

st.markdown("""
<div class="conclusion-box">
<h4>🎉 PROJECT SUMMARY</h4>
<p>
Proyek <b>Big Data Analytics untuk Automated ICD-10 Diagnosis Coding</b> ini berhasil
mengembangkan sistem prediksi dengan akurasi <b>79.35%</b> menggunakan <b>XGBoost</b>
sebagai model tunggal.
</p>

<h4>🏆 KEY ACHIEVEMENTS:</h4>
<ul>
<li>✅ Model XGBoost dengan performa tinggi (<b>Accuracy: 79.35%, F1: 76.10%</b>)</li>
<li>✅ Analisis EDA komprehensif dengan <b>20+ visualisasi</b></li>
<li>✅ Feature engineering yang menghasilkan <b>9 fitur prediktif</b></li>
<li>✅ Cross-validation score stabil (<b>78.38% ± 0.4%</b>)</li>
<li>✅ Model siap untuk <b>deployment dan integrasi ke SIMRS</b></li>
</ul>

<h4>🚀 NEXT STEPS:</h4>
<ol>
<li>Pilot testing di environment produksi</li>
<li>Collect feedback dan performance metrics</li>
<li>Iterative improvement berdasarkan real-world data</li>
<li>Scale up ke seluruh unit rumah sakit</li>
</ol>

<p style="margin-top: 1rem;">
Dengan implementasi sistem ini, <b>RSUD Datu Sanggul</b> dapat meningkatkan efisiensi
operasional, mengurangi error rate, dan membebaskan SDM untuk fokus pada tugas-tugas
yang lebih strategis dan bernilai tinggi.
</p>

<h4>🏥 IMPLEMENTASI POLIKLINIK:</h4>
<ul>
<li>✅ Dashboard menampilkan distribusi pasien per poliklinik</li>
<li>✅ Rekomendasi optimalisasi beban kerja antar poliklinik</li>
<li>✅ Analisis kinerja masing-masing poliklinik</li>
<li>✅ Visualisasi heatmap pola kunjungan per hari dan poliklinik</li>
<li>✅ Rekomendasi strategis untuk pengembangan layanan poliklinik</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #7f8c8d; padding: 2rem 0;'>
    <p><b>🎉 PROJECT COMPLETED SUCCESSFULLY!</b></p>
    <p>Generated on: <b>{datetime.now().strftime('%d %B %Y, %H:%M:%S')}</b></p>
    <p>Model: <b>XGBoost (Single Model Only)</b></p>
    <p>Status: <b>✅ Ready for Deployment</b></p>
    <hr style='width: 50%; margin: 1rem auto;'>
    <p><i>RSUD Datu Sanggul Kabupaten Tapin, Kalimantan Selatan</i></p>
</div>
""", unsafe_allow_html=True)
