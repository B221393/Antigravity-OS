@echo off
title Hatetris Machine Learning Training (Genetic Algorithm)
echo ===========================================
echo Starting Hatetris ML Engine (Genetic Algorithm)
echo ===========================================
echo Press Ctrl+C to stop training manually. The best weights are saved progressively.
echo.

python train_ml.py

echo.
echo Training complete. Press any key to exit.
pause > nul
