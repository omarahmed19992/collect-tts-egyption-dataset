import os
import librosa
import glob
from transformers import AutoProcessor, CohereAsrForConditionalGeneration
from huggingface_hub import login
import config

# Setup environment
os.environ["PATH"] = config.FFMPEG_PATH + ";" + os.environ["PATH"]

# HuggingFace login (replace with your token)
try:
    login(config.HUGGUINGFACE_TOKEN)
except Exception as e:
    print(f"Warning: Could not login to HuggingFace: {e}")

# Load model once
print("\nLoading Cohere ASR model...")
processor = AutoProcessor.from_pretrained("CohereLabs/cohere-transcribe-03-2026")
model = CohereAsrForConditionalGeneration.from_pretrained(
    "CohereLabs/cohere-transcribe-03-2026",
    device_map="auto"
)
print("✓ Model loaded\n")


def clean_transcript(text):
    """Clean and normalize transcript text"""
    if isinstance(text, list):
        text = " ".join(text)
    return " ".join(text.split())


def get_chunk_audio_files(video_id=None):
    pattern = os.path.join(config.AUDIO_CHUNKS_FOLDER, "*.wav")
    if video_id:
        pattern = os.path.join(config.AUDIO_CHUNKS_FOLDER, f"{video_id}_chunk_*.wav")
    return sorted(glob.glob(pattern))


def process_audio_chunks(video_id=None):
    """Process audio chunks with Cohere ASR"""
    print("="*60)
    if video_id:
        print(f"STEP 5: COHERE ASR TRANSCRIPTION for {video_id}")
    else:
        print("STEP 5: COHERE ASR TRANSCRIPTION")
    print("="*60 + "\n")
    
    audio_files = get_chunk_audio_files(video_id)
    
    if not audio_files:
        print("No audio chunks found!")
        return False
    
    print(f"Found {len(audio_files)} audio chunk(s)\n")
    
    processed_count = 0
    for audio_path in audio_files:
        file_name = os.path.basename(audio_path)
        base_name = os.path.splitext(file_name)[0]
        output_txt = os.path.join(config.AUDIO_CHUNKS_FOLDER, f"{base_name}_cohere.txt")
        
        if os.path.exists(output_txt):
            print(f"✓ Skipping {file_name}: Cohere transcript already exists.")
            continue
        
        try:
            print(f"Processing: {file_name}...", end=" ")
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Run inference
            inputs = processor(audio, sampling_rate=16000, return_tensors="pt", language="ar")
            inputs = inputs.to(model.device, dtype=model.dtype)
            
            outputs = model.generate(**inputs, max_new_tokens=256)
            text = processor.decode(outputs, skip_special_tokens=True)
            
            # Clean transcript
            text = clean_transcript(text)
            
            # Save cohere transcript
            with open(output_txt, "w", encoding="utf-8") as f:
                f.write(text)
            
            print(f"✓ Saved")
            processed_count += 1
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            continue
    
    print(f"\n{'='*60}")
    print(f"Processed {processed_count}/{len(audio_files)} chunk(s)")
    print(f"{'='*60}\n")
    
    return processed_count > 0


# Main execution
if __name__ == "__main__":
    process_audio_chunks()