FROM python:3.11-slim

# Setăm directorul de lucru
WORKDIR /app

# Copiem fișierul de cerințe și instalăm pachetele
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiem restul codului sursă
COPY . .

# Expunem portul 8000 pe care rulează FastAPI
EXPOSE 8000

# Comanda de pornire a serverului
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]