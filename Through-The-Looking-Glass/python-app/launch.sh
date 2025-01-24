#!/bin/bash

# Prevent Python from creating __pycache__ directory
export PYTHONDONTWRITEBYTECODE=1

# Trap Ctrl+C (SIGINT) to run the cleanup function
trap cleanup SIGINT

# Start backend.py and frontend.py in the background
python backend.py & backend_pid=$!
python frontend.py & frontend_pid=$!

# Function to handle Ctrl+C and kill the background processes
cleanup() {
    echo "Ctrl+C detected. Stopping both processes..."
    kill $backend_pid $frontend_pid
    wait $backend_pid $frontend_pid
    echo "Both processes stopped."
}

# Wait for both background processes to finish
wait $backend_pid $frontend_pid
