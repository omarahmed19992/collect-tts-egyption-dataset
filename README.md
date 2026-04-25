# Collecting Egption Text-Audio Dataset Automation Pipeline

Automated pipeline for downloading YouTube videos, processing audio, and creating datasets for TTS models.

## 🎯 Pipeline Overview

The pipeline automates the following 6 steps:

```
1. Download Audios & Transcripts
   ├─ Downloads audio from YouTube URLs
   ├─ Auto-extracts video IDs for naming
   └─ Downloads Arabic subtitles/transcripts

2. Remove Duplicate Sentences
   ├─ Cleans SRT transcript files
   ├─ Removes duplicate sentences
   └─ Normalizes whitespace

3. CTC Alignment & Timestamps
   ├─ Uses CTC forced aligner
   ├─ Generates word-level timestamps
   └─ Creates JSON alignment files

4. Audio Chunking with Pydub
   ├─ Reads alignment JSON files
   ├─ Splits audio into 5-15 second chunks
   └─ Aligns text to audio chunks

5. Cohere ASR Transcription
   ├─ Runs Cohere ASR model on chunks
   ├─ Creates alternative transcriptions
   └─ Improves transcript quality

6. Parquet Conversion & HF Push
   ├─ Converts dataset to Parquet format
   ├─ Pushes to HuggingFace Hub
   └─ Creates shareable dataset
```

## 🚀 Quick Start

### Prerequisites

1. **Install required packages:**
```bash
pip install torch librosa soundfile transformers datasets yt-dlp scikit-learn
```

2. **Update configuration:**
   - Edit `config_example.py` and add your YouTube URLs 
   - Update HuggingFace token
   - Set your desired chunk durations
   - Rename it into `config.py`

3. **Verify dependencies:**
   - FFmpeg installed and in PATH
   - yt-dlp executable path correct
   - CUDA available (or will use CPU, but slower)

### Running the Pipeline

**Option 1: Run full pipeline (recommended)**
```bash
python pipeline.py
```

**Option 2: Run individual steps**
```bash
# Step 1: Download
python download_audios_transcript_yt.py

# Step 2: Clean transcripts
python remove_duplicates.py

# Step 3: CTC alignment
python ctc_aligner.py

# Step 4: Audio chunking
python split_audios.py

# Step 5: Cohere ASR
python cohere_asr.py

# Step 6: Push to Hub
python Push_into_HF.py
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Add multiple YouTube URLs
URLs = [
    "https://www.youtube.com/watch?v=VIDEO_ID_1",
    "https://www.youtube.com/watch?v=VIDEO_ID_2",
    # Add more URLs
]

# Chunk duration settings (in seconds)
MIN_CHUNK_DURATION = 5
MAX_CHUNK_DURATION = 15

# HuggingFace settings
HF_DATASET_NAME = "your-username/dataset-name"
HF_PRIVATE = True  # or False for public datasets
```

## 📁 Directory Structure

```
Collect_Dataset/
├── config.py                          # Configuration file
├── pipeline.py                        # Main orchestration script
├── download_audios_transcript_yt.py  # Step 1: Download
├── remove_duplicates.py              # Step 2: Clean
├── ctc_aligner.py                    # Step 3: Alignment
├── split_audios.py                   # Step 4: Chunking
├── cohere_asr.py                     # Step 5: ASR
├── Push_into_HF.py                   # Step 6: Export
├── downloaded_audio_and_transcript/   # Raw downloads
│   ├── VIDEO_ID_1.wav
│   ├── VIDEO_ID_1.ar.srt
│   ├── VIDEO_ID_1_clean_transcript.txt
│   ├── VIDEO_ID_1_audio_chunks.json
│   ├── VIDEO_ID_2.wav
│   └── VIDEO_ID_2.ar.srt
├── processed_data/
│   └── chunks/
│       ├── VIDEO_ID_1_chunk_0.wav
│       ├── VIDEO_ID_1_chunk_0.txt
│       ├── VIDEO_ID_1_chunk_0_cohere.txt
│       └── ...
└── dataset.parquet                   # Final output
```

## 🔄 Detailed Workflow

### Step 1: Download
- Extracts video ID from YouTube URL
- Downloads best quality audio as WAV
- Downloads Arabic subtitles as SRT
- Supports multiple URLs in loop

**Input:** YouTube URLs  
**Output:** `VIDEO_ID.wav`, `VIDEO_ID.ar.srt`

### Step 2: Remove Duplicates
- Parses SRT files
- Removes duplicate consecutive sentences
- Normalizes whitespace
- Creates clean transcript files

**Input:** `VIDEO_ID.ar.srt`  
**Output:** `VIDEO_ID_clean_transcript.txt`

### Step 3: CTC Alignment
- Loads CTC forced aligner model
- Generates frame-level emissions
- Aligns text to audio timing
- Creates JSON with word-level timestamps

**Input:** Audio + clean transcript  
**Output:** `VIDEO_ID_audio_chunks.json`

### Step 4: Audio Chunking
- Reads JSON alignment files
- Uses pydub to split audio precisely
- Creates chunks between 5-15 seconds
- Based on word boundaries

**Input:** Audio + JSON timestamps  
**Output:** `VIDEO_ID_chunk_N.wav`, `VIDEO_ID_chunk_N.txt`

### Step 5: Cohere ASR
- Runs Cohere ASR model on each chunk
- Generates alternative transcriptions
- Useful for comparing with YouTube subtitles
- Improves transcript quality

**Input:** Audio chunks  
**Output:** `VIDEO_ID_chunk_N_cohere.txt`

### Step 6: Export to HF
- Creates Dataset from all chunks
- Includes audio, text, and cohere_text columns
- Converts to Parquet format
- Pushes to HuggingFace Hub

**Input:** All chunks and transcripts  
**Output:** `dataset.parquet`, pushed to Hub

## 📊 Dataset Format

Final dataset includes:

```
{
  "audio": {
    "path": "path/to/audio.wav",
    "array": [...],
    "sampling_rate": 16000
  },
  "text": "YouTube transcript",
  "cohere_text": "Cohere ASR transcript"
}
```

## ⚠️ Tips & Troubleshooting

### Performance Optimization
- Use CUDA for faster CTC alignment: install `torch` with CUDA support
- Adjust `batch_size` in `config.py` for memory constraints
- Process videos in parallel (modify pipeline.py)

### Common Issues

**"Model not found" error:**
- First run downloads 5GB+ of models
- Ensure good internet connection
- Models cached locally after first download

**"ffmpeg not found":**
- Update FFmpeg path in `config.py`
- Or install globally: `choco install ffmpeg` (Windows)

**No Arabic subtitles available:**
- Script falls back to auto-generated subtitles
- Some videos may use different languages
- Manually provide transcripts if needed

## 📝 Notes

- Video IDs are automatically extracted and used for file naming
- Processing time: ~5-15 minutes per video (depends on duration and CUDA)
- Dataset size: ~100-300MB for 1 hour of audio
- All temperatures and settings optimized for Arabic

## Limitation
- If there no diarization for multiple speakers (as podcast for example) 
- you will need trim silence from audios

## 🙏 Acknowledgements

This project makes use of the forced alignment model and Cohere ASR model provided by:

- [MahmoudAshraf/mms-300m-1130-forced-aligner](https://huggingface.co/MahmoudAshraf/mms-300m-1130-forced-aligner)
- [Cohere ASR](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) 

---
