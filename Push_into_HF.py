from datasets import Dataset, Audio
import os
import glob
import config
from huggingface_hub import login

# HuggingFace login
try:
    login(config.HUGGUINGFACE_TOKEN)
except Exception as e:
    print(f"Warning: Could not login to HuggingFace: {e}")


def create_and_push_dataset():
    """Create dataset from audio chunks and push to HuggingFace"""
    print("\n" + "="*60)
    print("STEP 5: CONVERTING TO PARQUET & PUSHING TO HF")
    print("="*60 + "\n")
    
    chunks_dir = config.AUDIO_CHUNKS_FOLDER
    
    # Find all audio files
    audio_files = glob.glob(os.path.join(chunks_dir, "*.wav"))
    
    if not audio_files:
        print("No audio chunks found!")
        return False
    
    print(f"Found {len(audio_files)} audio chunk(s)\n")
    print("Building dataset...")
    
    data = []
    missing_transcripts = 0
    
    for audio_path in sorted(audio_files):
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        
        text_path = os.path.join(chunks_dir, f"{base_name}.txt")
        cohere_path = os.path.join(chunks_dir, f"{base_name}_cohere.txt")
        
        # Read texts
        try:
            with open(text_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
        except FileNotFoundError:
            print(f"  Warning: YouTube transcript not found for {base_name}")
            text = ""
            missing_transcripts += 1
        
        try:
            with open(cohere_path, "r", encoding="utf-8") as f:
                cohere_text = f.read().strip()
        except FileNotFoundError:
            print(f"  Warning: Cohere transcript not found for {base_name}")
            cohere_text = ""
            missing_transcripts += 1
        
        if not text and not cohere_text:
            print(f"  Skipping {base_name} (no transcripts)")
            continue
        
        data.append({
            "audio": audio_path,
            "text": text,
            "cohere_text": cohere_text
        })
    
    if not data:
        print("No valid data found to create dataset!")
        return False
    
    print(f"Creating dataset with {len(data)} sample(s)...")
    
    # Create dataset
    dataset = Dataset.from_list(data)
    
    # Cast audio column
    dataset = dataset.cast_column("audio", Audio())
    
    print(f"Dataset info:")
    print(f"  Samples: {len(dataset)}")
    print(f"  Columns: {dataset.column_names}")
    print(dataset)
    
    # Save to parquet
    print(f"\nSaving to parquet: {config.PARQUET_OUTPUT_FILE}")
    os.makedirs(os.path.dirname(config.PARQUET_OUTPUT_FILE), exist_ok=True)
    dataset.to_parquet(config.PARQUET_OUTPUT_FILE)
    print("✓ Parquet saved")
    
    # Push to HuggingFace
    print(f"\nPushing to HuggingFace ({config.HF_DATASET_NAME})...")
    try:
        dataset.push_to_hub(
            config.HF_DATASET_NAME,
            private=config.HF_PRIVATE
        )
        print("✓ Pushed to HuggingFace Hub")
    except Exception as e:
        print(f"Warning: Could not push to HF: {e}")
    
    print(f"\n{'='*60}")
    print(f"Dataset conversion complete!")
    print(f"  Total samples: {len(data)}")
    print(f"  Missing transcripts: {missing_transcripts}")
    print(f"{'='*60}\n")
    
    return True


# Main execution
if __name__ == "__main__":
    create_and_push_dataset()