#!/bin/bash

# Start FastAPI on 0.0.0.0 so the container network can route to it
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0