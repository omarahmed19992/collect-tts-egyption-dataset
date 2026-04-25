# Multiple YouTube URLs to download
URLs = [
    "https://www.youtube.com/watch?v=2QPdPBk51B4",
    "https://www.youtube.com/watch?v=3SDH0qZ4ykU",
    "https://www.youtube.com/watch?v=dU8hTbYdfMc",
    "https://www.youtube.com/watch?v=cKn9AsIACd0"
    # Add more URLs here
]

# Base output directories
OUTPUT_DIR = r"downloaded_audio_and_transcript"
PROCESSED_DIR = r"processed_data"

FFMPEG_PATH = r"C:\ffmpeg-8.1-full_build\bin" # write ` where ffmpeg ` in terminal to find the path

YTDLP_PATH = r"C:\Users\xxx\xxx\enxxs\xx\yt-dlp.exe"  # write ` where yt-dlp ` in terminal to find the path

HUGGUINGFACE_TOKEN = "your_token_here" # create a token from https://huggingface.co/settings/tokens and paste it here

# Naming conventions (will use video_id for each download)
TRANSCRIPT_EXTENSION = ".ar.srt"
TRANSCRIPT_CLEAN_NAME = "clean_transcript.txt"
TRANSCRIPT_COHERE_NAME = "cohere_transcript.txt"
AUDIO_EXTENSION = ".wav"
AUDIO_CHUNK_DURATIONS_FILE = "audio_chunks.json"

# Chunk settings
MIN_CHUNK_DURATION = 5  # seconds
MAX_CHUNK_DURATION = 15  # seconds
AUDIO_CHUNKS_FOLDER = OUTPUT_DIR + "\\" + "chunks"

# Parquet output
PARQUET_OUTPUT_FILE = r"Collect_Dataset\dataset.parquet"

# HuggingFace settings
HF_DATASET_NAME = "Omar111/tts-egyption-dataset" # Choose a unique name for your dataset in the format "username/dataset-name"
HF_PRIVATE = False # Set to True if you want the dataset to be private, False for public