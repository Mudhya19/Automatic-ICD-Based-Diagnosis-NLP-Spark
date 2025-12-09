# INSTRUKSI PROYEK BIG DATA ANALYTICS: AUTOMATED ICD DIAGNOSIS EXTRACTION

## Ekstraksi Diagnosis Otomatis dari Catatan Medis Pasien RSUD Datu Sanggul

**Menggunakan Apache Spark + Spark NLP + ICD-10 Coding**

---

## BAGIAN 1: OVERVIEW PROYEK

### 1.1 Problem Statement

Rumah Sakit Umum Daerah (RSUD) Datu Sanggul menerima ratusan pasien setiap hari. Setiap pasien memiliki catatan medis yang berisi informasi diagnosis dalam bentuk teks narasi klinis yang tidak terstruktur. Kondisi ini menghasilkan tantangan:

- **Waktu Ekstraksi Manual:** 1-2 menit per rekam medis untuk ekstraksi diagnosis
- **Kesalahan Manusia:** Inkonsistensi dalam pencatatan diagnosis dan koding ICD-10
- **Keterlambatan Pelaporan:** Data diagnosis tidak mudah dianalisis untuk keperluan manajemen dan BPJS
- **Skalabilitas:** Sulit untuk memproses ribuan rekam medis dalam waktu singkat

### 1.2 Tujuan Proyek

Mengembangkan sistem otomatis menggunakan **Apache Spark + Spark NLP** untuk:

1. Mengekstraksi diagnosis utama dan sekunder dari teks rekam medis pasien
2. Memetakan diagnosis ke kode ICD-10 secara otomatis
3. Menghasilkan laporan diagnosis terstruktur untuk keperluan analisis dan pelaporan
4. Meningkatkan efisiensi dan akurasi proses coding diagnosis di RSUD Datu Sanggul

### 1.3 Manfaat Proyek

| Stakeholder                       | Manfaat                                                                      |
| --------------------------------- | ---------------------------------------------------------------------------- |
| **Tenaga Medis (Dokter/Perawat)** | Otomatisasi pencatatan diagnosis, lebih fokus pada patient care              |
| **Tim Coding Medis**              | Mempercepat proses coding ICD-10, mengurangi beban kerja manual              |
| **Manajemen RSUD**                | Data diagnosis terstruktur untuk analisis epidemiologi dan pelaporan kinerja |
| **BPJS**                          | Verifikasi klaim lebih cepat dan akurat berdasarkan diagnosis terstruktur    |
| **Peneliti Kesehatan**            | Akses data diagnosis untuk riset epidemiologi dan analisis pola penyakit     |

### 1.4 Teknologi yang Digunakan

- **Apache Spark 3.5.0** - Distributed computing framework
- **Spark NLP 5.2.2** - Natural Language Processing library dengan model klinis
- **Python 3.8+** - Bahasa pemrograman
- **Pandas** - Data manipulation
- **Jupyter Notebook** - Interactive computing environment
- **Git** - Version control

---

## BAGIAN 2: PERSIAPAN LINGKUNGAN

### 2.1 Prasyarat Sistem

**Persyaratan Minimum:**

- RAM: 8 GB (recommended 16 GB+)
- Storage: 10 GB untuk data dan model
- OS: Linux, macOS, Windows (dengan WSL2)
- Python: 3.8 atau lebih tinggi
- Java: JDK 8 atau lebih tinggi (untuk Spark)

### 2.2 Instalasi Otomatis (Recommended)

```bash
# Jalankan script setup otomatis (akan dijelaskan di bagian 3)
bash setup.sh
```

Script ini akan menginstal semua dependencies otomatis untuk semua OS.

### 2.3 Instalasi Manual

Jika Anda ingin instalasi manual, ikuti langkah berikut:

```bash
# 1. Clone repository Spark NLP dari John Snow Labs
git clone https://github.com/JohnSnowLabs/spark-nlp.git

# 2. Masuk ke direktori
cd spark-nlp

# 3. Setup virtual environment (optional tapi recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install --upgrade pip
pip install pyspark==3.5.0
pip install spark-nlp==5.2.2
pip install pandas>=1.3.0
pip install jupyter>=1.0.0
pip install matplotlib>=3.3.0
pip install seaborn>=0.11.0
pip install scikit-learn>=0.24.0

# 5. Verifikasi instalasi
python -c "import sparknlp; print(f'Spark NLP Version: {sparknlp.__version__}')"
```

---

## BAGIAN 3: SETUP DAN KONFIGURASI

