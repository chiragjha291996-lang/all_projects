#!/bin/bash

echo "Starting Health Tracker Application..."
echo "======================================"

# Start the backend server
echo "Starting Flask backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:5002/api/health > /dev/null; then
    echo "✓ Backend server is running on http://localhost:5002"
else
    echo "✗ Backend server failed to start"
    kill $BACKEND_PID
    exit 1
fi

# Open frontend
echo "Opening frontend..."
cd ../frontend
open index.html

echo ""
echo "Health Tracker is now running!"
echo "Frontend: Open in your browser"
echo "Backend API: http://localhost:5002"
echo ""
echo "To stop the backend server, press Ctrl+C or run: kill $BACKEND_PID"

# Keep the script running
wait $BACKEND_PID
