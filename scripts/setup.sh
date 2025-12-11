#!/bin/bash

# ============================================================================
# AUTOMATED SETUP SCRIPT - BIG DATA ANALYTICS PROJECT
# Automated ICD Diagnosis Extraction from Medical Records
# RSUD Datu Sanggul
# Modified version for automated execution without user input
# ============================================================================

set -e  # Exit on error

# Color codes untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNGSI UTILITY
# ============================================================================

print_header() {
    echo -e "${BLUE}========================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================================================
# DETEKSI OS
# ============================================================================

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        DISTRO=$(sw_vers -productName 2>/dev/null || echo "Unknown")
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="Windows"
        DISTRO="Windows (native bash)"
    else
        OS="Unknown"
        DISTRO="Unknown"
    fi
}

# ============================================================================
# CEK PRASYARAT SISTEM
# ============================================================================

check_prerequisites() {
    print_header "Checking System Prerequisites"
    
    local missing_deps=0
    
    # Check Python
    if command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        print_success "Python found: $PYTHON_VERSION"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python not found"
        print_info "Please install Python 3.8 or higher"
        missing_deps=$((missing_deps + 1))
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "$GIT_VERSION"
    else
        print_error "Git not found"
        missing_deps=$((missing_deps + 1))
    fi
    
    # Check Java (optional tapi recommended untuk Spark)
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | grep version)
        print_success "Java found: $JAVA_VERSION"
    else
        print_warning "Java not found (recommended for Spark, akan dicoba download otomatis)"
    fi
    
    # Check pip
    if command -v pip &> /dev/null; then
        PIP_VERSION=$(pip --version)
        print_success "$PIP_VERSION"
    elif command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version)
        print_success "$PIP_VERSION"
    else
        print_error "pip not found"
        missing_deps=$((missing_deps + 1))
    fi
    
    if [ $missing_deps -gt 0 ]; then
        print_error "Missing $missing_deps required dependencies"
        return 1
    fi
    
    print_success "All prerequisites met"
    return 0
}

# ============================================================================
# INSTALL DEPENDENCIES BERDASARKAN OS
# ============================================================================

install_system_dependencies() {
    print_header "Installing System Dependencies"
    
    case "$OS" in
        "Linux")
            print_info "Detected Linux ($DISTRO)"
            
            # Update package manager
            if command -v apt-get &> /dev/null; then
                print_info "Using apt-get package manager"
                sudo apt-get update -y
                
                # Install dependencies
                sudo apt-get install -y \
                    python3-dev \
                    python3-pip \
                    build-essential \
                    git \
                    wget \
                    curl \
                    openjdk-11-jdk
                    
                print_success "System dependencies installed (apt-get)"
                
            elif command -v yum &> /dev/null; then
                print_info "Using yum package manager"
                sudo yum update -y
                sudo yum install -y \
                    python3-devel \
                    gcc \
                    gcc-c++ \
                    git \
                    wget \
                    curl \
                    java-11-openjdk
                    
                print_success "System dependencies installed (yum)"
                
            elif command -v pacman &> /dev/null; then
                print_info "Using pacman package manager (Arch Linux)"
                sudo pacman -Syu --noconfirm
                sudo pacman -S --noconfirm \
                    python \
                    base-devel \
                    git \
                    wget \
                    curl \
                    jdk1-openjdk
                    
                print_success "System dependencies installed (pacman)"
            fi
            ;;
            
        "macOS")
            print_info "Detected macOS ($DISTRO)"
            
            # Check if Homebrew is installed
            if ! command -v brew &> /dev/null; then
                print_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            print_info "Using Homebrew"
            brew update
            brew install python@3.11 git wget curl openjdk@11
            
            # Link Java
            if [ -d "/opt/homebrew/opt/openjdk@11" ]; then
                export JAVA_HOME=/opt/homebrew/opt/openjdk@11
            fi
            
            print_success "System dependencies installed (Homebrew)"
            ;;
            
        "Windows")
            print_info "Detected Windows"
            print_warning "Please ensure you have installed:"
            print_warning "  1. Python 3.8+ (https://www.python.org/downloads/)"
            print_warning "  2. Git (https://git-scm.com/download/win)"
            print_warning "  3. Java JDK 11+ (https://adoptium.net/)"
            print_info "Continuing with Python package setup..."
            ;;
            
        *)
            print_warning "Unknown OS detected, attempting to continue..."
            ;;
    esac
}

