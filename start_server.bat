@echo off
title VNR VJIET - Industrial Truck Failure Prediction Server
echo =====================================================================
echo  VNR VJIET | Industrial Truck Predictive Maintenance AI Server
echo =====================================================================
echo.
echo Starting FastAPI & LightGBM Machine Learning Localhost Server...
echo Root URL:       http://localhost:8000
echo Swagger Docs:   http://localhost:8000/docs
echo.
python server.py
pause

