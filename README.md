# Tugas Big Data Analytics - Ekstraksi Diagnosis Otomatis dari Catatan Medis Pasien

## RSUD Datu Sanggul

---

## 1. Problem Statement

### Latar Belakang

Rumah Sakit Umum Daerah (RSUD) Datu Sanggul melayani ribuan pasien setiap hari. Setiap pasien memiliki catatan medis yang berisi informasi diagnosis dalam bentuk teks narasi tidak terstruktur. Data yang tidak terstruktur ini menyulitkan proses analisis dan pelaporan diagnosis secara cepat dan akurat.

### Identifikasi Masalah

- Ekstraksi diagnosis dilakukan secara manual yang memakan banyak waktu dan tenaga (1-2 menit/rekam medis).
- Rentan terjadi kesalahan manusia dalam pencatatan diagnosis dan koding ICD-10.
- Data diagnosis tidak mudah dianalisis untuk keperluan manajemen rumah sakit dan pelaporan kepada BPJS.
- Verifikasi klaim BPJS menjadi lambat akibat data diagnosis tidak terstruktur (15-20% klaim ditolak).
- Skala data besar (10,000-12,000 pasien/bulan) membuat proses manual tidak efisien dan tidak scalable.

| SMART      | Rumusan untuk kasus "Automated ICD coding pada SIMRS"                                                                                                                                                                       |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Specific   | "Apakah implementasi coding assistant berbasis Spark NLP pada dokumen rekam medis (narasi klinis) dapat meningkatkan akurasi kode ICD dan mempercepat proses coding di unit rekam medis?" jmir+1​                           |
| Measurable | "Berapa perubahan (i) akurasi/tingkat kesesuaian kode ICD model vs ground truth coder, (ii) median turnaround time coding per berkas, dan (iii) throughput berkas per coder per hari sebelum vs sesudah asisten NLP?" jmir​ |
| Achievable | "Dengan data historis SIMRS dan infrastruktur Spark yang tersedia, dapatkah dilakukan pilot yang memproses minimal N berkas (mis. 5.000–20.000) untuk menghitung metrik akurasi dan waktu secara objektif?" atlassian​      |
| Relevant   | "Apakah peningkatan akurasi dan penurunan waktu coding tersebut cukup relevan untuk menurunkan beban kerja coder dan mendukung kualitas proses administrasi/claim (melalui coding yang lebih konsisten)?" jmir+1​           |
| Time-bound | "Dalam periode pilot selama 8–12 minggu (mis. Q1 2026), apakah sistem mencapai target: penurunan median waktu coding ≥ X% dan peningkatan agreement ICD ≥ Y% dibanding baseline?" samhsa+1​                                 |

---

## 2. Tujuan

Mengembangkan solusi otomatis untuk mengekstraksi diagnosis utama dan sekunder dari catatan teks rekam medis pasien di RSUD Datu Sanggul menggunakan SparkNLP. Sistem ini bertujuan untuk mengubah data diagnosis yang tersimpan dalam bentuk teks tidak terstruktur menjadi data terstruktur yang mudah dianalisis dan dilaporkan.

Dengan solusi ini, proses pencatatan, analisis, dan pelaporan diagnosis menjadi lebih cepat, akurat, dan efisien, mendukung pengambilan keputusan klinis dan manajerial. Proyek ini menargetkan pemrosesan 24.806 rekam medis dalam waktu singkat (dalam detik) sebagai proof-of-concept untuk skala lebih besar (100K+ rekam medis/bulan).

---

## 3. Manfaat

- **Efisiensi kerja tenaga medis dan coding medis**: Mengurangi waktu yang dibutuhkan untuk mengekstrak diagnosis dari catatan medis secara manual (dari 1-2 menit/rekam menjadi detik).
- **Akurasi data diagnosis**: Meminimalkan kesalahan akibat human error dalam pencatatan diagnosis dan koding ICD-10.
- **Kemudahan analisis dan pelaporan**: Data diagnosis terstruktur memudahkan analisis epidemiologi, pelaporan kepada BPJS, serta perencanaan kebutuhan fasilitas dan SDM medis.
- **Pengambilan Dukungan Keputusan**: Data diagnosis yang terstruktur membantu manajemen RSUD dalam mengambil keputusan berbasis data terkait alokasi sumber daya dan peningkatan kualitas layanan kesehatan.
- **Optimasi klaim BPJS**: Meningkatkan akurasi dan kecepatan verifikasi klaim BPJS (target: peningkatan approval rate dari 80% menjadi >95%).
- **Real-time analytics**: Memungkinkan pelaporan real-time ke Dinas Kesehatan (dari 2-4 minggu menjadi real-time).

