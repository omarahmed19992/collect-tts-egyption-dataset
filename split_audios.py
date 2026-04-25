import json
import os
import glob
from pydub import AudioSegment
import config

os.makedirs(config.AUDIO_CHUNKS_FOLDER, exist_ok=True)

MIN_DURATION = config.MIN_CHUNK_DURATION   # seconds
MAX_DURATION = config.MAX_CHUNK_DURATION   # seconds


def split_audio_by_timestamps(audio_path, json_path, video_id):
    """
    Split audio into chunks based on word timestamps from JSON
    """
    print(f"\nProcessing: {video_id}")
    print("-" * 40)
    
    try:
        # Load audio
        print(f"  Loading audio...")
        audio = AudioSegment.from_wav(audio_path)
        
        # Load JSON with word timestamps
        print(f"  Loading timestamps...")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        words = data.get("words", [])
        
        if not words:
            print(f"  ✗ No word timestamps found!")
            return 0
        
        # Create chunks
        chunks = []
        current_chunk = []
        chunk_start = None
        
        for word in words:
            start = word.get("start", 0)
            end = word.get("end", 0)
            text = word.get("char", word.get("text", ""))
            
            if chunk_start is None:
                chunk_start = start
            
            current_chunk.append(word)
            duration = end - chunk_start
            
            # Check if chunk is ready
            if duration >= MIN_DURATION:
                if duration <= MAX_DURATION:
                    chunks.append(current_chunk)
                    current_chunk = []
                    chunk_start = None
                else:
                    # Exceeded max duration - save and start new
                    last_word = current_chunk.pop()
                    chunks.append(current_chunk)
                    
                    current_chunk = [last_word]
                    chunk_start = last_word.get("start", 0)
        
        # Don't forget last chunk
        if current_chunk:
            duration = current_chunk[-1].get("end", 0) - chunk_start
            if duration >= MIN_DURATION:
                chunks.append(current_chunk)
        
        if not chunks:
            print(f"  ✗ No valid chunks created!")
            return 0
        
        # Save chunks
        print(f"  Saving {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks):
            start_ms = int(chunk[0].get("start", 0) * 1000)
            end_ms = int(chunk[-1].get("end", 0) * 1000)
            
            # Extract audio chunk
            audio_chunk = audio[start_ms:end_ms]
            
            # Extract text
            text = " ".join([w.get("char", w.get("text", "")) for w in chunk])
            
            # Save audio
            chunk_name = f"{video_id}_chunk_{i}"
            audio_path_chunk = os.path.join(config.AUDIO_CHUNKS_FOLDER, f"{chunk_name}.wav")
            audio_chunk.export(audio_path_chunk, format="wav")
            
            # Save text
            text_path_chunk = os.path.join(config.AUDIO_CHUNKS_FOLDER, f"{chunk_name}.txt")
            with open(text_path_chunk, "w", encoding="utf-8") as f:
                f.write(text)
        
        print(f"  ✓ Created {len(chunks)} chunks")
        return len(chunks)
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return 0


def video_chunk_files(video_id):
    return glob.glob(os.path.join(config.AUDIO_CHUNKS_FOLDER, f"{video_id}_chunk_*.wav"))


def process_video_chunks(video_id):
    json_path = os.path.join(config.OUTPUT_DIR, f"{video_id}_{config.AUDIO_CHUNK_DURATIONS_FILE}")
    audio_path = os.path.join(config.OUTPUT_DIR, f"{video_id}{config.AUDIO_EXTENSION}")
    chunk_files = video_chunk_files(video_id)

    if not os.path.exists(json_path):
        print(f"✗ Alignment JSON missing for {video_id}: {json_path}")
        return False

    if not os.path.exists(audio_path):
        print(f"✗ Audio file missing for {video_id}: {audio_path}")
        return False

    if chunk_files:
        valid_chunks = 0
        for wav_path in chunk_files:
            base_name = os.path.splitext(os.path.basename(wav_path))[0]
            txt_path = os.path.join(config.AUDIO_CHUNKS_FOLDER, f"{base_name}.txt")
            if os.path.exists(txt_path):
                valid_chunks += 1
        if valid_chunks == len(chunk_files):
            print(f"✓ Skipping chunking for {video_id}: {len(chunk_files)} complete chunk(s) already exist.")
            return True
        print(f"⚠️  Partial chunk data found for {video_id}. Regenerating chunks.")

    chunks_created = split_audio_by_timestamps(audio_path, json_path, video_id)
    return chunks_created > 0


def process_all_alignments():
    """Process all JSON alignment files"""
    print("\n" + "="*60)
    print("STEP 4: AUDIO CHUNKING WITH PYDUB")
    print("="*60)
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(config.OUTPUT_DIR, f"*_{config.AUDIO_CHUNK_DURATIONS_FILE}"))
    
    if not json_files:
        print("No alignment JSON files found!")
        return False
    
    print(f"Found {len(json_files)} alignment file(s)\n")
    
    total_chunks = 0
    for json_file in sorted(json_files):
        # Extract video ID from filename
        basename = os.path.basename(json_file)
        video_id = basename.replace(f"_{config.AUDIO_CHUNK_DURATIONS_FILE}", "")
        
        # Find corresponding audio file
        audio_file = os.path.join(config.OUTPUT_DIR, f"{video_id}{config.AUDIO_EXTENSION}")
        
        if not os.path.exists(audio_file):
            print(f"✗ Audio file not found for {video_id}")
            continue
        
        chunks = split_audio_by_timestamps(audio_file, json_file, video_id)
        total_chunks += chunks
    
    print(f"\n{'='*60}")
    print(f"Total chunks created: {total_chunks}")
    print(f"{'='*60}\n")
    
    return total_chunks > 0


# Main execution
if __name__ == "__main__":
    process_all_alignments()