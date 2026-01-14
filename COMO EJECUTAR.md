# 🚀 Cómo Ejecutar el Proyecto

## Requisitos

- **Python 3.11+**
- **Node.js 18+**

---

## Backend (Servidor)

```powershell
cd Servidor

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

**URL:** http://localhost:8080/docs

---

## Frontend (Vue)

En otra terminal:

```powershell
cd Vue-Front

# Instalar dependencias (solo primera vez)
npm install

# Ejecutar
npm run dev
```

**URL:** http://localhost:5173

---

## Resumen Rápido

| Terminal | Comando |
|----------|---------|
| Backend | `cd Servidor && .\venv\Scripts\Activate.ps1 && python -m uvicorn app.main:app --port 8080 --reload` |
| Frontend | `cd Vue-Front && npm run dev` |
