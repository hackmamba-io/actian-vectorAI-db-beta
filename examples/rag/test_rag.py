#!/usr/bin/env python3
############################################################
#
# Copyright (C) 2025-2026 - Actian Corp.
#
############################################################
"""Quick validation test for RAG example.

This script performs automated checks to verify the RAG example
can run successfully.

Usage:
    python examples/rag/test_rag.py
"""

import sys
import subprocess
from typing import Tuple


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_check(name: str, passed: bool, details: str = ""):
    """Print a check result."""
    icon = "✅" if passed else "❌"
    print(f"{icon} {name}")
    if details:
        print(f"   {details}")


def check_docker() -> Tuple[bool, str]:
    """Check if Docker is installed and VectorAI DB is running."""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            if "vectoraidb" in result.stdout.lower():
                return True, "VectorAI DB container is running"
            else:
                return False, "Docker running but VectorAI DB container not found"
        else:
            return False, "Docker command failed"
    except FileNotFoundError:
        return False, "Docker not installed"
    except Exception as e:
        return False, f"Error checking Docker: {str(e)}"


def check_python_version() -> Tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"Python {version.major}.{version.minor} (requires 3.10+)"


def check_dependencies() -> Tuple[bool, str]:
    """Check if required packages are installed."""
    missing = []
    
    try:
        import cortex
    except ImportError:
        missing.append("cortex (actiancortex)")
    
    try:
        import sentence_transformers
    except ImportError:
        missing.append("sentence-transformers")
    
    if missing:
        return False, f"Missing: {', '.join(missing)}"
    else:
        return True, "All required packages installed"


def check_database_connection() -> Tuple[bool, str]:
    """Test connection to VectorAI DB."""
    try:
        from cortex import CortexClient
        
        with CortexClient("localhost:50051") as client:
            version, uptime = client.health_check()
            return True, f"Connected to {version}"
    except ImportError:
        return False, "cortex package not installed"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def main():
    print_header("RAG Example - Pre-flight Checks")
    
    all_passed = True
    
    # Check 1: Python version
    passed, details = check_python_version()
    print_check("Python version (3.10+)", passed, details)
    all_passed = all_passed and passed
    
    # Check 2: Docker and VectorAI DB
    passed, details = check_docker()
    print_check("VectorAI DB running", passed, details)
    if not passed:
        print("   💡 Start with: docker compose up -d")
    all_passed = all_passed and passed
    
    # Check 3: Dependencies
    passed, details = check_dependencies()
    print_check("Python dependencies", passed, details)
    if not passed:
        print("   💡 Install with: pip install -r examples/rag/requirements.txt")
    all_passed = all_passed and passed
    
    # Check 4: Database connection
    if all_passed:  # Only test if previous checks passed
        passed, details = check_database_connection()
        print_check("Database connection", passed, details)
        all_passed = all_passed and passed
    else:
        print("⏭️  Database connection - Skipped (fix previous issues first)")
    
    # Summary
    print_header("Summary")
    
    if all_passed:
        print("✅ All checks passed!")
        print("\n🚀 Ready to run the RAG example:")
        print("   python examples/rag/rag_example.py --local")
    else:
        print("❌ Some checks failed")
        print("\n📋 Follow the suggestions above to fix issues")
        print("\n📖 See examples/rag/VALIDATION.md for detailed troubleshooting")
        sys.exit(1)
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
