@echo off
echo ========================================
echo  Smart Classroom AI - Frontend
echo ========================================
echo.
echo Iniciando servidor HTTP local...
echo.
echo El frontend estara disponible en:
echo http://localhost:8080
echo.
echo IMPORTANTE: Asegurate de que el backend este ejecutandose en http://localhost:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

python -m http.server 8080
