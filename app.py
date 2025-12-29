import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta
import glob

# Set page config
st.set_page_config(layout="wide", page_title="Automated ICD-10 Coding Analytics – SIMRS")

# Function to find latest file
def find_latest_file(pattern, folder="data"):
    files = glob.glob(os.path.join(folder, pattern))
    if not files:
        return None
    return max(files, key=os.path.getctime)

# Function to load JSON with caching
@st.cache_data
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Function to load CSV with caching
@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

# Header
st.title("📊 Automated ICD-10 Coding Analytics – SIMRS")
st.markdown("""
Dashboard untuk analisis otomatisasi kodefikasi diagnosis ICD-10 berbasis NLP di SIMRS. 
Menyediakan insight tentang kinerja model, tren beban kerja, dan kualitas diagnosis.
""")

# Sidebar
with st.sidebar:
    st.header("📁 Input Data")
    
    # File uploaders
    json_file = st.file_uploader("Upload JSON metrik", type=['json'])
    csv_predictions = st.file_uploader("Upload predictions sample CSV", type=['csv'])
    csv_clinical = st.file_uploader("Upload clinical CSV (optional)", type=['csv'])
    
    # Toggle for sampling
    use_sampling = st.toggle("Use sampling (e.g., 20000 rows)", value=True)
    
    # Load data based on uploads or auto-detect
    model_results = None
    predictions_df = None
    clinical_df = None
    latest_json = None
    latest_csv_pred = None
    latest_csv_clin = None
    
    # Auto-detect files if no uploads
    if not json_file:
        latest_json = find_latest_file("modelresults*.json", "data")
        if latest_json:
            try:
                model_results = load_json(latest_json)
            except:
                st.warning(f"Tidak dapat memuat {latest_json}")
    
    if not csv_predictions:
        latest_csv_pred = find_latest_file("predictionssample*.csv", "data")
        if latest_csv_pred:
            try:
                predictions_df = load_csv(latest_csv_pred)
                if use_sampling and len(predictions_df) > 20000:
                    predictions_df = predictions_df.sample(20000)
            except:
                st.warning(f"Tidak dapat memuat {latest_csv_pred}")
    
    if not csv_clinical:
        latest_csv_clin = find_latest_file("pertama-diagnosis-icd.csv", "data")
        if latest_csv_clin:
            try:
                clinical_df = load_csv(latest_csv_clin)
                if use_sampling and len(clinical_df) > 200:
                    clinical_df = clinical_df.sample(20000)
            except:
                st.warning(f"Tidak dapat memuat {latest_csv_clin}")
    
    # Handle uploaded files
    if json_file:
        try:
            model_results = json.load(json_file)
        except:
            st.error("Gagal memuat file JSON")
    
    if csv_predictions:
        try:
            predictions_df = pd.read_csv(csv_predictions)
            if use_sampling and len(predictions_df) > 20000:
                predictions_df = predictions_df.sample(20000)
        except:
            st.error("Gagal memuat file CSV predictions")
    
    if csv_clinical:
        try:
            clinical_df = pd.read_csv(csv_clinical)
            if use_sampling and len(clinical_df) > 20000:
                clinical_df = clinical_df.sample(20000)
            
            # Date range filter
            if 'tgl_registrasi' in clinical_df.columns:
                clinical_df['tgl_registrasi'] = pd.to_datetime(clinical_df['tgl_registrasi'], errors='coerce')
                min_date = clinical_df['tgl_registrasi'].min()
                max_date = clinical_df['tgl_registrasi'].max()
                if pd.notna(min_date) and pd.notna(max_date):
                    date_range = st.date_input(
                        "Filter rentang tanggal",
                        value=(min_date.date(), max_date.date()),
                        min_value=min_date.date(),
                        max_value=max_date.date()
                    )
                    if len(date_range) == 2:
                        start_date = pd.Timestamp(date_range[0])
                        end_date = pd.Timestamp(date_range[1])
                        clinical_df = clinical_df[
                            (clinical_df['tgl_registrasi'] >= start_date) &
                            (clinical_df['tgl_registrasi'] <= end_date)
                        ]
            
            # Gender filter
            if 'jk' in clinical_df.columns:
                gender_options = clinical_df['jk'].dropna().unique().tolist()
                selected_genders = st.multiselect("Filter gender", options=gender_options, default=gender_options)
                clinical_df = clinical_df[clinical_df['jk'].isin(selected_genders)]
            
            # Age group filter
            if 'umur_pasien' in clinical_df.columns:
                clinical_df['age_group'] = pd.cut(
                    clinical_df['umur_pasien'],
                    bins=[0, 5, 18, 65, 100],
                    labels=['Infant (0-5)', 'Child (6-18)', 'Adult (19-65)', 'Senior (65+)']
                )
                age_groups = clinical_df['age_group'].dropna().unique().tolist()
                selected_age_groups = st.multiselect("Filter kelompok usia", options=age_groups, default=age_groups)
                clinical_df = clinical_df[clinical_df['age_group'].isin(selected_age_groups)]

        except:
            st.error("Gagal memuat file CSV clinical")

