# BIG DATA ANALYTICS: AUTOMATED ICD-10 DIAGNOSIS CODING

## RSUD Datu Sanggul, Kabupaten Tapin, Kalimantan Selatan

---

# SLIDE 1: COVER SLIDE

- **JUDUL**: Automated ICD-10 Diagnosis Coding Menggunakan Big Data Analytics & Machine Learning
- **INSTITUSI**: RSUD Datu Sanggul, Kabupaten Tapin, Kalimantan Selatan
- **PROGRAM**: Magister Teknik Informatika - Sains Data Profesional
- **TANGGAL**: Januari 2026
- **PRESENTER**: [Nama Mahasiswa]

---

# SLIDE 2: MASALAH & MOTIVASI

## Latar Belakang

| Aspek               | Data                                                             |
| ------------------- | ---------------------------------------------------------------- |
| **Volume Pasien**   | 10,000-12,000 pasien/bulan → 24,806 rekam medis (3 bulan)        |
| **Proses Manual**   | 1-2 menit per rekam = 150-300 jam per bulan                      |
| **Error Rate**      | 15-20% klaim BPJS ditolak                                        |
| **Delay Pelaporan** | 2-4 minggu ke Dinas Kesehatan                                    |
| **Dampak**          | Beban kerja tim coding overload, akurasi rendah, ROI BPJS hilang |

**Solusi**: Implementasi NLP + Machine Learning untuk otomatisasi kodefikasi diagnosis ICD-10

---

# SLIDE 3: S.M.A.R.T QUESTIONS (POIN 2)

## Kerangka Pertanyaan Bisnis

### Specific

Apakah implementasi NLP-based coding assistant dapat meningkatkan akurasi kode ICD dan mempercepat proses coding?

### Measurable

- Akurasi model vs ground truth: **≥85%**
- Waktu per berkas: **≤5 menit → <1 detik**
- Throughput: **2x lipat**

### Achievable

✓ Dataset: 24,806 rekam medis + 18,543 kode ICD
✓ Infrastructure: Apache Spark + NLP
✓ Data volume: Cukup untuk pilot 5,000-20,000 berkas

### Relevant

Reduce BPJS claim rejection rate: **15-20% → <5%**

### Time-bound

**Q1 2026**: 8-12 minggu pilot, akurasi ≥85%, time savings ≥30-40%

---

# SLIDE 4: DATA OVERVIEW (POIN 3)

## Data Loading & Validation

### Dataset 1: Rekam Medis Pasien (SIMRS)

- **Total Records**: 24,806 pasien
- **Periode**: 01 Januari - 05 September 2025
- **Fitur**: ID Pasien, Nama, Usia, JK, Dokter, Narasi Medis, Diagnosis
- **Missing Data**: 2,121 narasi, 2,123 diagnosis
- **Usia Range**: 0-2019 tahun (mean ≈ 43.99)
- **Gender**: L=11,326 (45.6%), P=13,480 (54.4%)

### Dataset 2: Katalog ICD-10 Resmi

- **Total Kode**: 18,543 kode ICD-10
- **Versi**: ICD-10 2010
- **Format**: CODE, DISPLAY, VERSION

**Status**: ✓ Data validation completed successfully

---

# SLIDE 5: NLP PIPELINE (POIN 4a)

## Clinical NER & Ground Truth Preparation

### Preprocessing

1. **Explode Diagnosis**: Multi-label diagnosis per record → **65,476** baris diagnosis tunggal
2. **Clinical NER**: Keyword-based entity extraction dari medical narrative
3. **Mapping Kategori Klinik**: 16 kelompok diagnosis klinis

### Ground Truth Validation Results

| Metrik                      | Hasil           |
| --------------------------- | --------------- |
| **Total Diagnosis Entries** | 65,476          |
| **Matched with NER**        | 11,107 (16.96%) |
| **Accuracy**                | **16.96%**      |

**Interpretasi:** Akurasi NER keyword-based masih rendah (16.96%) → cukup sebagai baseline, namun belum layak produksi.

---

# SLIDE 6: FEATURE ENGINEERING (POIN 4b)