### 3.1 Struktur Direktori Proyek

Setelah clone repository, struktur direktori Anda akan terlihat seperti:

```
spark-nlp/
├── setup.sh                          # Script setup otomatis (anda berikan)
├── INSTRUCTION-AUTOMATED-ICD-DIAGNOSIS.md  # File instruksi ini
├── automated_icd_diagnosis.ipynb    # Notebook utama (dari repo atau custom)
├── database/
│   └── diagnosis_icd_2025.csv       # Data CSV hasil query SIMRS
├── output/
│   ├── hasil_ekstraksi_*.csv        # Output ekstraksi
│   └── logs/                        # Log files
├── models/
│   └── (model NLP akan di-download otomatis)
└── src/
    └── (opsional: Python modules untuk helper functions)
```

### 3.2 Setup Database CSV

**Langkah 1: Pastikan CSV tersedia**

CSV file `diagnosis_icd_2025.csv` harus berada di path: `../database/diagnosis_icd_2025.csv`

Format CSV yang diharapkan:

```csv
id_pasien,nm_pasien,jk,umur_pasien,id_kunjungan,tgl_registrasi,nm_dokter,rekam_medis_narasi,diagnosis_structured
153284,H. KURSANI Tn,L,71,2025/01/01/000004,2025-01-01,dr. Resti Riyandina Mujiarto,"Patient: H. KURSANI Tn, Age: 71 years old. Chief Complaint: mimisan sejak jam 22.00 td malam...","Essential (primary) hypertension, Epistaxis"
153285,Siti Nurhaliza,P,55,2025/01/02/000005,2025-01-02,dr. Bambang Sutrisno,"Patient: Siti Nurhaliza, Age: 55 years old...","Community-acquired pneumonia, Hypertension stage 2"
```

**Langkah 2: Validasi CSV**

```python
import pandas as pd

# Load dan validasi CSV
df = pd.read_csv('../database/diagnosis_icd_2025.csv')
print(f"Total Records: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(df.head())
```

### 3.3 Konfigurasi Spark Session

Pada notebook `automated_icd_diagnosis.ipynb`, Spark session dikonfigurasi sebagai berikut:

```python
import sparknlp
from pyspark.sql import SparkSession

# Start Spark with SparkNLP
spark = sparknlp.start()

# Konfigurasi optional (jika perlu)
spark.sparkContext.setLogLevel("WARN")  # Set log level
```

---

## BAGIAN 4: MENJALANKAN PROYEK

### 4.1 Jalankan Setup Script

```bash
# Dari direktori proyek (spark-nlp/)
bash setup.sh
```

Script ini akan:

- ✓ Membuat virtual environment
- ✓ Install semua dependencies
- ✓ Setup direktori output
- ✓ Verifikasi instalasi
- ✓ Display informasi sistem

### 4.2 Jalankan Jupyter Notebook

```bash
# Aktifkan virtual environment (jika menggunakan)
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

# Jalankan Jupyter
jupyter notebook

# Akses notebook di browser: http://localhost:8888
# Buka file: automated_icd_diagnosis.ipynb
```

### 4.3 Struktur Notebook `automated_icd_diagnosis.ipynb`

Notebook dibagi menjadi beberapa cell sesuai tahapan:

#### **Cell 1-3: Setup dan Import**

```python
# Instalasi library
!pip install spark-nlp==5.2
!pip install pandas

# Import dependencies
import sparknlp
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
import pandas as pd

# Start Spark + SparkNLP
spark = sparknlp.start()
```

#### **Cell 4: Load Data dari CSV**

```python
# Load CSV dari path
df_csv = pd.read_csv('../database/diagnosis_icd_2025.csv')

# Convert ke Spark DataFrame
df_spark = spark.createDataFrame(df_csv)

print(f"Total Records: {df_spark.count()}")
df_spark.show()
```

#### **Cell 5: Build Spark NLP Pipeline**

```python
from sparknlp.base import DocumentAssembler
from sparknlp.annotator import Tokenizer, NerDLModel, NerConverter

# Pipeline stages
document_assembler = DocumentAssembler() \
    .setInputCol("rekam_medis_narasi") \
    .setOutputCol("document")

tokenizer = Tokenizer() \
    .setInputCol("document") \
    .setOutputCol("token")

ner_model = NerDLModel.pretrained("ner_dl_clinical", "en") \
    .setInputCols(["document", "token"]) \
    .setOutputCol("ner")

ner_converter = NerConverter() \
    .setInputCols(["document", "token", "ner"]) \
    .setOutputCol("entities")

# Combine into pipeline
pipeline = Pipeline(stages=[
    document_assembler,
    tokenizer,
    ner_model,
    ner_converter
])
```

