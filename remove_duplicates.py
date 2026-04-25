import re
import os
import glob
import config

def clean_srt(file_path, output_path):
    """Remove duplicate sentences from SRT file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
        return False

    cleaned_lines = []
    prev_text = ""

    for i in range(len(lines)):
        line = lines[i].strip()

        # skip index and timestamps
        if line.isdigit() or "-->" in line or line == "":
            continue

        text = line

        # normalize spaces
        text_norm = re.sub(r"\s+", " ", text).strip()

        # skip duplicates
        if text_norm == prev_text or text_norm == "":
            continue

        cleaned_lines.append(text_norm)
        prev_text = text_norm

    # write cleaned transcript
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for line in cleaned_lines:
                f.write(line + "\n")
        print(f"✓ Cleaned: {os.path.basename(file_path)} → {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")
        return False


def transcript_input_path(video_id):
    return os.path.join(config.OUTPUT_DIR, f"{video_id}{config.TRANSCRIPT_EXTENSION}")


def transcript_clean_path(video_id):
    return os.path.join(config.OUTPUT_DIR, f"{video_id}_{config.TRANSCRIPT_CLEAN_NAME}")


def process_video_transcript(video_id):
    """Process one video's transcript file and produce a cleaned version."""
    input_path = transcript_input_path(video_id)
    output_path = transcript_clean_path(video_id)

    if not os.path.exists(input_path):
        print(f"✗ Transcript source not found for {video_id}: {input_path}")
        return False

    if os.path.exists(output_path):
        print(f"✓ Skipping transcript cleanup for {video_id}: already exists.")
        return True

    return clean_srt(input_path, output_path)


def process_all_transcripts():
    """Process all SRT files in the output directory"""
    print("\n" + "="*60)
    print("STEP 2: REMOVING DUPLICATE SENTENCES")
    print("="*60 + "\n")
    
    # Find all .ar.srt files
    srt_files = glob.glob(os.path.join(config.OUTPUT_DIR, f"*{config.TRANSCRIPT_EXTENSION}"))
    
    if not srt_files:
        print("No transcript files found!")
        return False
    
    print(f"Found {len(srt_files)} transcript file(s)\n")
    
    processed_count = 0
    for srt_file in srt_files:
        # Extract video ID from filename
        video_id = os.path.basename(srt_file).replace(config.TRANSCRIPT_EXTENSION, "")
        
        # Create output filename
        output_file = os.path.join(config.OUTPUT_DIR, f"{video_id}_{config.TRANSCRIPT_CLEAN_NAME}")
        
        if clean_srt(srt_file, output_file):
            processed_count += 1
    
    print(f"\n{'='*60}")
    print(f"Processed {processed_count}/{len(srt_files)} transcript(s)")
    print(f"{'='*60}\n")
    
    return processed_count > 0


# Main execution
if __name__ == "__main__":
    process_all_transcripts()