import sys
import subprocess
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("installer")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("Python 3.8 or higher is required")
        return False
    return True

def install_dependencies():
    """Install all required dependencies"""
    if not check_python_version():
        return False
    
    required_packages = [
        "nextcord",
        "python-dotenv",
        "python-telegram-bot>=20.0",  # Updated to version 20+ for compatibility with our code
        "httpx"  # Required for direct API calls in our implementation
    ]
    
    logger.info("Installing dependencies...")
    
    for package in required_packages:
        try:
            logger.info(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            logger.error(f"Failed to install {package}")
            return False
    
    logger.info("All dependencies installed successfully!")
    return True

def verify_tokens():
    """Check if tokens are configured"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        logger.warning(f"No {env_file} file found. Creating template...")
        with open(env_file, "w") as f:
            f.write("DISCORD_TOKEN=your_discord_token_here\n")
            f.write("TELEGRAM_TOKEN=your_telegram_token_here\n")
        logger.info(f"{env_file} file created. Please edit it with your actual tokens.")
        return False
    
    logger.info(f"{env_file} file exists. Make sure it contains your tokens.")
    return True

if __name__ == "__main__":
    print("==== Cross-Platform Chat Bot Installer ====")
    print("This script will install all required dependencies.")
    
    if install_dependencies():
        print("\nDependencies installed successfully!")
    else:
        print("\nSome dependencies failed to install. Please check the logs.")
    
    if verify_tokens():
        print("\nToken configuration found.")
    else:
        print("\nPlease edit the .env file with your actual tokens.")
    
    print("\nSetup complete! You can now run the bot with: python main.py")