# Display warning if no data available
if model_results is None and (predictions_df is None or predictions_df.empty) and (clinical_df is None or clinical_df.empty):
    st.warning("""
    🔍 Tidak ada file data ditemukan. Silakan:
    - Pastikan file modelresults*.json, predictionssample*.csv, dan/atau pertama-diagnosis-icd.csv ada di folder 'data/'
    - Atau upload file melalui sidebar
    """)

# Get last loaded file info
last_loaded_info = []
if latest_json:
    last_loaded_info.append(f"JSON: {os.path.basename(latest_json)}")
if latest_csv_pred:
    last_loaded_info.append(f"Predictions: {os.path.basename(latest_csv_pred)}")
if latest_csv_clin:
    last_loaded_info.append(f"Clinical: {os.path.basename(latest_csv_clin)}")
if json_file:
    last_loaded_info.append(f"JSON: {json_file.name}")
if csv_predictions:
    last_loaded_info.append(f"Predictions: {csv_predictions.name}")
if csv_clinical:
    last_loaded_info.append(f"Clinical: {csv_clinical.name}")

# Header & Ringkasan
st.header("📋 Ringkasan Utama")
col1, col2, col3, col4, col5, col6 = st.columns(6)

# KPI Metrics
total_records = 0
nlp_accuracy = "N/A"
best_model_accuracy = "N/A"
time_saving = "N/A"
missing_diagnosis_pct = "N/A"

if model_results:
    if 'total_records_analyzed' in model_results:
        total_records = model_results['total_records_analyzed']
    
    if 'nlp_validation' in model_results and 'accuracy' in model_results['nlp_validation']:
        nlp_accuracy = model_results['nlp_validation']['accuracy'].replace('%', '')
    
    if 'models' in model_results:
        models = model_results['models']
        if 'model_3_random_forest' in models:
            rf_model = models['model_3_random_forest']
            if 'accuracy' in rf_model:
                best_model_accuracy = f"{rf_model['accuracy']:.2f}"
        elif 'model_1_logistic_regression' in models:
            lr_model = models['model_1_logistic_regression']
            if 'accuracy' in lr_model:
                best_model_accuracy = f"{lr_model['accuracy']:.2f}"
    
    if 'expected_roi_annual' in model_results:
        # Estimasi jam hemat berdasarkan ROI tahunan
        time_saving = "150-300 jam/bulan"

if clinical_df is not None and 'diagnosis_structured' in clinical_df.columns:
    missing_diagnosis = clinical_df['diagnosis_structured'].isna().sum()
    total_diagnosis = len(clinical_df)
    missing_diagnosis_pct = f"{(missing_diagnosis/total_diagnosis)*100:.1f}%" if total_diagnosis > 0 else "0%"

with col1:
    st.metric(label="Total Records", value=f"{total_records:,}" if total_records > 0 else "N/A")
with col2:
    st.metric(label="NLP Accuracy", value=f"{nlp_accuracy}%" if nlp_accuracy != 'N/A' else "N/A")
with col3:
    st.metric(label="Best Model Acc", value=f"{best_model_accuracy}%" if best_model_accuracy != 'N/A' else "N/A")
with col4:
    st.metric(label="Estimasi Hemat Waktu", value=time_saving)
with col5:
    st.metric(label="% Missing Diagnosis", value=missing_diagnosis_pct)
with col6:
    data_available = (model_results is not None) or (predictions_df is not None and not predictions_df.empty) or (clinical_df is not None and not clinical_df.empty)
    st.metric(label="Data Tersedia", value="✅" if data_available else "❌")

# Row Grafik Utama
st.header("📈 Grafik Utama")

col1, col2 = st.columns(2)

