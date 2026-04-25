"""
QUICK START GUIDE for Collecting Text-Audio Egyption Data Pipeline

This script helps you set up and run the pipeline.
"""

import os
import sys
import json
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n" + "="*60)
    print("CHECKING DEPENDENCIES")
    print("="*60 + "\n")
    
    required_packages = [
        ("torch", "PyTorch"),
        ("librosa", "librosa"),
        ("soundfile", "soundfile"),
        ("transformers", "Transformers"),
        ("datasets", "HuggingFace Datasets"),
        ("yt_dlp", "yt-dlp"),
    ]
    
    missing = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages. Install with:")
        print(f"pip install {' '.join(missing)}\n")
        return False
    
    print("\n✓ All dependencies installed")
    return True


def check_config():
    """Check if config.py is properly set up"""
    print("\n" + "="*60)
    print("CHECKING CONFIG")
    print("="*60 + "\n")
    
    try:
        import config
        
        # Check URLs
        if not config.URLs:
            print("✗ No URLs configured in config.py")
            return False
        print(f"✓ {len(config.URLs)} URL(s) configured")
        
        # Check paths
        print(f"✓ Output dir: {config.OUTPUT_DIR}")
        print(f"✓ Chunks dir: {config.AUDIO_CHUNKS_FOLDER}")
        print(f"✓ Parquet output: {config.PARQUET_OUTPUT_FILE}")
        
        # Check chunk settings
        print(f"✓ Min chunk: {config.MIN_CHUNK_DURATION}s")
        print(f"✓ Max chunk: {config.MAX_CHUNK_DURATION}s")
        
        # Check tools
        if os.path.exists(config.FFMPEG_PATH):
            print(f"✓ FFmpeg path exists")
        else:
            print(f"✗ FFmpeg path not found: {config.FFMPEG_PATH}")
            return False
        
        if os.path.exists(config.YTDLP_PATH):
            print(f"✓ yt-dlp path exists")
        else:
            print(f"✗ yt-dlp path not found: {config.YTDLP_PATH}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False


def create_directories():
    """Create required directories"""
    print("\n" + "="*60)
    print("CREATING DIRECTORIES")
    print("="*60 + "\n")
    
    import config
    
    directories = [
        config.OUTPUT_DIR,
        config.AUDIO_CHUNKS_FOLDER,
        os.path.dirname(config.PARQUET_OUTPUT_FILE),
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ {directory}")
    
    print("\n✓ All directories ready")
    return True


def show_urls():
    """Display configured URLs"""
    print("\n" + "="*60)
    print("CONFIGURED YOUTUBE URLs")
    print("="*60 + "\n")
    
    import config
    
    for i, url in enumerate(config.URLs, 1):
        # Extract video ID
        import re
        match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)', url)
        video_id = match.group(1) if match else "UNKNOWN"
        print(f"{i}. [{video_id}] {url}")
    
    return True


def run_pipeline():
    """Run the full pipeline"""
    print("\n" + "="*60)
    print("RUNNING FULL PIPELINE")
    print("="*60 + "\n")
    
    import pipeline
    pipeline.main()


def main():
    """Main menu"""
    print(f"""
╔═════════════════════════════════════════════════════════════════════════════════════╗
║             Collecting Text-Audio Egyption Data Pipeline - SETUP TOOL               ║
╚═════════════════════════════════════════════════════════════════════════════════════╝
""")
    
    while True:
        print(f"""
Menu:
  1. Check dependencies
  2. Check configuration
  3. Create directories
  4. Show URLs
  5. Run full pipeline
  6. Exit

""")
        
        choice = input("Select option (1-6): ").strip()
        
        try:
            if choice == "1":
                check_dependencies()
            elif choice == "2":
                check_config()
            elif choice == "3":
                create_directories()
            elif choice == "4":
                show_urls()
            elif choice == "5":
                run_pipeline()
                break
            elif choice == "6":
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice")
        except KeyboardInterrupt:
            print("\nInterrupted")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
