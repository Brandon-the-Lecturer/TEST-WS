# Basisimage mit Python 3.12 und Streamlit
FROM python:3.12-slim

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere requirements.txt und installiere die Abhängigkeiten
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Projekts in das Arbeitsverzeichnis
COPY src /app/src

# Exponiere den Port, auf dem Streamlit läuft (Standard ist 8501)
EXPOSE 8501

# Befehl zum Starten der Streamlit-Anwendung
CMD ["streamlit", "run", "src/app.py"]
