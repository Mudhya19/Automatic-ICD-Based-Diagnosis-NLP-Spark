import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# KONFIGURASI
# =========================
st.set_page_config(
    page_title="Dashboard ICD-10",
    layout="wide"
)

DIAG_PATH = "database/dataset/diagnosis_icd_2025.csv"
ICD_PATH  = "database/dataset/icd-10.csv"

# =========================
# UTILITAS
# =========================
def normalize_text(x: str) -> str:
    if pd.isna(x):
        return ""
    x = str(x).lower()
    # Replace multiple whitespace with single space using built-in string methods
    x = " ".join(x.split())
    return x

# Kamus poli sederhana (baseline) - boleh Anda tambah keyword-nya
POLI_KEYWORDS = {
    "IGD": ["demam", "sesak", "trauma", "cedera", "pingsan", "syncope", "acute", "gawat", "nyeri hebat"],
    "JANTUNG": ["jantung", "angina", "mi", "ami", "i20", "i21", "heart failure", "gagal jantung"],
    "PARU": ["pneumonia", "bronchitis", "tuberculosis", "tb", "paru", "j18", "j20", "a15"],
    "THT": ["tonsillitis", "pharyngitis", "sinusitis", "otitis", "telinga", "hidung", "tenggorok", "j02", "j03", "j32", "h66"],
    "MATA": ["cataract", "katarak", "glaucoma", "conjunctivitis", "mata", "h25", "h40", "h10"],
    "OBGYN": ["persalinan", "delivery", "pre-eclampsia", "preeklamsia", "gestational", "placenta", "o80", "o14", "o24.4", "o44"],
    "BEDAH": ["appendicitis", "hernia", "cholelithiasis", "fracture", "fraktur", "k35", "k40", "k80", "s72"],
    "GERIATRI": ["hipertensi", "hypertension", "diabetes", "dm", "dementia", "alzheimer", "i10", "e11", "f03", "g30"],
    "FISIOTERAPI": ["low back pain", "nyeri pinggang", "cervicalgia", "rehabilitasi", "hemiplegia", "m54.5", "m54.2", "g81", "z50"],
    "HEMODIALISIS": ["hemodialysis", "dialysis", "cuci darah", "esrd", "ckd", "n18", "n18.6", "z99.2"],
    "KULIT_KELAMIN": ["dermatitis", "psoriasis", "acne", "tinea", "kutil", "l20", "l40", "l70", "b35.4", "a63"],
    "JIWA": ["depression", "depresi", "anxiety", "cemas", "schizophrenia", "bipolar", "insomnia", "f32", "f41", "f20", "f31", "g47"],
    "SARAF": ["stroke", "epilepsy", "epilepsi", "parkinson", "migraine", "i63", "g40", "g20", "g43"],
    "ANAK": ["ispa", "uri", "upper respiratory", "kejang demam", "febrile", "j06", "r56"],
}

def categorize_poli(diagnosis_text: str) -> str:
    t = normalize_text(diagnosis_text)
    if not t:
        return "TIDAK_DIISI"
    for poli, keywords in POLI_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                return poli
    return "OTHER"

@st.cache_data(show_spinner=False)
def load_data():
    df_diag = pd.read_csv(DIAG_PATH)
    df_icd  = pd.read_csv(ICD_PATH)
    return df_diag, df_icd

def pick_date_column(df: pd.DataFrame):
    # prefer kolom dari notebook: tglregistrasi
    candidates = ["tglregistrasi", "tgl_registrasi", "tanggal", "date", "tgl"]
    for c in candidates:
        if c in df.columns:
            return c
    return None

def parse_dates(s: pd.Series) -> pd.Series:
    # notebook Anda memakai format d/M/yyyy (contoh "1/1/2025") [file:22]
    # coba parsing fleksibel
    dt = pd.to_datetime(s, errors="coerce", dayfirst=True)
    # Konversi ke date jika berhasil diparse
    if dt.dt.tz is not None:
        dt = dt.dt.tz_localize(None)
    return dt

# =========================
# LOAD
# =========================
st.title("Dashboard Sederhana ICD-10")

try:
    df_diag, df_icd = load_data()
except Exception as e:
    st.error(f"Gagal membaca file CSV. Pastikan path benar.\n\nDetail: {e}")
    st.stop()

date_col = pick_date_column(df_diag)
if date_col is None:
    st.error("Kolom tanggal tidak ditemukan. Pastikan ada kolom seperti 'tglregistrasi' / 'tanggal'.")
    st.stop()

df = df_diag.copy()
df[date_col] = parse_dates(df[date_col])