---

## 4. Pengguna Solusi

- **Dokter dan Perawat**: Memperoleh catatan diagnosis yang lebih lengkap dan terstruktur, membantu proses pelayanan pasien.
- **Tenaga Coding Medis**: Membantu dalam proses coding diagnosis menjadi kode ICD-10 secara otomatis sehingga mempercepat proses administrasi.
- **Manajemen Rumah Sakit**: Memiliki data diagnosis yang terstruktur dan siap pakai untuk kebutuhan pelaporan dan evaluasi kinerja RSUD.
- **Pengelola BPJS**: Mendapatkan data klaim diagnosis yang akurat dan lengkap untuk proses verifikasi klaim.
- **Peneliti Kesehatan dan Epidemiologi**: Memiliki akses ke data diagnosis yang bisa dianalisis untuk penelitian dan pengembangan layanan kesehatan.
- **Dinas Kesehatan**: Mendapatkan laporan real-time tentang pola penyakit di wilayah Tapin, Kalimantan Selatan.

---

## 5. Data Sintesis dan Sumber

Data yang digunakan merupakan hasil sintesis dari query Sistem Informasi Manajemen Rumah Sakit (SIMRS) RSUD Datu Sanggul. Data ini berupa catatan rekam medis pasien dalam format teks narasi klinis yang menggambarkan kondisi dan diagnosis pasien secara ringkas.

Dataset ini mencakup **24,806 rekam medis** dengan periode data dari **01 Januari - 05 September 2025**, mencakup 17 poliklinik spesialisasi RSUD Datu Sanggul. Dataset juga mencakup katalog resmi **18,543 kode ICD-10** versi 2010 untuk mapping diagnosis.

Data sintesis ini dibuat untuk mewakili kondisi nyata data rekam medis RSUD Datu Sanggul sehingga aplikasi ekstraksi diagnosis otomatis menggunakan SparkNLP dapat diuji coba dan dievaluasi dengan representasi data yang sesuai dunia nyata.

Contoh query yang digunakan untuk menarik data rekam medis dari SIMRS melibatkan tabel `rekam_medis`, `kunjungan`, dan `pasien` agar diperoleh informasi lengkap mengenai tanggal kunjungan dan narasi diagnosis pasien.

| Nama Tabel  | Keterangan                                           |
| ----------- | ---------------------------------------------------- |
| pasien      | Data identitas pasien                                |
| kunjungan   | Data rekam kunjungan pasien                          |
| rekam_medis | Catatan medis rekam medis (narasi klinis, diagnosis) |
| diagnosis   | Data diagnosis yang sudah terstruktur dan coding ICD |
| dokter      | Data dokter yang menangani                           |

Untuk referensi dataset serupa dan latihan, dapat digunakan dataset MIMIC-III, i2b2, atau dataset sintetik dari Synthea yang menyediakan gambaran data serupa walaupun dalam skala lebih besar dan format yang berbeda.

## Query Pengambilan Data Rekam Medis Tahun 2025

Query berikut digunakan untuk mengambil data rekam medis, tanggal kunjungan, dan narasi diagnosis dari pasien yang datang pada rentang tanggal **1 Januari 2025 hingga 31 Desember 2025**. Hasil dibatasi sebanyak **50 data** pertama.

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

