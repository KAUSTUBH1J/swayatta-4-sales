#!/usr/bin/env python3
"""
Run the Sales-enabled FastAPI server
"""

import uvicorn
import os
from pathlib import Path

# Set up the Python path
import sys
sys.path.append(str(Path(__file__).parent))

# Import the main app
from app.main import app

if __name__ == "__main__":
    print("Starting FastAPI server with Sales module...")
    print("Server will be available at: http://localhost:8001")
    print("API docs available at: http://localhost:8001/docs")
    print("Sales endpoints:")
    print("  - GET/POST /api/v1/sales/companies")
    print("  - GET/POST /api/v1/sales/contacts")
    print("")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )