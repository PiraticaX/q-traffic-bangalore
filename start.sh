#!/bin/bash

# 1. Start the FastAPI backend in the background (runs locally inside the container)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# 2. Start the Streamlit frontend in the foreground (exposes to the public web)
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0