## Fitur untuk ML Models

| No  | Fitur                | Tipe      | Penjelasan                                   |
| --- | -------------------- | --------- | -------------------------------------------- |
| 1   | **narrative_length** | Numerik   | Panjang narasi medis (karakter)              |
| 2   | **narrative_words**  | Numerik   | Jumlah kata dalam narasi                     |
| 3   | **num_diagnosis**    | Numerik   | Jumlah diagnosis per kunjungan               |
| 4   | **umur_pasien**      | Numerik   | Usia pasien (tahun)                          |
| 5   | **age_group**        | Kategorik | Infant, Child, Adult, Senior                 |
| 6   | **entity_count**     | Numerik   | Jumlah entitas klinis terdeteksi (NER)       |
| 7   | **is_valid_mapping** | Binary    | 1 jika NER match dengan diagnosis (match_gt) |
| 8   | **day_of_week**      | Kategorik | Hari registrasi (fitur temporal)             |

### Statistik Fitur Utama

- **Narrative Length**: mean ≈ 338.8 (min=125, max=2040)
- **Narrative Words**: mean ≈ 45.3 (min=17, max=295)
- **Num Diagnosis**: mean ≈ 3.61 (min=1, max=15)
- **Entity Count**: mean ≈ 2.32 (min=1, max=9)
- **Distribusi Label is_valid_mapping**: 1 = 11,107 (17%), 0 = 54,369 (83%) → **imbalanced**

---

# SLIDE 7: MODEL 1 - XGBOOST CLASSIFIER (POIN 4c)

## Prediksi Keberhasilan Matching NER vs Ground Truth (Binary Classification)

### Tujuan (Revisi)

Memprediksi **apakah hasil NER keyword-based akan match dengan diagnosis ground truth**, bukan langsung “valid ICD-10 mapping”.

### Arsitektur

- **Algoritma**: XGBoost Classifier
- **Training Data**: 52,224 baris (80%)
- **Test Data**: 13,252 baris (20%)
- **Features**: narrative_length, narrative_words, num_diagnosis, umur_pasien, entity_count

### Performance Metrics (Hasil Aktual Notebook)

| Metrik        | Nilai    |
| ------------- | -------- |
| **Accuracy**  | 83.08%   |
| **Precision** | 72.79%   |
| **Recall**    | 4.63%    |
| **F1-Score**  | 8.71%    |
| **AUC-ROC**   | 0.7525   |

**Confusion Matrix (kelas “Valid”):**
- True Positive (TP): 107
- False Negative (FN): 2,202

### Feature Importance (Gain-based)

1. **entity_count**: 0.7984 (≈79.84%)
2. **num_diagnosis**: 0.0701
3. **narrative_length**: 0.0469
4. **umur_pasien**: 0.0431
5. **narrative_words**: 0.0414

### Interpretasi Akademik

- Model memiliki **akurasi total tinggi (83%)**, tetapi **recall untuk kasus match (positif) sangat rendah (4.63%)** → banyak kasus match yang tidak terdeteksi.
- Dominasi fitur **entity_count** mengindikasikan adanya **kedekatan kuat antara fitur dan label** (potensi leakage konseptual).
- Cocok diposisikan sebagai **analisis baseline** NER matching, bukan model final untuk valid ICD-10 mapping.

### Use Case yang Masih Masuk Akal

✓ Analisis faktor apa yang mempengaruhi keberhasilan NER keyword-based.

---

# SLIDE 8: MODEL 2 - FACEBOOK PROPHET (POIN 4d)

## Trend Forecasting Beban Kerja Coding (Time Series)

### Tujuan

Memprediksi trend jumlah diagnosis per hari (total_diagnosis) untuk kebutuhan **resource planning**.

### Data Time Series

- **Horizon data**: 140 hari (01 Jan – 23 Mei 2025)
- Kolom agregat harian: `daily_visits`, `avg_diagnosis_per_visit`, `total_diagnosis`

### Arsitektur

- **Algoritma**: Facebook Prophet
- **Seasonality**: weekly_seasonality = True, yearly=False, daily=False
- **Target**: total_diagnosis per hari (kolom `y`)

