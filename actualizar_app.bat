@echo off
cd "C:\Users\Usuario\OneDrive\Documentos\River\2025\Proyectos\driblab-app"

echo ============================
echo   Subiendo cambios a GitHub
echo ============================

git add .
git commit -m "Actualizo datos o código"
git push origin main

echo.
echo ✅ Cambios subidos correctamente. Esperá unos segundos y Streamlit actualizará la app.
pause