with col1:
    if clinical_df is not None and 'tgl_registrasi' in clinical_df.columns:
        # Workload chart (jumlah kunjungan per tanggal)
        clinical_df['tgl_registrasi'] = pd.to_datetime(clinical_df['tgl_registrasi'], errors='coerce')
        daily_visits = clinical_df.groupby(pd.Grouper(key='tgl_registrasi', freq='D')).size().reset_index(name='count')
        daily_visits = daily_visits.dropna()
        daily_visits = daily_visits.dropna()
        
        if not daily_visits.empty:
            fig = px.line(daily_visits, x='tgl_registrasi', y='count', title='Trend Jumlah Kunjungan per Hari')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data kunjungan valid untuk ditampilkan")
    else:
        # Fallback to predictions data if clinical not available
        if predictions_df is not None:
            # Use index as time proxy if no date column
            temp_df = pd.DataFrame({'index': range(len(predictions_df)), 'count': 1})
            temp_df = temp_df.groupby(temp_df['index'] // 100).size().reset_index(name='count')
            fig = px.line(temp_df, x='index', y='count', title='Trend Prediksi (Proxy - berdasarkan urutan data)')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data untuk grafik workload")

with col2:
    if clinical_df is not None and 'diagnosis_structured' in clinical_df.columns:
        # Top 10 diagnosis dari diagnosis_structured
        if 'diagnosis_structured' in clinical_df.columns:
            # Split diagnosis yang dipisahkan koma
            all_diagnoses = []
            for diag_str in clinical_df['diagnosis_structured'].dropna():
                if isinstance(diag_str, str):
                    diagnoses = [d.strip() for d in diag_str.split(',')]
                    all_diagnoses.extend(diagnoses)
            
            if all_diagnoses:
                diag_counts = pd.Series(all_diagnoses).value_counts().head(10)
                fig = px.bar(
                    x=diag_counts.values, 
                    y=diag_counts.index, 
                    orientation='h',
                    title='Top 10 Diagnosis (Structured)'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tidak ada data diagnosis structured")
    else:
        # Fallback to predictions data
        if predictions_df is not None and len(predictions_df.columns) > 0:
            # Use first column as proxy for top classes
            first_col = predictions_df.columns[0]
            if first_col in predictions_df.columns:
                top_classes = predictions_df[first_col].value_counts().head(10)
                fig = px.bar(
                    x=top_classes.values, 
                    y=top_classes.index, 
                    orientation='h',
                    title=f'Top 10 Kelas Prediksi ({first_col})'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data untuk grafik diagnosis")

# Row Kualitas Model
st.header("🔍 Kualitas Model")

col1, col2, col3 = st.columns(3)

with col1:
    # Model comparison chart
    if model_results and 'models' in model_results:
        models_data = []
        models = model_results['models']
        
        if 'model_1_logistic_regression' in models:
            lr = models['model_1_logistic_regression']
            models_data.append({
                'Model': 'Logistic Regression',
                'Accuracy': lr.get('accuracy', 0),
                'F1': lr.get('f1_score', 0)
            })
        
        if 'model_3_random_forest' in models:
            rf = models['model_3_random_forest']
            models_data.append({
                'Model': 'Random Forest',
                'Accuracy': rf.get('accuracy', 0),
                'F1': rf.get('weighted_f1', 0)
            })
        
        if 'model_2_linear_regression' in models:
            linreg = models['model_2_linear_regression']
            models_data.append({
                'Model': 'Linear Regression',
                'R2': linreg.get('r2', 0),
                'RMSE': linreg.get('rmse', 0)
            })
        
        if models_data:
            models_df = pd.DataFrame(models_data)
            # Use accuracy/F1 for comparison
            if 'Accuracy' in models_df.columns:
                fig = px.bar(
                    models_df, 
                    x='Model', 
                    y='Accuracy', 
                    title='Perbandingan Akurasi Model'
                )
                st.plotly_chart(fig, use_container_width=True)
            elif 'R2' in models_df.columns:
                fig = px.bar(
                    models_df, 
                    x='Model', 
                    y='R2', 
                    title='Perbandingan R² Model'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada metrik model untuk ditampilkan")
    else:
        st.info("Tidak ada data model untuk ditampilkan")

with col2:
    # Confusion matrix placeholder
    if predictions_df is not None and 'prediction' in predictions_df.columns and 'label' in predictions_df.columns:
        # Create confusion matrix if both actual and predicted labels exist
        from sklearn.metrics import confusion_matrix
        
        y_true = predictions_df['label'].dropna()
        y_pred = predictions_df['prediction'].dropna()
        
        if len(y_true) > 0 and len(y_pred) > 0:
            # Take minimum length to ensure same size
            min_len = min(len(y_true), len(y_pred))
            cm = confusion_matrix(y_true[:min_len], y_pred[:min_len])
            
            # Create heatmap using plotly.graph_objects instead of figure_factory
            fig = go.Figure(data=go.Heatmap(
                z=cm,
                colorscale='Blues',
                text=cm,
                texttemplate="%{text}",
                textfont={"size":16},
                showscale=True
            ))
            fig.update_layout(
                title='Confusion Matrix',
                xaxis_title='Predicted Label',
                yaxis_title='True Label'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Confusion matrix requires y_true and y_pred columns")
    else:
        st.info("Confusion matrix requires predictions with actual labels")

with col3:
    # Feature importance (Model 3)
    if model_results and 'models' in model_results and 'model_3_random_forest' in model_results['models']:
        rf_model = model_results['models']['model_3_random_forest']
        if 'feature_importance' in rf_model:
            feat_imp = rf_model['feature_importance']
            if isinstance(feat_imp, dict):
                features = list(feat_imp.keys())
                importances = list(feat_imp.values())
                feat_df = pd.DataFrame({'Feature': features, 'Importance': importances})
                feat_df = feat_df.sort_values('Importance', ascending=True)
                
                fig = px.bar(
                    feat_df, 
                    x='Importance', 
                    y='Feature', 
                    orientation='h',
                    title='Feature Importance (Model 3)'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Format feature importance tidak didukung")
        else:
            st.info("Feature importance tidak tersedia. Untuk mengekspor dari notebook, tambahkan kode untuk menyimpan feature importance ke JSON.")
    else:
        st.info("Feature importance hanya tersedia untuk Model 3 (Random Forest)")

# Audit & Drill-down
st.header("🔍 Audit & Drill-down Data")

# Create audit dataframe
audit_df = pd.DataFrame()

if clinical_df is not None:
    # Audit for clinical data - records with missing diagnosis, empty narratives, extreme ages
    audit_conditions = []
    
    if 'diagnosis_structured' in clinical_df.columns:
        missing_diag = clinical_df[clinical_df['diagnosis_structured'].isna() | (clinical_df['diagnosis_structured'] == '')]
        if not missing_diag.empty:
            audit_conditions.append(missing_diag)
    
    if 'rekam_medis_narasi' in clinical_df.columns:
        # Truncate long narrative for display
        clinical_df_display = clinical_df.copy()
        if 'rekam_medis_narasi' in clinical_df_display.columns:
            clinical_df_display['rekam_medis_narasi'] = clinical_df_display['rekam_medis_narasi'].apply(
                lambda x: str(x)[:100] + "..." if pd.notna(x) and len(str(x)) > 10 else x
            )
        
        missing_narrative = clinical_df_display[
            clinical_df_display['rekam_medis_narasi'].isna() | 
            (clinical_df_display['rekam_medis_narasi'] == '')
        ]
        if not missing_narrative.empty:
            audit_conditions.append(missing_narrative)
    
    if 'umur_pasien' in clinical_df.columns:
        extreme_age = clinical_df[(clinical_df['umur_pasien'] < 0) | (clinical_df['umur_pasien'] > 120)]
        if not extreme_age.empty:
            audit_conditions.append(extreme_age)
    
    if audit_conditions:
        audit_df = pd.concat(audit_conditions, ignore_index=True).drop_duplicates()

elif predictions_df is not None:
    # Proxy audit for predictions - low confidence records
    audit_conditions = []
    
    if 'entitycount' in predictions_df.columns:
        low_entities = predictions_df[predictions_df['entitycount'] <= 1]
        if not low_entities.empty:
            audit_conditions.append(low_entities)
    
    if 'narrativelength' in predictions_df.columns:
        short_narrative = predictions_df[predictions_df['narrativelength'] <= 200]
        if not short_narrative.empty:
            audit_conditions.append(short_narrative)
    
    if audit_conditions:
        audit_df = pd.concat(audit_conditions, ignore_index=True).drop_duplicates()

# Display audit dataframe
if not audit_df.empty:
    st.subheader("📋 Tabel Audit (50 Baris Pertama)")
    st.dataframe(audit_df.head(50))
    
    # Download button
    csv = audit_df.head(50).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Tabel Audit (CSV)",
        data=csv,
        file_name="audit_table.csv",
        mime="text/csv"
    )
else:
    st.info("Tidak ada data audit yang memenuhi kriteria")

# How to run
with st.expander("ℹ️ How to run"):
    st.markdown("""
    **Cara Menjalankan Aplikasi:**
    ```bash
    pip install streamlit pandas plotly scikit-learn
    streamlit run app.py
    ```
    
    **Kebutuhan File:**
    - Letakkan file berikut di folder `data/`:
      - `modelresults*.json` (hasil metrik model)
      - `predictionssample*.csv` (contoh prediksi)
      - `pertama-diagnosis-icd.csv` (data klinis opsional)
    
    **Atau gunakan upload di sidebar** untuk memasukkan file secara manual.
    """)
    
    st.markdown("""
    **Contoh isi requirements.txt:**
    ```
    streamlit==1.28.0
    pandas==1.5.3
    plotly==5.15.0
    scikit-learn==1.3.0
    numpy==1.24.3
    ```
    """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #66;'>
    Dashboard Analisis Otomatisasi Kodefikasi ICD-10 | 
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)