```
┌──────────────────┐
│     pasien       │
│ (ID, nama, umur) │
└────────┬─────────┘
         │
         │ no_rkm_medis
         ↓
┌──────────────────────────┐
│     reg_periksa          │
│ (no_rawat, tgl_registrasi)
│  ├─ kd_dokter → dokter   │
│  └─ status               │
└────────┬────────┬────────┘
         │        │
         │        └─ no_rawat
         │           ↓
         │     ┌─────────────────────┐
         │     │ pemeriksaan_ralan   │
         │     │ (keluhan,           │
         │     │  pemeriksaan,       │
         │     │  penilaian)         │
         │     └─────────────────────┘
         │
         └─ no_rawat
            ↓
     ┌──────────────────────┐
     │ diagnosa_pasien      │
     │ (kd_penyakit,        │
     │  prioritas, status)  │
     └──────────┬───────────┘
                │
                └─ kd_penyakit
                   ↓
            ┌──────────────────┐
            │    penyakit      │
            │ (nm_penyakit)    │
            └──────────┘
```

---

## 6. Scope dan Batasan

- **Scope:**
  Ekstraksi diagnosis utama dan sekunder dari 24.806 catatan medis pasien hasil query data SIMRS, mencakup 17 poliklinik spesialisasi RSUD Datu Sanggul, dengan fokus pada mapping ke 18.543 kode ICD-10.
- **Batasan:**
  - Data teks berupa bahasa Indonesia yang disintesis menggunakan istilah standar medis.
  - Fokus pada entitas diagnosis (PROBLEM), tidak termasuk obat/tindakan (akan dikembangkan di fase selanjutnya).
  - Menggunakan model pre-trained NER klinis SparkNLP yang tersedia untuk bahasa Inggris, dengan adaptasi yang diperlukan untuk data sintesis.
- **Catatan:** Untuk penggunaan skala besar dan bahasa lokal, diperlukan pelatihan dan penyesuaian model lebih lanjut (fine-tuning dengan data lokal).

---

## 7. Teknologi yang Digunakan

- **Apache Spark 3.5.0** - Distributed computing framework
- **Spark NLP 5.2.2** - Natural Language Processing library dengan model klinis
- **Python 3.8+** - Bahasa pemrograman utama
- **Pandas** - Data manipulation
- **Jupyter Notebook** - Interactive computing environment
- **Git** - Version control
- **Docker** - Containerization untuk deployment
- **Streamlit** - Dashboard interaktif untuk visualisasi
- **XGBoost** - Model machine learning untuk klasifikasi
- **Facebook Prophet** - Model forecasting untuk prediksi beban kerja
- **Random Forest** - Model machine learning untuk klasifikasi multi-class

---

## 8. Cara Menjalankan Proyek

### Persyaratan Sistem

- RAM: 8 GB (disarankan 16 GB+)
- Storage: 10 GB untuk data dan model
- OS: Linux, macOS, Windows (dengan WSL2)
- Python: 3.8 atau lebih tinggi
- Java: JDK 1+ (untuk Apache Spark)

### Instalasi Otomatis (Disarankan)

```bash
# Jalankan script setup otomatis
bash setup.sh
```

### Instalasi Manual

```bash
# 1. Clone repository
git clone https://github.com/JohnSnowLabs/spark-nlp.git
cd spark-nlp

# 2. Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Jalankan notebook
jupyter lab
```

### Jalankan dengan Docker

```bash
# Bangun dan jalankan service
docker-compose up -d

# Akses Jupyter di http://localhost:8888
# Akses Spark UI di http://localhost:4040
# Akses Streamlit dashboard di http://localhost:8501
```

### Jalankan dengan Makefile (opsional)

```bash
# Setup environment
make setup

# Jalankan Jupyter
make jupyter

# Atau jalankan notebook secara otomatis
make run
```

---

## 9. Struktur Proyek

