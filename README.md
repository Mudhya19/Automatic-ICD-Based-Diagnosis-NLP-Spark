# Tugas Big Data Analytics - Ekstraksi Diagnosis Otomatis dari Catatan Medis Pasien

## RSUD Datu Sanggul

---

## 1. Problem Statement

### Latar Belakang

Rumah Sakit Umum Daerah (RSUD) Datu Sanggul melayani ribuan pasien setiap hari. Setiap pasien memiliki catatan medis yang berisi informasi diagnosis dalam bentuk teks narasi tidak terstruktur. Data yang tidak terstruktur ini menyulitkan proses analisis dan pelaporan diagnosis secara cepat dan akurat.

### Identifikasi Masalah

- Ekstraksi diagnosis dilakukan secara manual yang memakan banyak waktu dan tenaga.
- Rentan terjadi kesalahan manusia dalam pencatatan diagnosis.
- Data diagnosis tidak mudah dianalisis untuk keperluan manajemen rumah sakit dan pelaporan kepada BPJS.
- Verifikasi klaim BPJS menjadi lambat akibat data diagnosis tidak terstruktur.
---

## 2. Tujuan

Mengembangkan solusi otomatis untuk mengekstraksi diagnosis utama dan sekunder dari catatan teks rekam medis pasien di RSUD Datu Sanggul menggunakan SparkNLP. Sistem ini bertujuan untuk mengubah data diagnosis yang tersimpan dalam bentuk teks tidak terstruktur menjadi data terstruktur yang mudah dianalisis dan dilaporkan.

Dengan solusi ini, proses pencatatan, analisis, dan pelaporan diagnosis menjadi lebih cepat, akurat, dan efisien, mendukung pengambilan keputusan klinis dan manajerial.

---

## 3. Manfaat

- **Efisiensi kerja tenaga medis dan coding medis :** Mengurangi waktu yang dibutuhkan untuk mengekstrak diagnosis dari catatan medis dengan cara manual.
- **Akurasi data diagnosis :** Meminimalkan kesalahan akibat human error dalam pencatatan diagnosis.
- **Kemudahan analisis dan pelaporan :** Data diagnosis terstruktur memudahkan analisis epidemiologi, pelaporan kepada BPJS, serta perencanaan kebutuhan fasilitas dan SDM medis.
- **Pengambilan Dukungan Keputusan :** Data diagnosis yang terstruktur membantu manajemen RSUD dalam mengambil keputusan berbasis data terkait alokasi sumber daya dan peningkatan kualitas layanan kesehatan.

---

## 4. Pengguna Solusi

- **Dokter dan Perawat:** Memperoleh catatan diagnosis yang lebih lengkap dan terstruktur, membantu proses pelayanan pasien.
- **Tenaga Coding Medis:** Membantu dalam proses coding diagnosis menjadi kode ICD-10 secara otomatis sehingga mempercepat proses administrasi.
- **Manajemen Rumah Sakit:** Memiliki data diagnosis yang terstruktur dan siap pakai untuk kebutuhan pelaporan dan evaluasi kinerja RSUD.
- **Pengelola BPJS:** Mendapatkan data klaim diagnosis yang akurat dan lengkap untuk proses verifikasi klaim.
- **Peneliti Kesehatan dan Epidemiologi:** Memiliki akses ke data diagnosis yang bisa dianalisis untuk penelitian dan pengembangan layanan kesehatan.

---

## 5. Data Sintesis dan Sumber

Data yang digunakan merupakan hasil sintesis dari query Sistem Informasi Manajemen Rumah Sakit (SIMRS) RSUD Datu Sanggul. Data ini berupa catatan rekam medis pasien dalam format teks narasi klinis yang menggambarkan kondisi dan diagnosis pasien secara ringkas.

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
            └──────────────────┘
```

---

## 6. Scope dan Batasan

- **Scope:**  
  Ekstraksi diagnosis utama dan sekunder dari 10-50 catatan medis pasien hasil query data SIMRS.
- **Batasan:**
  - Data teks berupa bahasa Indonesia yang disintesis menggunakan istilah standar medis.
  - Fokus pada entitas diagnosis (PROBLEM), tidak termasuk obat/tindakan.
  - Menggunakan model pre-trained NER klinis SparkNLP yang tersedia untuk bahasa Inggris, dengan adaptasi yang diperlukan untuk data sintesis.
- **Catatan:** Untuk penggunaan skala besar dan bahasa lokal, diperlukan pelatihan dan penyesuaian model lebih lanjut.

---

## 7. Teknologi yang Digunakan

- **Apache Spark 3.5.0** - Distributed computing framework
- **Spark NLP 5.2.2** - Natural Language Processing library dengan model klinis
- **Python 3.8+** - Bahasa pemrograman
- **Pandas** - Data manipulation
- **Jupyter Notebook** - Interactive computing environment
- **Git** - Version control

---

## 8. Cara Menjalankan Proyek

### Persyaratan Sistem

- RAM: 8 GB (disarankan 16 GB+)
- Storage: 10 GB untuk data dan model
- OS: Linux, macOS, Windows (dengan WSL2)
- Python: 3.8 atau lebih tinggi
- Java: JDK 8 atau lebih tinggi (untuk Spark)

### Instalasi Otomatis (Disarankan)

```bash
# Jalankan script setup otomatis
bash scripts/setup.sh
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
jupyter notebook
```

### Jalankan dengan Docker

```bash
# Bangun dan jalankan service
docker-compose up -d

# Akses Jupyter di http://localhost:8888
```

---

## 9. Struktur Proyek

```
Automatic-ICD-Based-Diagnosis-NLP-Spark/
├── automated_icd_diagnosis.ipynb    # Notebook utama
├── requirements.txt                  # Dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker compose configuration
├── Makefile                        # Task automation
├── README.md                       # Dokumentasi ini
├── INSTRUCTION-AUTOMATED-ICD-DIAGNOSIS.md  # Dokumentasi teknis
├── .env                            # Environment variables
├── .gitignore                      # Files to ignore in Git
├── database/
│   └── diagnosis_icd_2025.csv      # Data CSV hasil query SIMRS
├── output/
│   ├── hasil_ekstraksi_*.csv       # Output ekstraksi
│   └── logs/                       # Log files
├── models/
│   └── (model NLP akan di-download otomatis)
├── notebooks/
│   └── example.py                  # Contoh script
├── docs/
│   └── INSTRUCTION-AUTOMATED-ICD-DIAGNOSIS.md  # Dokumentasi teknis
├── scripts/                        # Script tambahan
│   └── setup.sh                    # Script setup otomatis
├── image/                          # Gambar-gambar untuk dokumentasi
├── test/                           # File-file pengujian
├── config/                         # File-file konfigurasi
└── src/
    └── __init__.py                 # Python package
```

---

## 10. Penggunaan

1. Pastikan data CSV `diagnosis_icd_2025.csv` tersedia di direktori `database/`
2. Jalankan notebook `automated_icd_diagnosis.ipynb`
3. Ikuti langkah-langkah dalam notebook untuk:
   - Load data
   - Build pipeline NLP
   - Ekstraksi diagnosis
   - Mapping ke ICD-10
   - Evaluasi hasil
   - Export hasil

---

## 11. Hasil dan Evaluasi

Proyek ini menghasilkan:

- Data diagnosis terstruktur dari teks narasi medis
- Mapping diagnosis ke kode ICD-10
- Statistik akurasi ekstraksi
- File output dalam format CSV dan JSON

---
