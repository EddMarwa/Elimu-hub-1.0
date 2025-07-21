#!/usr/bin/env python3
"""
Comprehensive setup script for Elimu Hub project.
This script will set up both backend and frontend for development.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    if platform.system() == "Windows":
        # Use PowerShell on Windows
        result = subprocess.run(
            ["powershell", "-Command", command],
            cwd=cwd,
            capture_output=True,
            text=True
        )
    else:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
    
    if result.returncode != 0 and check:
        print(f"Command failed: {command}")
        print(f"Error: {result.stderr}")
        return False
    
    return True

def setup_backend():
    """Set up the backend environment."""
    print("\n🔧 Setting up Backend...")
    
    backend_dir = Path("backend")
    
    # Create virtual environment if it doesn't exist
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        print("Creating virtual environment...")
        run_command("python -m venv .venv")
    
    # Activate virtual environment and install dependencies
    if platform.system() == "Windows":
        pip_path = ".venv/Scripts/pip.exe"
        python_path = ".venv/Scripts/python.exe"
    else:
        pip_path = ".venv/bin/pip"
        python_path = ".venv/bin/python"
    
    print("Installing backend dependencies...")
    requirements_path = backend_dir / "requirements.txt"
    if requirements_path.exists():
        run_command(f"{pip_path} install -r {requirements_path}")
    
    # Create necessary directories
    directories = [
        backend_dir / "data" / "pdfs",
        backend_dir / "data" / "chroma",
        backend_dir / "logs",
        backend_dir / "models"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Copy environment file if it doesn't exist
    env_file = backend_dir / ".env"
    env_example = backend_dir / "env.example"
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        env_content = env_example.read_text()
        env_file.write_text(env_content)
        print("⚠️  Please edit backend/.env with your settings")
    
    print("✅ Backend setup completed")

def setup_frontend():
    """Set up the frontend environment."""
    print("\n🔧 Setting up Frontend...")
    
    frontend_dir = Path("frontend")
    
    # Install Node.js dependencies
    print("Installing frontend dependencies...")
    if not run_command("npm install", cwd=frontend_dir):
        print("❌ Frontend dependency installation failed")
        return False
    
    # Create environment file if it doesn't exist
    env_file = frontend_dir / ".env.local"
    env_example = frontend_dir / ".env.local.example"
    if not env_file.exists() and env_example.exists():
        print("Creating .env.local file from template...")
        env_content = env_example.read_text()
        env_file.write_text(env_content)
        print("⚠️  Please edit frontend/.env.local with your settings")
    
    print("✅ Frontend setup completed")

def setup_database():
    """Set up the database."""
    print("\n🔧 Setting up Database...")
    
    backend_dir = Path("backend")
    
    if platform.system() == "Windows":
        python_path = ".venv/Scripts/python.exe"
    else:
        python_path = ".venv/bin/python"
    
    # Run database migrations
    migration_script = backend_dir / "scripts" / "migrate_db.py"
    if migration_script.exists():
        print("Running database migrations...")
        run_command(f"{python_path} {migration_script}", cwd=backend_dir)
    
    # Create admin user
    admin_script = backend_dir / "scripts" / "create_admin.py"
    if admin_script.exists():
        print("Creating admin user...")
        run_command(f"{python_path} {admin_script}", cwd=backend_dir)
    
    print("✅ Database setup completed")

def download_llm_model():
    """Download LLM model if it doesn't exist."""
    print("\n🔧 Checking LLM Model...")
    
    model_dir = Path("backend/models")
    model_file = model_dir / "mistral-7b.Q4_K_M.gguf"
    
    if not model_file.exists():
        print("❌ LLM model not found")
        print("📝 Please download the model manually:")
        print("   1. Go to: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF")
        print("   2. Download: mistral-7b-instruct-v0.1.Q4_K_M.gguf")
        print(f"   3. Place it at: {model_file}")
        print("   OR use a different model and update the LLM_MODEL_PATH in .env")
    else:
        print("✅ LLM model found")

def main():
    """Main setup function."""
    print("🚀 Elimu Hub Setup Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("README.md").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup components
    setup_backend()
    setup_frontend()
    setup_database()
    download_llm_model()
    
    print("\n🎉 Setup completed!")
    print("\n📝 Next steps:")
    print("1. Edit backend/.env with your configuration")
    print("2. Edit frontend/.env.local with your configuration")
    print("3. Download the LLM model if needed")
    print("4. Start the backend: python backend/start.py")
    print("5. Start the frontend: cd frontend && npm run dev")
    print("\n💡 Visit http://localhost:3000 to see your application")

if __name__ == "__main__":
    main()
