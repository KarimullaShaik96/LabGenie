@echo off
title LabGenie AI - Backend Server
echo Starting LabGenie AI Backend (FastAPI + Uvicorn)...
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause

