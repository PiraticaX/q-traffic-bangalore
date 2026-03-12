#!/bin/bash

# Export the project root to PYTHONPATH so `backend` can be resolved
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start Streamlit directly. 
# We've embedded the quantum math into the app so we don't need a separate background server!
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
