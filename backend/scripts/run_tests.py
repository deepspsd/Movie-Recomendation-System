#!/usr/bin/env python3
"""
Test runner script for Movie Recommendation System
"""

import subprocess
import sys
import os
from pathlib import Path

def run_backend_tests():
    """Run backend tests"""
    print("🧪 Running backend tests...")
    
    backend_path = Path(__file__).parent.parent
    
    # Change to backend directory
    os.chdir(backend_path)
    
    # Run pytest with coverage
    result = subprocess.run([
        "python", "-m", "pytest", 
        "tests/", 
        "-v", 
        "--cov=.", 
        "--cov-report=html",
        "--cov-report=term"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_frontend_tests():
    """Run frontend tests"""
    print("🧪 Running frontend tests...")
    
    frontend_path = Path(__file__).parent.parent.parent / "frontend"
    
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Change to frontend directory
    os.chdir(frontend_path)
    
    # Run npm test
    result = subprocess.run(["npm", "test", "--", "--coverage"], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_linting():
    """Run code linting"""
    print("🔍 Running code linting...")
    
    backend_path = Path(__file__).parent.parent
    
    # Backend linting
    os.chdir(backend_path)
    
    # Run black
    print("Running Black formatter...")
    subprocess.run(["python", "-m", "black", ".", "--check"], capture_output=True)
    
    # Run flake8
    print("Running Flake8 linter...")
    subprocess.run(["python", "-m", "flake8", "."], capture_output=True)
    
    # Run mypy
    print("Running MyPy type checker...")
    subprocess.run(["python", "-m", "mypy", "."], capture_output=True)
    
    print("✅ Linting completed")

def main():
    """Main test runner"""
    print("🚀 Starting comprehensive test suite...")
    
    success = True
    
    # Run backend tests
    if not run_backend_tests():
        success = False
    
    # Run frontend tests
    if not run_frontend_tests():
        success = False
    
    # Run linting
    run_linting()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
