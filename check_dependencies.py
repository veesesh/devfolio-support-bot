#!/usr/bin/env python3
"""
Dependency checker script to verify all required packages are installed
and working correctly before running the RAG bot.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Requires Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_package_import(package_name, import_name=None):
    """Check if a package can be imported"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name} - {str(e)}")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    required_keys = ['OPENAI_API_KEY']
    optional_keys = ['TELEGRAM_BOT_TOKEN', 'DISCORD_BOT_TOKEN']
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    missing_required = []
    missing_optional = []
    
    for key in required_keys:
        if key not in content or f"{key}=your_" in content:
            missing_required.append(key)
    
    for key in optional_keys:
        if key not in content or f"{key}=your_" in content:
            missing_optional.append(key)
    
    if missing_required:
        print(f"❌ .env missing required keys: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"⚠️  .env missing optional keys: {', '.join(missing_optional)}")
    
    print("✅ .env file configured")
    return True

def check_vector_database():
    """Check if vector database exists"""
    db_path = Path("chroma_docs")
    if not db_path.exists():
        print("⚠️  Vector database not found. Run: python create_docs_database.py")
        return False
    print("✅ Vector database exists")
    return True

def main():
    """Run all checks"""
    print("🔍 Checking RAG Bot Dependencies...\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Vector Database", check_vector_database),
    ]
    
    # Package checks
    packages = [
        ("langchain", "langchain"),
        ("langchain-openai", "langchain_openai"),
        ("langchain-community", "langchain_community"),
        ("OpenAI", "openai"),
        ("ChromaDB", "chromadb"),
        ("Python Telegram Bot", "telegram"),
        ("Discord.py", "discord"),
        ("Python dotenv", "dotenv"),
        ("Unstructured", "unstructured"),
    ]
    
    print("📦 Package Dependencies:")
    package_results = []
    for name, import_name in packages:
        result = check_package_import(name, import_name)
        package_results.append(result)
    
    print(f"\n🔧 Environment Checks:")
    env_results = []
    for name, check_func in checks:
        result = check_func()
        env_results.append(result)
    
    # Summary
    total_packages = len(packages)
    working_packages = sum(package_results)
    total_env = len(checks)
    working_env = sum(env_results)
    
    print(f"\n📊 Summary:")
    print(f"   Packages: {working_packages}/{total_packages} working")
    print(f"   Environment: {working_env}/{total_env} ready")
    
    if working_packages == total_packages and working_env == total_env:
        print("\n🎉 All checks passed! Ready to run the RAG bot.")
        return True
    else:
        print("\n⚠️  Some issues found. Please fix them before running the bot.")
        print("\n💡 Quick fixes:")
        if working_packages < total_packages:
            print("   - Install missing packages: pip install -r requirements.txt")
        if not any([check_env_file()]):
            print("   - Create/update .env file with your API keys")
        if not any([check_vector_database()]):
            print("   - Create vector database: python create_docs_database.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