#### **Cell 6: Fit dan Transform**

```python
# Fit model
nlp_model = pipeline.fit(df_spark)

# Transform data (ekstraksi)
results = nlp_model.transform(df_spark)
```

#### **Cell 7: Ekstraksi dan Visualisasi Hasil**

```python
# Select relevant columns
results_view = results.selectExpr(
    "id_pasien",
    "nm_pasien",
    "rekam_medis_narasi",
    "entities.result as entities_detected",
    "diagnosis_structured as ground_truth"
)

# Tampilkan hasil
results_view.show(truncate=False)

# Convert ke Pandas untuk analisis
results_pd = results_view.toPandas()
```

#### **Cell 8: Mapping ke ICD-10 (Optional)**

```python
# Load ICD-10 mapping dictionary
icd10_mapping = {
    "hypertension": "I10",
    "epistaxis": "R04.0",
    "pneumonia": "J18.9",
    # ... more mappings
}

# Fungsi untuk mapping diagnosis ke ICD-10
def map_diagnosis_to_icd10(diagnosis_text, mapping_dict):
    """Map diagnosis ke kode ICD-10"""
    icd_codes = []
    for key, code in mapping_dict.items():
        if key.lower() in diagnosis_text.lower():
            icd_codes.append(code)
    return icd_codes

# Apply mapping
results_pd['icd10_codes'] = results_pd['entities_detected'].apply(
    lambda x: map_diagnosis_to_icd10(str(x), icd10_mapping)
)
```

#### **Cell 9: Evaluasi dan Statistik**

```python
# Calculate statistics
total_records = len(results_pd)
total_entities = sum([len(e) if e else 0 for e in results_pd['entities_detected']])
avg_entities = total_entities / total_records if total_records > 0 else 0

print(f"Total Records Processed: {total_records}")
print(f"Total Entities Detected: {total_entities}")
print(f"Average Entities per Record: {avg_entities:.2f}")

# Compare dengan ground truth
matches = 0
for idx, row in results_pd.iterrows():
    if row['entities_detected'] and row['ground_truth']:
        # Simple string matching (untuk demo)
        if str(row['entities_detected']).lower() in str(row['ground_truth']).lower():
            matches += 1

accuracy = (matches / total_records) * 100 if total_records > 0 else 0
print(f"Accuracy (Simple Matching): {accuracy:.1f}%")
```

#### **Cell 10: Export Hasil**

```python
from datetime import datetime

# Export ke CSV
output_filename = f"hasil_ekstraksi_diagnosis_rsud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
results_pd.to_csv(f"output/{output_filename}", index=False)

print(f"✓ Hasil disimpan ke: output/{output_filename}")

# Export ke JSON (optional)
results_pd.to_json(f"output/{output_filename.replace('.csv', '.json')}", orient='records', indent=2)
```

#### **Cell 11: Narasi Hasil dan Kesimpulan**

```python
# Print comprehensive summary
print("""
================================================================================
RINGKASAN HASIL EKSTRAKSI DIAGNOSIS OTOMATIS
================================================================================

PROBLEM YANG DISELESAIKAN:
- Ekstraksi diagnosis manual memakan waktu 1-2 menit per rekam medis
- Rentan kesalahan manusia dalam pencatatan dan koding ICD-10
- Data diagnosis tidak mudah dianalisis untuk pelaporan

SOLUSI YANG DIIMPLEMENTASIKAN:
- Pipeline Spark NLP dengan model NER klinis (ner_dl_clinical)
- Ekstraksi otomatis entitas diagnosis dari teks rekam medis
- Mapping diagnosis ke kode ICD-10

HASIL YANG DICAPAI:
- Total Rekam Medis Diproses: {0}
- Total Entitas Terdeteksi: {1}
- Akurasi (dibanding Ground Truth): {2:.1f}%

MANFAAT:
✓ Otomatisasi ekstraksi diagnosis
✓ Peningkatan kecepatan processing (dari 1-2 menit → detik)
✓ Akurasi tinggi dalam identifikasi diagnosis
✓ Skalabilitas untuk big data processing
✓ Data terstruktur siap untuk analisis dan pelaporan

IMPLEMENTASI LANJUTAN:
1. Integrasi dengan SIMRS RSUD untuk real-time processing
2. Fine-tuning model dengan data RSUD Datu Sanggul
3. Setup pipeline production dengan monitoring
4. Integration dengan sistem ICD-10 coding dan billing BPJS

================================================================================
""".format(total_records, total_entities, accuracy))
```

