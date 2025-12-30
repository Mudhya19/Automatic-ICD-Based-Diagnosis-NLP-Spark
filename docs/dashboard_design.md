# Rancangan Dashboard Visualisasi - Otomatisasi Kodefikasi Diagnosis ICD-10

## Pendahuluan

Dashboard ini dirancang untuk menampilkan hasil analisis big data dari proyek otomatisasi kodefikasi diagnosis ICD-10 menggunakan Natural Language Processing (NLP) dan Machine Learning (ML) di RSUD Datu Sanggul, Kabupaten Tapin, Kalimantan Selatan. Dashboard ini ditujukan untuk stakeholder seperti manajemen rumah sakit, unit rekam medis, dan tim coding, sehingga harus menyajikan informasi secara jelas dan mudah dipahami.

## Tujuan Dashboard

1. Menyajikan ringkasan kinerja sistem otomatisasi kodefikasi ICD-10
2. Menampilkan metrik-metrik utama dari model ML terbaik (Random Forest)
3. Memberikan wawasan tentang efisiensi dan akurasi proses coding
4. Menyajikan rekomendasi bisnis dan potensi ROI dari implementasi sistem

## Struktur Dashboard

### 1. Ringkasan Eksekutif (Executive Summary)

Panel ini akan menampilkan metrik-metrik utama secara singkat:

- Jumlah total rekam medis yang dianalisis: 24,806 pasien
- Akurasi model terbaik (Random Forest): 85.89%
- Estimasi penghematan waktu: ~99.2% (dari 1-2 menit per rekam menjadi <1 detik)
- Estimasi ROI tahunan: $199,200 - $298,800

### 2. Kinerja Model ML

Panel ini akan menampilkan visualisasi perbandingan ketiga model ML:

- Grafik batang menampilkan akurasi dari:
  - Model 1: Logistic Regression (~70-80%)
  - Model 2: Linear Regression (R² ~0.7-0.8)
  - Model 3: Random Forest (85.89%) - Model Terbaik

### 3. Validasi NLP

Panel ini akan menampilkan hasil validasi Natural Language Processing:

- Pie chart menampilkan perbandingan antara diagnosis yang cocok dan tidak cocok dengan ground truth
- Akurasi NLP: 85.89%

### 4. Distribusi Kategori Diagnosis

Grafik batang menampilkan distribusi kategori diagnosis (GERIATRI, PARU, KARDIO, SARAF, IGD, JIWA, dll.) untuk menunjukkan beban kerja per poliklinik.

### 5. Rekomendasi dan Insight Bisnis

Panel ini akan menyajikan informasi strategis:

- Rekomendasi implementasi: Model 3 (Random Forest) sebagai model utama
- Estimasi ROI dan payback period <2 bulan
- Timeline implementasi 12 minggu

## Teknologi dan Implementasi

Dashboard akan menggunakan teknologi:

- Apache Spark (PySpark) untuk pemrosesan data besar
- Spark NLP untuk Natural Language Processing
- Machine Learning: Random Forest (model terbaik)
- Visualisasi: Matplotlib dan Seaborn

Dashboard akan dirancang responsif, dengan warna kontras yang ramah untuk presentasi, dan dapat diekspor ke berbagai format (PNG, PDF) untuk laporan.

## Fitur Rentang Tanggal

Dashboard akan menyertakan fitur interaktif untuk memilih rentang tanggal tertentu, memungkinkan stakeholder untuk:

1. Memfilter data berdasarkan periode waktu yang dipilih
2. Melihat tren dan pola dalam rentang waktu tertentu
3. Menganalisis kinerja model secara temporal
4. Melakukan perbandingan antar periode waktu

Fitur ini akan ditempatkan di bagian atas dashboard sebagai kontrol utama yang mempengaruhi semua visualisasi di bawahnya. Stakeholder dapat memilih rentang tanggal menggunakan komponen date picker yang intuitif, dan semua grafik akan diperbarui secara otomatis sesuai dengan rentang waktu yang dipilih.

## Integrasi Dataset

Dashboard akan terhubung ke dua dataset utama:

1. Dataset ICD-10: `csv_path_icd = "/content/drive/MyDrive/Colab Notebooks/dataset/icd-10.csv"`
2. Dataset diagnosis klinis: `csv_path_clinical = "/content/drive/MyDrive/Colab Notebooks/dataset/diagnosis_icd_2025.csv"`

Kedua dataset ini akan digunakan untuk:

- Validasi dan verifikasi kode ICD-10
- Analisis tren diagnosis
- Evaluasi kinerja model prediktif
- Pembuatan visualisasi tren waktu dan distribusi diagnosis

Integrasi ini akan memungkinkan dashboard untuk menampilkan informasi secara real-time dari sumber data asli, memastikan bahwa semua visualisasi dan analisis didasarkan pada data terbaru. Proses integrasi akan menggunakan Apache Spark untuk menangani volume data besar secara efisien, memastikan kinerja dashboard tetap optimal meskipun dengan dataset yang sangat besar.