# ============================================================================
# SETUP PYTHON VIRTUAL ENVIRONMENT
# ============================================================================

setup_virtualenv() {
    print_header "Setting Up Python Virtual Environment"
    
    if [ -d ".venv" ]; then
        print_warning "Virtual environment already exists"
        print_info "Removing existing virtual environment for fresh setup..."
        rm -rf .venv
        print_info "Removed existing virtual environment"
    fi
    
    print_info "Creating virtual environment..."
    if command -v python &> /dev/null; then
        python -m venv .venv
    else
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    if [[ "$OS" == "Windows" ]]; then
        if [ -f ".venv/Scripts/activate" ]; then
            source .venv/Scripts/activate
        elif [ -f ".venv\\Scripts\\activate" ]; then
            source .venv\\Scripts\\activate
        elif [ -f ".venv/bin/activate" ]; then
            print_warning "Unix-style virtual environment found on Windows. Recreating for Windows compatibility..."
            rm -rf .venv
            if command -v python &> /dev/null; then
                python -m venv .venv
            else
                python3 -m venv .venv
            fi
            source .venv/Scripts/activate
        else
            print_error "Virtual environment activation script not found for Windows"
            return 1
        fi
    else
        if [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate
        elif [ -f ".venv/Scripts/activate" ]; then
            source .venv/Scripts/activate
        elif [ -f ".venv\\Scripts\\activate" ]; then
            source .venv\\Scripts\\activate
        else
            print_error "Virtual environment activation script not found"
            return 1
        fi
    fi
    
    print_success "Virtual environment created and activated"
    
    # Upgrade pip, setuptools, wheel
    print_info "Upgrading pip, setuptools, and wheel..."
    if command -v python &> /dev/null; then
        python -m pip install --upgrade pip setuptools wheel
    else
        pip install --upgrade pip setuptools wheel
    fi
    
    print_success "Virtual environment setup complete"
}

# ============================================================================
# INSTALL PYTHON DEPENDENCIES
# ============================================================================

install_python_dependencies() {
    print_header "Installing Python Dependencies"
    
    # Activate virtual environment
    if [[ "$OS" == "Windows" ]]; then
        if [ -f ".venv/Scripts/activate" ]; then
            source .venv/Scripts/activate
        elif [ -f ".venv\\Scripts\\activate" ]; then
            source .venv\\Scripts\\activate
        elif [ -f ".venv/bin/activate" ]; then
            print_warning "Unix-style virtual environment found on Windows. Recreating for Windows compatibility..."
            rm -rf .venv
            if command -v python &> /dev/null; then
                python -m venv .venv
            else
                python3 -m venv .venv
            fi
            source .venv/Scripts/activate
        else
            print_error "Virtual environment activation script not found for Windows"
            return 1
        fi
    else
        if [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate
        elif [ -f ".venv/Scripts/activate" ]; then
            source .venv/Scripts/activate
        elif [ -f ".venv\\Scripts\\activate" ]; then
            source .venv\\Scripts\\activate
        else
            print_error "Virtual environment activation script not found"
            return 1
        fi
    fi
    
    print_info "Installing Python packages..."
    
    # List of packages
    packages=(
        "pyspark==3.5.0"
        "spark-nlp==5.2.2"
        "pandas>=1.3.0"
        "jupyter>=1.0.0"
        "jupyterlab>=3.0.0"
        "matplotlib>=3.3.0"
        "seaborn>=0.11.0"
        "scikit-learn>=0.24.0"
        "numpy>=1.21.0"
        "scipy>=1.7.0"
    )
    
    for package in "${packages[@]}"; do
        print_info "Installing: $package"
        if command -v python &> /dev/null; then
            python -m pip install "$package"
        else
            pip install "$package"
        fi
    done
    
    print_success "All Python dependencies installed"
}

# ============================================================================
# CLONE SPARK NLP REPOSITORY
# ============================================================================

clone_sparknlp_repo() {
    print_header "Cloning Spark NLP Repository"
    
    if [ -d "spark-nlp" ]; then
        print_warning "spark-nlp directory already exists"
        print_info "Pulling latest changes..."
        cd spark-nlp
        git pull origin master
        cd ..
        print_success "spark-nlp repository updated"
    else
        print_info "Cloning spark-nlp repository..."
        git clone --depth 1 --config core.longpaths=true https://github.com/JohnSnowLabs/spark-nlp.git
        print_success "spark-nlp repository cloned"
    fi
}

# ============================================================================
# SETUP DIREKTORI PROYEK
# ============================================================================

setup_project_directories() {
    print_header "Setting Up Project Directories"
    
    # Create necessary directories
    mkdir -p database
    mkdir -p output
    mkdir -p output/logs
    mkdir -p models
    mkdir -p src
    mkdir -p notebooks
    mkdir -p image
    mkdir -p test
    mkdir -p config
    
    print_success "Project directories created"
    
    # Create sample CSV jika tidak ada
    if [ ! -f "database/diagnosis_icd_2025.csv" ]; then
        print_info "Creating sample diagnosis_icd_2025.csv..."
        
        cat > database/diagnosis_icd_2025.csv << 'EOF'
id_pasien,nm_pasien,jk,umur_pasien,id_kunjungan,tgl_registrasi,nm_dokter,rekam_medis_narasi,diagnosis_structured
153284,H. KURSANI Tn,L,71,2025/01/01/0004,2025-01-01,dr. Resti Riyandina Mujiarto,"Patient: H. KURSANI Tn, Age: 71 years old. Chief Complaint: mimisan sejak jam 22.00 td malam, perdarahan aktif (+) sebelah kiri. mual (+) muntah (+) riw HT (+). Physical Examination: Mata: ca (-/-) si (-/-)isokor (+/+) cowong (-/-) Leher: kaku kuduk (-) Thoraks: simetris. Retraksi (-) Pulmo: rhonki - / - / - - / - wheezing - / - - / - - / - Cor s1 s2 reguler. Abd: BU + N. Timpani. Nyeri tekan: - / - / - - / - / - - / - / - CVA (-/-) Defans muskular (-) Hepatomegali (-) Splenomegali (-). Assessment: HT emergency epistaksis posterior. Diagnosis: Essential (primary) hypertension, Epistaxis.","Essential (primary) hypertension, Epistaxis"
153285,Siti Nurhaliza,P,55,2025/01/02/00005,2025-01-02,dr. Bambang Sutrisno,"Patient: Siti Nurhaliza, Age: 55 years old. Chief Complaint: Shortness of breath for 1 day, cough, dan demam. Physical Examination: SpO2 92%, BP 165/100 mmHg, RR 22/min. Pulmo: Crackles bilateral, ronkhi. Abd: BU normal, tidak ada massa. Cor: S1 S2 reguler. Assessment: Community-acquired pneumonia dengan tanda vital tidak stabil. Diagnosis: Community-acquired pneumonia, Hypertension stage 2, Type 2 diabetes mellitus.","Community-acquired pneumonia, Hypertension stage 2, Type 2 diabetes mellitus"
153286,Budi Santoso,L,45,2025/01/03/0006,2025-01-03,dr. Rina Widyaningsih,"Patient: Budi Santoso, Age: 45 years old. Chief Complaint: Post-operative follow-up from appendectomy. Physical Examination: Luka operasi baik, tidak ada infeksi, tanda vital stabil. Abd: Tidak nyeri, BU normal. Assessment: Status post-appendectomy day 3 dengan pemulihan baik. Diagnosis: Status post-appendectomy, Overweight, Hypertension.","Status post-appendectomy, Overweight, Hypertension"
EOF
        
        print_success "Sample CSV created at: database/diagnosis_icd_2025.csv"
    else
        print_info "CSV file already exists at: database/diagnosis_icd_2025.csv"
    fi
}

# ============================================================================
# SETUP ENVIRONMENT VARIABLES
# ============================================================================

setup_environment_variables() {
    print_header "Setting Up Environment Variables"
    
    # Create .env file jika tidak ada
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# Environment variables untuk Automated ICD Diagnosis Extraction Project

# Python dan Virtual Environment
PYTHON_VERSION=3.9
VENV_PATH=./.venv

# Spark Configuration
SPARK_HOME=$JAVA_HOME/spark
SPARK_LOCAL_IP=127.0.1
SPARK_MASTER=local[*]

# Spark NLP Configuration
SPARKNLP_VERSION=5.2.2

# Java Configuration
JAVA_OPTS="-Xmx8g -Xms1g"

# Project Paths
PROJECT_ROOT=$(pwd)
DATABASE_PATH=$PROJECT_ROOT/database
OUTPUT_PATH=$PROJECT_ROOT/output
MODELS_PATH=$PROJECT_ROOT/models

# Logging
LOG_LEVEL=INFO
LOG_PATH=$OUTPUT_PATH/logs

# Database Configuration (jika menggunakan MySQL/MariaDB SIMRS)
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=password
# DB_NAME=simrs_db

# Uncomment untuk production deployment
# ENVIRONMENT=production
EOF
        
        print_success ".env file created"
    fi
    
    # Source .env
    if [ -f ".env" ]; then
        set -a
        source .env
        set +a
        print_success "Environment variables loaded"
    fi
}

# ============================================================================
# VERIFY INSTALLATION
# ============================================================================

verify_installation() {
    print_header "Verifying Installation"
    
    # Activate virtual environment
    if [[ "$OS" == "Windows" ]]; then
        if [ -f ".venv/Scripts/activate" ]; then
            source .venv/Scripts/activate
        elif [ -f ".venv\\Scripts\\activate" ]; then
            source .venv\\Scripts\\activate
        elif [ -f ".venv/bin/activate" ]; then
            print_warning "Unix-style virtual environment found on Windows. Recreating for Windows compatibility..."
            rm -rf .venv
            python3 -m venv .venv
            source .venv/Scripts/activate
        else
            print_error "Virtual environment activation script not found for Windows"
            return 1
        fi
    else
        if [ -f ".venv/bin/activate" ]; then
            source .venv/bin/activate
        elif [ -f ".venv/Scripts/activate" ]; then
            source .venv/Scripts/activate
        elif [ -f ".venv\\Scripts\\activate" ]; then
            source .venv\\Scripts\\activate
        else
            print_error "Virtual environment activation script not found"
            return 1
        fi
    fi
    
    # Test Python imports
    print_info "Testing Python imports..."
    
    if command -v python &> /dev/null; then
        python << 'PYTHON_TEST'
import sys
print("Python Version: {}".format(sys.version))

try:
    import pyspark
    print("PySpark imported successfully")
except ImportError as e:
    print("PySpark import failed: {}".format(e))

try:
    import sparknlp
    print("SparkNLP imported successfully")
except ImportError as e:
    print("SparkNLP import failed: {}".format(e))

try:
    import pandas
    print("Pandas imported successfully")
except ImportError as e:
    print("Pandas import failed: {}".format(e))

try:
    import jupyter
    print("Jupyter imported successfully")
except ImportError as e:
    print("Jupyter import failed: {}".format(e))

try:
    import numpy
    print("NumPy imported successfully")
except ImportError as e:
    print("NumPy import failed: {}".format(e))
PYTHON_TEST
    else
        python3 << 'PYTHON_TEST'
import sys
print("Python Version: {}".format(sys.version))

try:
    import pyspark
    print("PySpark imported successfully")
except ImportError as e:
    print("PySpark import failed: {}".format(e))

try:
    import sparknlp
    print("SparkNLP imported successfully")
except ImportError as e:
    print("SparkNLP import failed: {}".format(e))

try:
    import pandas
    print("Pandas imported successfully")
except ImportError as e:
    print("Pandas import failed: {}".format(e))

try:
    import jupyter
    print("Jupyter imported successfully")
except ImportError as e:
    print("Jupyter import failed: {}".format(e))

try:
    import numpy
    print("NumPy imported successfully")
except ImportError as e:
    print("NumPy import failed: {}".format(e))
PYTHON_TEST
    fi
    
    print_success "Installation verification complete"
}

# ============================================================================
# CREATE QUICKSTART SCRIPT
# ============================================================================

create_quickstart_script() {
    print_header "Creating Quickstart Script"
    
    cat > start_jupyter.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
    elif [ -f ".venv\\Scripts\\activate" ]; then
        source .venv\\Scripts\\activate
    else
        echo "Virtual environment activation script not found for Windows"
        exit 1
    fi
else
    source .venv/bin/activate
fi

# Start Jupyter Lab
echo "Starting Jupyter Lab..."
jupyter lab
EOF
    
    chmod +x start_jupyter.sh
    
    print_success "Quickstart script created: scripts/start_jupyter.sh"
    
    # Also create Windows batch script
    cat > start_jupyter.bat << 'EOF_WINDOWS'
@echo off

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Jupyter Lab...
call .venv\Scripts\jupyter-lab.exe
EOF_WINDOWS
    
    print_success "Windows quickstart script created: scripts/start_jupyter.bat"
}

# ============================================================================
# DISPLAY FINAL SUMMARY
# ============================================================================

display_summary() {
    print_header "SETUP COMPLETE - SUMMARY"
    
    echo -e "\n${GREEN}System Information:${NC}"
    echo " OS: $OS ($DISTRO)"
    if command -v python &> /dev/null; then
        echo "  Python: $(python --version)"
    else
        echo "  Python: $(python3 --version)"
    fi
    if command -v pip &> /dev/null; then
        echo "  Pip: $(pip --version)"
    else
        echo "  Pip: $(pip3 --version)"
    fi
    
    echo -e "\n${GREEN}Project Structure:${NC}"
    echo "  Database: ./database/"
    echo "  Output: ./output/"
    echo "  Models: ./models/"
    echo "  Source: ./src/"
    echo "  Notebooks: ./notebooks/"
    echo "  Image: ./image/"
    echo "  Test: ./test/"
    echo "  Config: ./config/"
    
    echo -e "\n${GREEN}Key Packages Installed:${NC}"
    echo " - Apache Spark 3.5.0"
    echo " - Spark NLP 5.2"
    echo "  - Pandas, NumPy, Matplotlib, Seaborn"
    echo "  - Jupyter Lab"
    
    echo -e "\n${GREEN}Next Steps:${NC}"
    echo "  1. Copy or move your CSV file to: ./database/diagnosis_icd_2025.csv"
    echo "  2. Activate virtual environment:"
    
    if [[ "$OS" == "Windows" ]]; then
        echo "     .venv\\Scripts\\activate"
    else
        echo "     source .venv/bin/activate"
    fi
    
    echo " 3. Start Jupyter Lab:"
    echo "     bash start_jupyter.sh  # Linux/Mac"
    echo "     .venv\\Scripts\\activate && jupyter lab     # Windows"
    echo " 4. Open automated_icd_diagnosis.ipynb notebook"
    echo "  5. Run cells sequentially to process medical records"
    
    echo -e "\n${GREEN}Documentation:${NC}"
    echo "  - See: INSTRUCTION-AUTOMATED-ICD-DIAGNOSIS.md"
    echo "  - Repository: https://github.com/JohnSnowLabs/spark-nlp"
    
    echo -e "\n${BLUE}========================================================================${NC}"
    echo -e "${GREEN}✓ Setup completed successfully!${NC}"
    echo -e "${BLUE}========================================================================${NC}\n"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    clear
    
    echo -e "${BLUE}"
    echo "========================================================================="
    echo "  AUTOMATED SETUP - BIG DATA ANALYTICS PROJECT"
    echo " Automated ICD Diagnosis Extraction"
    echo "  RSUD Datu Sanggul"
    echo "  (Automated version - no user input required)"
    echo "========================================================================="
    echo -e "${NC}\n"
    
    # Detect OS
    detect_os
    print_success "OS Detected: $OS ($DISTRO)"
    
    # Check prerequisites
    print_info "This setup script will:"
    print_info "  1. Check system prerequisites"
    print_info "  2. Install system dependencies"
    print_info "  3. Setup Python virtual environment"
    print_info " 4. Install Python packages"
    print_info "  5. Clone Spark NLP repository"
    print_info "  6. Setup project directories"
    print_info "  7. Configure environment variables"
    print_info "  8. Verify installation"
    
    print_info "Continuing with setup (automated)..."
    
    # Execute setup steps
    check_prerequisites || {
        print_warning "Some prerequisites are missing, attempting to install them..."
        install_system_dependencies
    }
    
    install_system_dependencies
    setup_virtualenv
    install_python_dependencies
    clone_sparknlp_repo
    setup_project_directories
    setup_environment_variables
    verify_installation
    create_quickstart_script
    display_summary
}

# ============================================================================
# JALANKAN MAIN
# ============================================================================

# Handle script errors
trap 'print_error "Setup failed. Please check the error messages above."; exit 1' ERR

# Run main function
main

exit 0