```
Automatic-ICD-Based-Diagnosis-NLP-Spark/
├── app.py                           # Dashboard Streamlit utama
├── automated_icd_diagnosis.ipynb    # Notebook utama analisis
├── enhanced_analysis_diagnosis_icd_based.ipynb # Notebook analisis lanjutan
├── requirements.txt                 # Dependencies Python
├── setup.sh                         # Script setup otomatis
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker compose configuration
├── Makefile                         # Task automation
├── README.md                        # Dokumentasi ini
├── INSTRUCTION-AUTOMATED-ICD-DIAGNOSIS.md  # Dokumentasi teknis
├── .env                             # Environment variables
├── .gitignore                       # Files to ignore in Git
├── .venv/                           # Virtual environment
│   └── README.md                    # Informasi tentang virtual environment
├── app/
│   ├── dashboard.py                 # Dashboard Streamlit
│   └── readme.md                    # Dokumentasi dashboard
├── config/
│   ├── venv_config.py               # Konfigurasi virtual environment
│   └── README.md                    # Dokumentasi konfigurasi
├── database/
│   ├── diagnosis_icd_2025.csv       # Data CSV hasil query SIMRS
│   └── export/                      # Hasil ekspor analisis
│       ├── evaluation_report.md     # Laporan evaluasi model
│       └── icd_diagnosis_extraction_modelhub_*.zip  # Package model hub
├── docs/
│   ├── dashboard_design.md          # Desain dashboard
│   ├── hasil_analisis_icd_ppt.md    # Hasil analisis untuk presentasi
│   └── INSTRUCTION-AUTOMATED-ICD-DIAGNOSIS.md  # Dokumentasi teknis
├── image/                           # Gambar-gambar untuk dokumentasi
│   ├── ICD - WHO.jpg                # Gambar ICD WHO
│   ├── ICD10.jpg                    # Gambar ICD-10
│   ├── NLP 2.jpg                    # Gambar NLP
│   ├── NLP.jpg                      # Gambar NLP
│   ├── RSUD.jpg                     # Gambar RSUD
│   └── generated-image.png          # Gambar hasil generasi
├── notebooks/                       # Notebook tambahan
│   └── automated_diagnosis_icd.ipynb  # Notebook utama
├── output/                          # Output hasil ekstraksi
│   ├── hasil_ekstraksi_*.csv        # Output ekstraksi
│   └── logs/                        # Log files
├── scripts/                         # Script tambahan
│   ├── start_jupyter.sh             # Script start Jupyter Linux/Mac
│   └── start_jupyter.bat            # Script start Jupyter Windows
├── spark-nlp/                       # Repository Spark NLP (jika di-clone)
├── test/                            # File-file pengujian
├── models/                          # Model NLP (akan di-download otomatis)
└── src/                             # Source code tambahan
    └── __init__.py                  # Python package
```

---

## 10. Penggunaan

### Notebook Utama: `automated_diagnosis_icd.ipynb`

1. Pastikan data CSV `diagnosis_icd_2025.csv` tersedia di direktori `database/`
2. Jalankan notebook `notebooks/automated_diagnosis_icd.ipynb` atau `automated_icd_diagnosis.ipynb`
3. Ikuti langkah-langkah dalam notebook untuk:
   - Load data dari CSV
   - Build pipeline NLP menggunakan Spark NLP
   - Ekstraksi entitas diagnosis (NER)
   - Mapping hasil ekstraksi ke kode ICD-10
   - Evaluasi hasil ekstraksi
   - Export hasil ke CSV/JSON

### Dashboard Streamlit: `app.py`

1. Jalankan `streamlit run app.py` untuk memulai dashboard
2. Dashboard menyediakan visualisasi hasil analisis dari 3 model ML:
   - XGBoost Classifier (Binary Classification)
   - Facebook Prophet (Time Series Forecasting)
   - Random Forest Classifier (Multi-class Classification)

### Hasil Analisis

Dari dataset 24.806 rekam medis, proyek ini berhasil:

- Mengekstraksi **96,979 entitas diagnosis** dengan rata-rata 3.91 entitas per rekam medis
- Mencapai **akurasi matching sederhana 57.67%** antara hasil NER dan ground truth
- Menyediakan **mapping ke 150+ kode ICD-10** untuk 17 poliklinik RSUD Datu Sanggul

---

## 11. Hasil dan Evaluasi

Proyek ini menghasilkan 3 model machine learning utama dengan hasil sebagai berikut:

### Model 1: XGBoost Classifier (Binary Classification - NER Matching Prediction)

- **Akurasi**: 83.08%
- **Presisi**: 72.79%
- **Recall**: 4.63%
- **F1-Score**: 8.71%
- **AUC-ROC**: 0.7525
- **Confusion Matrix**: TP=107, FP=40, TN=10,903, FN=2,202

### Model 2: Facebook Prophet (Time Series Forecasting - Workload Planning)

- **RMSE**: 884.99
- **MAE**: 629.63
- **MAPE**: 1044.85%
- **R²**: 0.3907
- **Trend Slope**: 238.08

