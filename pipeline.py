"""
Main automation pipeline for collecting and processing audio datasets from YouTube
Pipeline steps:
1. Download audios + transcripts from YouTube
2. Remove duplicate sentences
3. Use CTC aligner to chunk audios (5-15 seconds)
4. Use Cohere ASR to add transcripts
5. Convert to parquet and push to HuggingFace Hub
"""

import sys
import time
import re
import os
import glob
import importlib
from datetime import datetime
import config

print(f"""
╔═════════════════════════════════════════════════════════════════════════════════════╗
║       Collecting Egyption Text-Audio DATASET AUTOMATION PIPELINE v1.0               ║
║  From YouTube to HuggingFace Hub in 6 Easy Steps                                    ║
╚═════════════════════════════════════════════════════════════════════════════════════╝

Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
URLs to process: {len(config.URLs)}
""")

# Show URLs
for i, url in enumerate(config.URLs, 1):
    print(f"  {i}. {url}")

print(f"\nSettings:")
print(f"  Min chunk duration: {config.MIN_CHUNK_DURATION}s")
print(f"  Max chunk duration: {config.MAX_CHUNK_DURATION}s")
print(f"  Output directory: {config.OUTPUT_DIR}")
print(f"  Chunks directory: {config.AUDIO_CHUNKS_FOLDER}")
print(f"\n{'='*60}\n")


def run_step(step_num, step_name, module_name):
    """Run a pipeline step"""
    print(f"\n{'='*60}")
    print(f"RUNNING STEP {step_num}: {step_name}")
    print(f"{'='*60}\n")
    
    try:
        module = __import__(module_name)
        
        # Call the main function if it has one
        if hasattr(module, 'process_all_downloads'):
            result = module.process_all_downloads()
        elif hasattr(module, 'process_all_transcripts'):
            result = module.process_all_transcripts()
        elif hasattr(module, 'process_all_audios'):
            result = module.process_all_audios()
        elif hasattr(module, 'process_all_alignments'):
            result = module.process_all_alignments()
        elif hasattr(module, 'process_audio_chunks'):
            result = module.process_audio_chunks()
        elif hasattr(module, 'create_and_push_dataset'):
            result = module.create_and_push_dataset()
        else:
            print(f"Warning: No processing function found in {module_name}")
            result = False
        
        if result:
            print(f"✓ Step {step_num} completed successfully")
            return True
        else:
            print(f"✗ Step {step_num} had issues")
            return False
            
    except Exception as e:
        print(f"✗ Error in step {step_num}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def get_video_id(url):
    match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)', url)
    return match.group(1) if match else None


def audio_path(video_id):
    return os.path.join(config.OUTPUT_DIR, f"{video_id}{config.AUDIO_EXTENSION}")


def transcript_path(video_id):
    return os.path.join(config.OUTPUT_DIR, f"{video_id}{config.TRANSCRIPT_EXTENSION}")


def clean_transcript_path(video_id):
    return os.path.join(config.OUTPUT_DIR, f"{video_id}_{config.TRANSCRIPT_CLEAN_NAME}")


def alignment_json_path(video_id):
    return os.path.join(config.OUTPUT_DIR, f"{video_id}_{config.AUDIO_CHUNK_DURATIONS_FILE}")


def chunk_files(video_id):
    return sorted(glob.glob(os.path.join(config.AUDIO_CHUNKS_FOLDER, f"{video_id}_chunk_*.wav")))


def is_downloaded(video_id):
    return os.path.exists(audio_path(video_id)) and os.path.exists(transcript_path(video_id))


def is_cleaned(video_id):
    return os.path.exists(clean_transcript_path(video_id))


def is_aligned(video_id):
    return os.path.exists(alignment_json_path(video_id))


def is_chunked(video_id):
    return len(chunk_files(video_id)) > 0


def is_cohere_done(video_id):
    files = chunk_files(video_id)
    if not files:
        return False
    for wav_file in files:
        base_name = os.path.splitext(os.path.basename(wav_file))[0]
        cohere_path = os.path.join(config.AUDIO_CHUNKS_FOLDER, f"{base_name}_cohere.txt")
        if not os.path.exists(cohere_path):
            return False
    return True


def print_video_status(video_id):
    print(f"\nVideo: {video_id}")
    print(f"  Downloaded: {'yes' if is_downloaded(video_id) else 'no'}")
    print(f"  Cleaned: {'yes' if is_cleaned(video_id) else 'no'}")
    print(f"  Aligned: {'yes' if is_aligned(video_id) else 'no'}")
    print(f"  Chunked: {'yes' if is_chunked(video_id) else 'no'}")
    print(f"  Cohere: {'yes' if is_cohere_done(video_id) else 'no'}")


def process_video(url):
    video_id = get_video_id(url)
    if not video_id:
        print(f"✗ Could not extract video ID from URL: {url}")
        return False

    print_video_status(video_id)

    if is_downloaded(video_id) and is_cleaned(video_id) and is_aligned(video_id) and is_chunked(video_id) and is_cohere_done(video_id):
        print(f"✓ {video_id} already completed. Skipping this link.")
        return True

    download_module = importlib.import_module("download_audios_transcript_yt")
    remove_module = importlib.import_module("remove_duplicates")
    aligner_module = importlib.import_module("ctc_aligner")
    splitter_module = importlib.import_module("split_audios")
    cohere_module = importlib.import_module("cohere_asr")

    if not is_downloaded(video_id):
        print(f"\nStarting download for {video_id}")
        if not download_module.download_audio_and_transcript(url, video_id):
            print(f"✗ Download failed for {video_id}. Skipping remaining steps.")
            return False

    if not is_cleaned(video_id):
        print(f"\nStarting transcript cleanup for {video_id}")
        if not remove_module.process_video_transcript(video_id):
            print(f"✗ Transcript cleanup failed for {video_id}. Skipping remaining steps.")
            return False

    if not is_aligned(video_id):
        print(f"\nStarting CTC alignment for {video_id}")
        if not aligner_module.process_video_alignment(video_id):
            print(f"✗ CTC alignment failed for {video_id}. Skipping remaining steps.")
            return False

    if not is_chunked(video_id):
        print(f"\nStarting chunk generation for {video_id}")
        if not splitter_module.process_video_chunks(video_id):
            print(f"✗ Chunk generation failed for {video_id}. Skipping remaining steps.")
            return False

    if not is_cohere_done(video_id):
        print(f"\nStarting Cohere ASR for {video_id}")
        if not cohere_module.process_audio_chunks(video_id):
            print(f"✗ Cohere ASR failed for {video_id}.")
            return False

    print(f"\n✓ {video_id} finished all required stages.")
    return True


def main():
    """Execute the full pipeline per URL, resuming where paused."""
    total_urls = len(config.URLs)
    completed = 0
    failed = 0
    
    for url in config.URLs:
        print(f"\n{'='*60}")
        print(f"PROCESSING URL: {url}")
        print(f"{'='*60}")
        if process_video(url):
            completed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"PIPELINE RESULT")
    print(f"{'='*60}")
    print(f"Total URLs: {total_urls}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"{'='*60}\n")

    print("Running final dataset export step...")
    push_module = importlib.import_module("Push_into_HF")
    push_module.create_and_push_dataset()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)