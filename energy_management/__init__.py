from . import models
import os
import subprocess

# Funzione per installare automaticamente le dipendenze
def install_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_file):
        try:
            subprocess.check_call(['pip', 'install', '-r', requirements_file])
        except Exception as e:
            raise ImportError(f"Errore durante l'installazione delle dipendenze: {str(e)}")

# Esegui l'installazione
install_requirements()