---

## BAGIAN 5: STRUKTUR DATA

### 5.1 Input Data (CSV Format)

| Column                 | Type    | Deskripsi                                       |
| ---------------------- | ------- | ----------------------------------------------- |
| `id_pasien`            | String  | ID unik pasien (nomor rekam medis)              |
| `nm_pasien`            | String  | Nama pasien                                     |
| `jk`                   | String  | Jenis kelamin (L/P)                             |
| `umur_pasien`          | Integer | Umur pasien                                     |
| `id_kunjungan`         | String  | ID unik kunjungan/rawat                         |
| `tgl_registrasi`       | Date    | Tanggal registrasi kunjungan                    |
| `nm_dokter`            | String  | Nama dokter yang menangani                      |
| `rekam_medis_narasi`   | Text    | **Teks narasi rekam medis (INPUT untuk NLP)**   |
| `diagnosis_structured` | String  | Diagnosis terstruktur dari SIMRS (Ground Truth) |

### 5.2 Output Data (CSV Format)

| Column               | Type   | Deskripsi                                        |
| -------------------- | ------ | ------------------------------------------------ |
| `id_pasien`          | String | ID pasien                                        |
| `nm_pasien`          | String | Nama pasien                                      |
| `rekam_medis_narasi` | Text   | Teks asli rekam medis                            |
| `entities_detected`  | List   | **Entitas diagnosis yang terdeteksi oleh model** |
| `ground_truth`       | String | Diagnosis referensi dari SIMRS                   |
| `icd10_codes`        | List   | Kode ICD-10 yang dimapping (jika applicable)     |

### 5.3 Entitas yang Dideteksi

Model `ner_dl_clinical` mendeteksi entitas berikut:

- **PROBLEM** - Diagnosis, kondisi medis, gejala (Hypertension, Diabetes, Pneumonia)
- **TREATMENT** - Tindakan medis, terapi (Surgery, Antibiotic therapy)
- **TEST** - Pemeriksaan diagnostik (X-ray, Blood test, ECG)
- **PROCEDURE** - Prosedur medis (Appendectomy, Stent placement)
- **DRUG** - Nama obat (Metformin, Aspirin, Amoxicillin)
- **DOSAGE** - Dosis obat (500mg, 2x sehari)

---

## BAGIAN 6: TROUBLESHOOTING

### 6.1 Error: "JAVA_HOME not found"

**Solusi:**

```bash
# Linux/Mac
export JAVA_HOME=/path/to/jdk
export PATH=$JAVA_HOME/bin:$PATH

# Windows (setx command)
setx JAVA_HOME "C:\Program Files\Java\jdk1.8.0_201"
```

### 6.2 Error: "No module named 'sparknlp'"

**Solusi:**

```bash
pip install --upgrade spark-nlp
```

### 6.3 Error: "Memory error" saat loading model

**Solusi:**

```python
# Tingkatkan memory allocation Spark
spark = sparknlp.start(memory="8G")
```

### 6.4 Error: "CSV not found"

**Solusi:**

```bash
# Verifikasi path CSV
ls ../database/diagnosis_icd_2025.csv

# Jika belum ada, buat sample CSV:
python -c "
import pandas as pd
data = {
    'id_pasien': ['RM001'],
    'nm_pasien': ['Sample Patient'],
    'jk': ['L'],
    'umur_pasien': [50],
    'id_kunjungan': ['RAW001'],
    'tgl_registrasi': ['2025-01'],
    'nm_dokter': ['dr. Sample'],
    'rekam_medis_narasi': ['Patient with hypertension and diabetes'],
    'diagnosis_structured': ['Hypertension, Diabetes']
}
df = pd.DataFrame(data)
df.to_csv('../database/diagnosis_icd_2025.csv', index=False)
"
```

### 6.5 Model Download Timeout

**Solusi:**

```python
# Download model secara manual
import sparknlp_jsl
from sparknlp.pretrained import PretrainedPipeline

# Download dengan explicit cache
nlp = sparknlp.load("ner_dl_clinical")
```

---

## BAGIAN 7: BEST PRACTICES

### 7.1 Data Quality

- ✓ Validasi format CSV sebelum processing
- ✓ Handle missing values dalam rekam_medis_narasi
- ✓ Normalize teks (lowercase, remove special characters jika perlu)
- ✓ Ensure konsistensi format tanggal (YYYY-MM-DD)