### Model 3: Random Forest Classifier (Multi-class Classification - 16 Diagnosis Categories)

- **Akurasi**: 84.57%
- **Weighted Presisi**: 85.18%
- **Weighted Recall**: 84.57%
- **Weighted F1-Score**: 83.05%

Proyek ini menghasilkan:

- Data diagnosis terstruktur dari teks narasi medis
- Mapping diagnosis ke kode ICD-10 (150+ kode untuk 17 poliklinik)
- Statistik akurasi ekstraksi
- File output dalam format CSV dan JSON
- Dashboard interaktif untuk visualisasi hasil

---

## 12. Pengaturan Lingkungan Virtual (.venv)

Proyek ini menggunakan virtual environment untuk mengelola dependensi Python. Ikuti langkah-langkah berikut untuk mengatur lingkungan:

### Persyaratan Awal

- Python 3.8 atau lebih tinggi
- Git
- Java JDK 11+ (untuk Apache Spark)

### Setup Virtual Environment

#### Metode Otomatis (Disarankan)

Jalankan skrip setup otomatis dari root direktori proyek (jika menggunakan WSL di Windows, pastikan menggunakan Git Bash atau PowerShell):

```bash
# Untuk Linux/Mac
./setup.sh

# Untuk Windows (gunakan Git Bash atau Command Prompt)
bash setup.sh
```

#### Metode Manual

1. Buat virtual environment dari root direktori proyek (jika tidak menggunakan skrip setup.sh):

   ```bash
   python -m venv ".venv"
   ```

2. Aktifkan virtual environment (dari root direktori proyek):

   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```
   - Windows (Git Bash):
     ```bash
     source .venv/Scripts/activate
     ```
   - Windows (Command Prompt):
     ```cmd
     .venv\Scripts\activate
     ```

3. Instal dependensi dari root direktori proyek:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

#### Metode Alternatif (Menggunakan Skrip Terpisah)

Fungsionalitas instalasi dependensi sekarang sudah diintegrasikan ke dalam setup.sh. Untuk Windows, Anda juga dapat menggunakan skrip terpisah di `scripts/start_jupyter.bat` atau `scripts/start_jupyter.sh` untuk menjalankan Jupyter Lab di lingkungan virtual yang sudah diaktifkan.

### Struktur Virtual Environment

Virtual environment disimpan di folder `.venv` di root proyek. Meskipun sebagian besar konten virtual environment diabaikan oleh Git, folder ini tetap ditampilkan di struktur proyek karena keberadaan file .gitkeep dan README.md untuk dokumentasi. File `config/venv_config.py` menyediakan informasi dan utilitas untuk mengelola virtual environment secara programatik.

### Menampilkan Folder .venv di VSCode

Jika folder `.venv` tidak terlihat di Explorer VSCode, Anda dapat mengikuti langkah-langkah berikut untuk menampilkannya (konfigurasi ini sudah disertakan dalam setup otomatis di file `.vscode/settings.json` yang dibuat oleh skrip setup.sh):

1. Buka VSCode
2. Buka Settings (File > Preferences > Settings atau tekan `Ctrl+,`)
3. Cari "files.exclude"
4. Pastikan entri berikut ada dan bernilai false:
   - `**/.venv`: false
   - `**/venv`: false
   - `**/env`: false
   - `**/.env`: false

Atau, Anda bisa menambahkan konfigurasi berikut ke file `.vscode/settings.json` di proyek Anda (sudah disediakan dalam konfigurasi otomatis):

```json
{
  "files.exclude": {
    "**/.venv": false,
    "**/venv": false,
    "**/env": false,
    "**/.env": false
  }
}
```

---

## 13. Dashboard Interaktif

Proyek ini menyertakan dashboard Streamlit interaktif yang dapat diakses dengan perintah `streamlit run app.py`. Dashboard menyediakan visualisasi komprehensif dari hasil analisis 3 model ML, termasuk metrik kinerja, confusion matrix, feature importance, serta rekomendasi bisnis berdasarkan hasil analisis data. Dashboard juga menyediakan informasi ROI dan business case untuk implementasi solusi di RSUD Datu Sanggul.