# kolom diagnosis (pakai yang paling mungkin)
diag_col_candidates = ["diagnosis_structured", "diagnosisstructured", "diagnosis", "diagnosa", "dx"]
diag_col = next((c for c in diag_col_candidates if c in df.columns), None)
if diag_col is None:
    # fallback: pakai kolom pertama bertipe object
    obj_cols = [c for c in df.columns if df[c].dtype == "object"]
    diag_col = obj_cols[0] if obj_cols else df.columns[0]

# kolom umur
age_col = "umurpasien" if "umurpasien" in df.columns else None

# buat kolom poli (rule-based)
df["poli"] = df[diag_col].apply(categorize_poli)

# buang baris tanggal invalid
df = df.dropna(subset=[date_col])

# =========================
# FILTER UI (1 baris)
# =========================
# Ambil min dan max date dari kolom tanggal
min_datetime = df[date_col].min()
max_datetime = df[date_col].max()
min_date = min_datetime.date() if pd.notna(min_datetime) else min_datetime
max_date = max_datetime.date() if pd.notna(max_datetime) else max_datetime

colA, colB, colC = st.columns([1.2, 1.0, 1.0])
with colA:
    date_range = st.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
with colB:
    poli_list = ["SEMUA"] + sorted(df["poli"].unique().tolist())
    selected_poli = st.selectbox("Pilih poli (rule-based)", poli_list)
with colC:
    topn = st.slider("Top diagnosis", min_value=5, max_value=30, value=10, step=5)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Buat filter berdasarkan rentang tanggal
if start_date and end_date:
    # Konversi kolom tanggal ke format date untuk perbandingan
    df_date = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d') if start_date else df_date.min()
    end_date_str = end_date.strftime('%Y-%m-%d') if end_date else df_date.max()
    mask = (df_date >= start_date_str) & (df_date <= end_date_str)
    df_f = df.loc[mask].copy()
else:
    df_f = df.copy()

if selected_poli != "SEMUA":
    df_f = df_f[df_f["poli"] == selected_poli]

# =========================
# KPI
# =========================
k1, k2, k3, k4 = st.columns(4)
k1.metric("Record terfilter", f"{len(df_f):,}")
k2.metric("Total record (raw)", f"{len(df):,}")
k3.metric("Kode ICD-10 (katalog)", f"{len(df_icd):,}")
missing_diag = int(df_f[diag_col].isna().sum())
k4.metric("Diagnosis kosong (filter)", f"{missing_diag:,}")

st.divider()

# =========================
# VISUALISASI (1 halaman)
# =========================
left, right = st.columns([1.3, 1.0])

with left:
    # Trend harian
    ts = (
        df_f
        .assign(tanggal=pd.to_datetime(df_f[date_col]).dt.strftime('%Y-%m-%d'))
        .groupby('tanggal')
        .size()
        .reset_index(name="jumlah_kunjungan")
    )
    fig_ts = px.line(
        ts,
        x="tanggal",
        y="jumlah_kunjungan",
        markers=True,
        title="Trend Kunjungan/Record per Hari (berdasarkan filter)"
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    # Distribusi poli
    poli_counts = df_f["poli"].value_counts().reset_index()
    poli_counts.columns = ["poli", "count"]
    fig_poli = px.bar(
        poli_counts,
        x="poli",
        y="count",
        title="Distribusi Poli (rule-based) pada Data Terfilter"
    )
    fig_poli.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig_poli, use_container_width=True)

with right:
    # Top diagnosis
    top_diag = (
        df_f[diag_col]
        .fillna("TIDAK_DIISI")
        .astype(str)
        .value_counts()
        .head(topn)
        .reset_index()
    )
    top_diag.columns = ["diagnosis", "count"]
    fig_top = px.bar(
        top_diag.sort_values("count"),
        x="count",
        y="diagnosis",
        orientation="h",
        title=f"Top {topn} Diagnosis (berdasarkan filter)",
        labels={'diagnosis': 'Diagnosis', 'count': 'Jumlah'}
    )
    st.plotly_chart(fig_top, use_container_width=True)

    # Distribusi usia (jika ada)
    if age_col is not None:
        df_age = df_f[[age_col]].dropna()
        if len(df_age) > 0:
            fig_age = px.histogram(
                df_age,
                x=age_col,
                nbins=20,
                title="Distribusi Umur Pasien (data terfilter)"
            )
            st.plotly_chart(fig_age, use_container_width=True)

st.divider()

# =========================
# TABEL DATA (opsional)
# =========================
st.subheader("Tabel Data Terfilter (preview)")
show_cols = [c for c in [date_col, "poli", diag_col, age_col, "nmdokter", "jk"] if c and c in df_f.columns]
st.dataframe(df_f[show_cols].head(200), use_container_width=True)