### Performance Metrics (Hasil Aktual Notebook, dihitung di training window)

| Metrik        | Nilai            |
| ------------- | ---------------- |
| **RMSE**      | 884.99           |
| **MAE**       | 629.63           |
| **MAPE**      | 1044.85%         |
| **R-squared** | 0.3907           |

### Interpretasi Akademik

- **R² 0.39**: hanya ≈39% variasi data yang mampu dijelaskan model → performa lemah.
- **MAPE sangat besar (1044%)** karena ada hari dengan nilai diagnosis sangat kecil (membuat error persen meledak).
- Prophet dalam konfigurasi saat ini **belum layak dipromosikan sebagai “model unggulan”**. Perlu:
  - Evaluasi di test set terpisah (bukan hanya training window).
  - Perbaikan metrik (mis. SMAPE/MASE) dan penambahan regressor (`daily_visits`).

### Use Case

✓ **Exploratory forecasting** untuk melihat pola kasar trend dan seasonality, **bukan** sebagai angka pasti untuk keputusan SDM.

---

# SLIDE 9: MODEL 3 - RANDOM FOREST (POIN 4e)

## Prediksi Kategori Diagnosis (Multi-class Classification)

### Tujuan

Mengategorisasi diagnosis ke beberapa kategori klinis (multi-class) berdasarkan fitur jumlah diagnosis, panjang narasi, umur, dan entity_count.

> Catatan: Implementasi saat ini menghasilkan **3 kelas efektif** (konfirmasi dari confusion matrix 3×3), bukan 16 poli penuh.

### Arsitektur

- **Algoritma**: Random Forest Classifier (Spark ML)
- **Num Trees**: 50
- **Max Depth**: 10
- **Training Data**: 80%
- **Test Data**: 20%

### Performance Metrics (Hasil Aktual Notebook)

| Metrik                 | Nilai    |
| ---------------------- | -------- |
| **Accuracy**           | 84.57%   |
| **Weighted Precision** | 85.18%   |
| **Weighted Recall**    | 84.57%   |
| **Weighted F1-Score**  | 83.05%   |

### Feature Importance (Top 5)

1. **narrative_length**: 0.3499
2. **narrative_words**: 0.2457
3. **num_diagnosis**: 0.2085
4. **umur_pasien**: 0.1428
5. **entity_count**: 0.0531

### Interpretasi Akademik

- Performa multi-class cukup baik untuk pilot (Accuracy 84.57%, F1 83.05%).
- Model sensitif terhadap kompleksitas teks (narrative_length, narrative_words) dan jumlah diagnosis.
- Klaim “16 poliklinik” **belum didukung penuh oleh implementasi saat ini** → di presentasi sebaiknya disebut “multi-class kategori klinis (saat ini 3 kelas utama)”.

---

# SLIDE 10: MODEL COMPARISON & SELECTION (POIN 4f)

## Perbandingan 3 Model (Hasil Aktual)

| Aspek              | Model 1 (XGBoost)                 | Model 2 (Prophet)        | Model 3 (Random Forest)             |
| ------------------ | --------------------------------- | ------------------------ | ----------------------------------- |
| **Task**           | Binary Classification (NER match) | Time Series Regression   | Multi-class Classification          |
| **Primary Metric** | 83.08% Accuracy                   | R² = 0.3907              | **84.57% Accuracy**                 |
| **Secondary**      | AUC-ROC = 0.7525                  | RMSE = 884.99, MAPE>1000%| F1-Score (weighted) = **83.05%**   |
| **Kekuatan**       | Menangkap pola NER match          | Menangkap seasonality    | Kinerja stabil di multi-class       |
| **Kelemahan**      | Recall positif sangat rendah      | Error sangat besar       | Saat ini baru mencakup 3 kelas      |

### Kesimpulan Teknis

- **Model 3 (Random Forest)** adalah kandidat utama untuk **kategorisasi diagnosis multi-class**.
- **Model 1 (XGBoost)** bermanfaat untuk **analisis keberhasilan NER match**, bukan final ICD-10 validator.
- **Model 2 (Prophet)** masih perlu **revisi lebih lanjut** sebelum dipakai sebagai dasar keputusan operasional.

