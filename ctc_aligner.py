import os
import config
import torch
import json
import glob

os.environ["PATH"] = config.FFMPEG_PATH + ";" + os.environ["PATH"]

from ctc_forced_aligner import (
    load_audio,
    load_alignment_model,
    generate_emissions,
    preprocess_text,
    get_alignments,
    get_spans,
    postprocess_results,
)

# Set up
language = "ara"  # ISO-639-3 Language code
device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 16
print(f"\nUsing device: {device}")

# Create output directories
os.makedirs(config.AUDIO_CHUNKS_FOLDER, exist_ok=True)

# Load model once (reuse for all files)
print("\nLoading CTC alignment model...")
alignment_model, alignment_tokenizer = load_alignment_model(
    device,
    dtype=torch.float16 if device == "cuda" else torch.float32,
)
print("✓ Model loaded\n")


def generate_alignment_json(audio_path, text_path, video_id):
    """
    Generate CTC alignment and word timestamps JSON
    """
    print(f"\nProcessing: {video_id}")
    print("-" * 40)
    
    try:
        # Load audio and transcript
        print(f"  Loading audio...")
        audio_waveform = load_audio(audio_path, alignment_model.dtype, alignment_model.device)
        
        print(f"  Loading transcript...")
        with open(text_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        text = "".join(line for line in lines).replace("\n", " ").strip()
        
        if not text:
            print(f"  ✗ Empty transcript file!")
            return False
        
        # Generate alignments
        print(f"  Generating alignments...")
        emissions, stride = generate_emissions(
            alignment_model, audio_waveform, batch_size=batch_size
        )
        
        tokens_starred, text_starred = preprocess_text(
            text,
            romanize=True,
            language=language,
        )
        
        segments, scores, blank_token = get_alignments(
            emissions,
            tokens_starred,
            alignment_tokenizer,
        )
        
        spans = get_spans(tokens_starred, segments, blank_token)
        word_timestamps = postprocess_results(text_starred, spans, stride, scores)
        
        # Save JSON
        json_file = os.path.join(config.OUTPUT_DIR, f"{video_id}_{config.AUDIO_CHUNK_DURATIONS_FILE}")
        
        data = {
            "audio_file": audio_path,
            "words": word_timestamps
        }
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Alignment saved to {os.path.basename(json_file)}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def alignment_json_path(video_id):
    return os.path.join(config.OUTPUT_DIR, f"{video_id}_{config.AUDIO_CHUNK_DURATIONS_FILE}")


def process_video_alignment(video_id):
    audio_path = os.path.join(config.OUTPUT_DIR, f"{video_id}{config.AUDIO_EXTENSION}")
    transcript_file = os.path.join(config.OUTPUT_DIR, f"{video_id}_{config.TRANSCRIPT_CLEAN_NAME}")
    json_file = alignment_json_path(video_id)

    if not os.path.exists(audio_path):
        print(f"✗ Audio file missing for {video_id}: {audio_path}")
        return False

    if not os.path.exists(transcript_file):
        print(f"✗ Clean transcript missing for {video_id}: {transcript_file}")
        return False

    if os.path.exists(json_file):
        print(f"✓ Skipping CTC alignment for {video_id}: alignment JSON already exists.")
        return True

    return generate_alignment_json(audio_path, transcript_file, video_id)


def process_all_audios():
    """Generate alignments for all audio files"""
    print("\n" + "="*60)
    print("STEP 3: CTC ALIGNMENT & WORD TIMESTAMPS")
    print("="*60)
    
    # Find all .wav files
    audio_files = glob.glob(os.path.join(config.OUTPUT_DIR, f"*{config.AUDIO_EXTENSION}"))
    
    if not audio_files:
        print("No audio files found!")
        return False
    
    print(f"Found {len(audio_files)} audio file(s)")
    
    processed_count = 0
    for audio_file in audio_files:
        # Extract video ID from filename
        video_id = os.path.basename(audio_file).replace(config.AUDIO_EXTENSION, "")
        
        # Find corresponding transcript
        transcript_file = os.path.join(config.OUTPUT_DIR, f"{video_id}_clean_transcript.txt")
        
        if not os.path.exists(transcript_file):
            print(f"\n✗ Transcript not found for {video_id}")
            continue
        
        if generate_alignment_json(audio_file, transcript_file, video_id):
            processed_count += 1
    
    print(f"\n{'='*60}")
    print(f"Alignments generated: {processed_count}/{len(audio_files)}")
    print(f"{'='*60}\n")
    
    return processed_count > 0


# Main execution
if __name__ == "__main__":
    process_all_audios()