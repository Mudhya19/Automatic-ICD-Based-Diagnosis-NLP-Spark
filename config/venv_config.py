"""
Konfigurasi Virtual Environment untuk Proyek Automated ICD Diagnosis Extraction

File ini berisi konfigurasi yang membantu aplikasi menemukan lokasi virtual environment
dan library yang digunakan dalam proyek ini.
"""

import os
import sys
from pathlib import Path

class VenvConfig:
    """
    Kelas konfigurasi untuk virtual environment
    """
    
    # Path ke root proyek
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
    
    # Path ke virtual environment
    VENV_PATH = PROJECT_ROOT / ".venv"
    
    # Path ke skrip aktivasi berdasarkan sistem operasi
    if os.name == 'nt':  # Windows
        ACTIVATE_SCRIPT = VENV_PATH / "Scripts" / "activate"
        PYTHON_EXECUTABLE = VENV_PATH / "Scripts" / "python.exe"
        PIP_EXECUTABLE = VENV_PATH / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        ACTIVATE_SCRIPT = VENV_PATH / "bin" / "activate"
        PYTHON_EXECUTABLE = VENV_PATH / "bin" / "python"
        PIP_EXECUTABLE = VENV_PATH / "bin" / "pip"
    
    # Path ke direktori kerja penting
    DATABASE_PATH = PROJECT_ROOT / "database"
    OUTPUT_PATH = PROJECT_ROOT / "output"
    MODELS_PATH = PROJECT_ROOT / "models"
    NOTEBOOKS_PATH = PROJECT_ROOT / "notebooks"
    APP_PATH = PROJECT_ROOT / "app"
    CONFIG_PATH = PROJECT_ROOT / "config"
    UTILS_PATH = PROJECT_ROOT / "utils"
    
    # Pastikan direktori-direktori penting ada
    @classmethod
    def ensure_directories_exist(cls):
        """
        Membuat direktori-direktori penting jika belum ada
        """
        dirs_to_create = [
            cls.DATABASE_PATH,
            cls.OUTPUT_PATH,
            cls.MODELS_PATH,
            cls.NOTEBOOKS_PATH,
            cls.APP_PATH,
            cls.CONFIG_PATH,
            cls.UTILS_PATH,
            cls.OUTPUT_PATH / "logs"
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_venv_status(cls):
        """
        Memeriksa status virtual environment
        """
        status = {
            'venv_exists': cls.VENV_PATH.exists(),
            'activate_script_exists': cls.ACTIVATE_SCRIPT.exists(),
            'python_executable_exists': cls.PYTHON_EXECUTABLE.exists(),
            'project_root': str(cls.PROJECT_ROOT),
            'using_venv': hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
            )
        }
        
        return status

# Fungsi utilitas untuk aktivasi environment
def check_and_setup_environment():
    """
    Memeriksa dan menyiapkan environment jika diperlukan
    """
    config = VenvConfig()
    config.ensure_directories_exist()
    
    status = config.get_venv_status()
    
    if not status['venv_exists']:
        print(f"Warning: Virtual environment tidak ditemukan di {config.VENV_PATH}")
        print("Jalankan: python -m venv .venv atau ./install_deps.sh")
    elif not status['activate_script_exists']:
        print(f"Warning: Skrip aktivasi tidak ditemukan di {config.ACTIVATE_SCRIPT}")
    elif not status['python_executable_exists']:
        print(f"Warning: Eksekutor Python tidak ditemukan di {config.PYTHON_EXECUTABLE}")
    
    return status

if __name__ == "__main__":
    # Jika file ini dijalankan langsung, tampilkan status environment
    status = check_and_setup_environment()
    print("Status Virtual Environment:")
    for key, value in status.items():
        print(f"  {key}: {value}")