import subprocess
import os
import re 
import glob
import config
from pathlib import Path

# Set up environment
os.environ["PATH"] = config.FFMPEG_PATH + ";" + os.environ["PATH"]
os.makedirs(config.OUTPUT_DIR, exist_ok=True)
os.makedirs(config.AUDIO_CHUNKS_FOLDER, exist_ok=True)

output_template = os.path.join(config.OUTPUT_DIR, "%(id)s.%(ext)s")

def video_id_from_url(url):
    match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)', url)
    return match.group(1) if match else None


def download_audio_and_transcript(url, video_id=None):
    """Download audio and transcript for a single YouTube URL"""
    
    print(f"\n{'='*60}")
    print(f"Downloading: {url}")
    print(f"{'='*60}\n")
    
    # Get video ID if not provided
    if not video_id:
        video_id = video_id_from_url(url)
        if not video_id:
            print(f"Could not extract video ID from {url}")
            return False
    
    audio_path = os.path.join(config.OUTPUT_DIR, f"{video_id}{config.AUDIO_EXTENSION}")
    transcript_path = os.path.join(config.OUTPUT_DIR, f"{video_id}{config.TRANSCRIPT_EXTENSION}")

    if os.path.exists(audio_path) and os.path.exists(transcript_path):
        print(f"✓ Skipping {video_id}: audio and transcript already exist.")
        return True

    # Download audio if missing
    if not os.path.exists(audio_path):
        print(f"[Step 1/2] Downloading audio for {video_id}...")
        audio_cmd = [
            config.YTDLP_PATH,
            "-f", "bestaudio/best",
            "-x",
            "--audio-format", "wav",
            "-o", output_template,
            url
        ]
        result = subprocess.run(audio_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error downloading audio: {result.stderr}")
            return False
        print(f"✓ Audio downloaded as {video_id}{config.AUDIO_EXTENSION}")
    else:
        print(f"✓ Audio already exists for {video_id}")

    # Download transcript if missing
    if not os.path.exists(transcript_path):
        print(f"[Step 2/2] Downloading Arabic transcript for {video_id}...")
        subs_cmd = [
            config.YTDLP_PATH,
            "--skip-download",
            "--write-auto-subs",
            "--write-subs",
            "--sub-langs", "ar",
            "--convert-subs", "srt",
            "-o", output_template,
            url
        ]
        result = subprocess.run(subs_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: Could not download transcript: {result.stderr}")
            # Keep going if audio already exists
            return os.path.exists(audio_path)
        print(f"✓ Transcript downloaded as {video_id}{config.TRANSCRIPT_EXTENSION}")
    else:
        print(f"✓ Transcript already exists for {video_id}")

    return True


def process_all_downloads():
    """Download audio and transcript for all configured URLs."""
    print("\n" + "="*60)
    print("STARTING YOUTUBE DOWNLOAD PIPELINE")
    print(f"Total URLs to process: {len(config.URLs)}")
    print("="*60)
    
    successful = 0
    failed = 0
    
    for url in config.URLs:
        if download_audio_and_transcript(url):
            successful += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"DOWNLOAD COMPLETE")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"{'='*60}\n")
    
    # List downloaded files
    print("Downloaded files:")
    for file in sorted(os.listdir(config.OUTPUT_DIR)):
        file_path = os.path.join(config.OUTPUT_DIR, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path) / (1024*1024)  # MB
            print(f"  - {file} ({size:.2f} MB)")
    
    return failed == 0


# Main execution
if __name__ == "__main__":
    process_all_downloads()