---

# SLIDE 11: DASHBOARD VISUALIZATION (POIN 5)

## Elemen Dashboard yang Direkomendasikan

1. **Model Performance Comparison (Bar Chart)**
   - Akurasi Model 1, Model 3
   - R² Model 2 (ditandai dengan catatan “underperforming”)

2. **Confusion Matrix & Class Metrics**
   - Confusion matrix Model 3 (3 kelas) untuk melihat pola salah klasifikasi

3. **Feature Importance**
   - Horizontal bar untuk 5 fitur teratas Model 1 dan Model 3

4. **Diagnosis Category Distribution**
   - Distribusi jumlah diagnosis per kategori (IGD, OTHER, dll.)

5. **NLP Validation Summary**
   - Pie chart: Matched (16.96%) vs Not Matched (83.04%)

6. **Time Series Overview**
   - Plot actual vs forecast Prophet sebagai insight eksplorasi (dengan label “model masih perlu penyempurnaan”).

---

# SLIDE 12: BUSINESS RECOMMENDATIONS (POIN 6)

## Perbaikan & Pengembangan Lanjutan

### 1. Peningkatan NLP (NER)

- Beralih dari keyword-based ke **pretrained clinical transformers** (BioBERT, ClinicalBERT).
- Target peningkatan akurasi NER dari 16.96% → 50-60%+.

### 2. Re-definisi Label Model 1

- Ganti target dari `match_with_gt` menjadi indikator validitas mapping terhadap katalog ICD-10 resmi.
- Hal ini mengurangi risiko **circularity** dan meningkatkan relevansi model terhadap kebutuhan coding ICD.

### 3. Penyempurnaan Time Series Model

- Evaluasi Prophet pada **test set terpisah** dan gunakan metrik yang lebih stabil (SMAPE, MASE).
- Masukkan `daily_visits` sebagai regressor tambahan.

### 4. Ekspansi Kategori Model 3

- Lengkapi mapping sehingga benar-benar mencakup **16 poliklinik** sesuai domain RSUD.
- Terapkan teknik handling imbalanced (class weights, oversampling) jika distribusi sangat timpang.

---

# SLIDE 13: NARASI UNTUK PRESENTASI

## Poin Penting yang Perlu Ditekankan di Slide

1. **Pipeline Lengkap**
   - Mulai dari data SIMRS mentah → eksplorasi → NLP → feature engineering → 3 model → evaluasi bisnis.

2. **Kejujuran Akademik**
   - Disampaikan apa adanya bahwa: 
     - NER baseline masih 16.96%.
     - Model 2 (Prophet) belum memuaskan dan dianggap sebagai eksperimen awal.

3. **Kekuatan Utama**
   - Model 3 (Random Forest) sudah menunjukkan kinerja multi-class yang baik (84.57% akurasi, F1 83.05%).
   - Model 1 menunjukkan bahwa fitur entity_count sangat berpengaruh terhadap keberhasilan NER.

4. **Rencana Pengembangan**
   - Jelaskan bahwa target jangka panjang adalah **ICD-10 auto-coding penuh** dengan NER berbasis deep learning dan time series yang lebih stabil.

---

# SLIDE 14: CLOSING & Q&A

- Ringkas kembali: 
  - Dataset besar (24,806 rekam medis, 65,476 diagnosis single, 18,543 kode ICD)
  - 3 model machine learning dengan metrik aktual yang realistis
  - Insight penting untuk pengembangan SIMRS dan coding ICD otomatis
- Tutup dengan **ajakan diskusi**: apa prioritas manajemen—peningkatan akurasi NER, forecasting beban kerja, atau routing diagnosis?

---

**Catatan:**
- Semua angka metrik di atas sudah disesuaikan dengan **output terbaru notebook `enhanced_analysis_diagnosis_icd_based.ipynb`**.
- Beberapa framing diubah agar **sesuai secara akademik** (misalnya: Model 1 = prediksi NER match, Prophet = exploratory, Model 3 = multi-class 3 kelas saat ini).
