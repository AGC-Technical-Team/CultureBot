#!/usr/bin/env python3
import uvicorn
import sys

if __name__ == "__main__":
    print("Starting CultureBot API on http://0.0.0.0:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