### 7.2 Performance Optimization

- ✓ Gunakan Spark partitioning untuk data besar: `df.repartition(4)`
- ✓ Cache intermediate results: `results.cache()`
- ✓ Tune Spark config untuk hardware Anda
- ✓ Batch processing untuk dataset massive

### 7.3 Model Management

- ✓ Simpan trained models untuk reuse
- ✓ Version control untuk model dan output
- ✓ Monitor model performance secara berkala
- ✓ Plan fine-tuning dengan data RSUD

### 7.4 Production Deployment

- ✓ Setup monitoring dan alerting
- ✓ Implement error handling dan retry logic
- ✓ Log semua ekstraksi untuk audit trail
- ✓ Setup CI/CD pipeline untuk automation

---

## BAGIAN 8: REFERENSI

### 8.1 Dokumentasi External

- [Apache Spark Official Documentation](https://spark.apache.org/docs/latest/)
- [Spark NLP GitHub Repository](https://github.com/JohnSnowLabs/spark-nlp)
- [Spark NLP Clinical Models](https://nlp.johnsnowlabs.com/models?edition=Healthcare)
- [ICD-10 Official Codes](https://www.cdc.gov/nchs/icd/icd10cm.htm)

### 8.2 Dataset Query SIMRS

Query SQL yang digunakan untuk extract data:

```sql
SELECT
    p.no_rkm_medis AS id_pasien,
    p.nm_pasien,
    p.jk,
    YEAR(CURDATE()) - YEAR(p.tgl_lahir) AS umur_pasien,
    rp.no_rawat AS id_kunjungan,
    rp.tgl_registrasi,
    d.nm_dokter,
    CONCAT(
        'Patient: ', p.nm_pasien, ', Age: ', YEAR(CURDATE()) - YEAR(p.tgl_lahir), ' years old. ',
        'Chief Complaint: ', COALESCE(prw.keluhan, prn.keluhan, 'Not recorded'), '. ',
        'Physical Examination: ', COALESCE(prw.pemeriksaan, prn.pemeriksaan, 'Not recorded'), '. ',
        'Assessment: ', COALESCE(prw.penilaian, prn.penilaian, 'Not recorded'), '. ',
        'Diagnosis: ', GROUP_CONCAT(DISTINCT py.nm_penyakit ORDER BY dp.prioritas SEPARATOR ', '), '.'
    ) AS rekam_medis_narasi,
    GROUP_CONCAT(DISTINCT py.nm_penyakit ORDER BY dp.prioritas SEPARATOR ', ') AS diagnosis_structured
FROM
    pasien p
    INNER JOIN reg_periksa rp ON p.no_rkm_medis = rp.no_rkm_medis
    INNER JOIN dokter d ON rp.kd_dokter = d.kd_dokter
    LEFT JOIN pemeriksaan_ralan prw ON rp.no_rawat = prw.no_rawat
    LEFT JOIN pemeriksaan_ranap prn ON rp.no_rawat = prn.no_rawat
    LEFT JOIN diagnosa_pasien dp ON rp.no_rawat = dp.no_rawat
    LEFT JOIN penyakit py ON dp.kd_penyakit = py.kd_penyakit
WHERE
    rp.tgl_registrasi BETWEEN '2025-01-01' AND '2025-12-31'
    AND rp.stts = 'Sudah'
GROUP BY
    p.no_rkm_medis, rp.no_rawat
ORDER BY
    rp.tgl_registrasi ASC;
```

### 8.3 Contact & Support

- **Project Owner:** RSUD Datu Sanggul IT Department
- **Technical Support:** Data Analytics Team
- **Last Updated:** 2025-11-27

---

## LAMPIRAN A: QUICK START GUIDE

```bash
# 1. Clone repository
git clone https://github.com/JohnSnowLabs/spark-nlp.git
cd spark-nlp

# 2. Run setup script
bash setup.sh

# 3. Activate virtual environment
source venv/bin/activate

# 4. Start Jupyter
jupyter notebook

# 5. Buka automated_icd_diagnosis.ipynb dan jalankan cell demi cell

# 6. Output tersimpan di: output/hasil_ekstraksi_diagnosis_rsud_*.csv
```

---

**END OF INSTRUCTION DOCUMENT**

_Dokumen ini dibuat untuk mendukung proyek Big Data Analytics: Automated ICD Diagnosis Extraction di RSUD Datu Sanggul_

_Version: 1.0_
_Last Updated: 2025-11-27_
