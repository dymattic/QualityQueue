import argparse
import json
import logging
import os
import shutil
import signal
from concurrent.futures import ProcessPoolExecutor, as_completed

import librosa
import numpy as np

DEFAULT_JSON_DIR = os.path.expanduser("~/.qualityqueue")
CACHE_FILE = os.path.join(DEFAULT_JSON_DIR, "fingerprints_cache.json")
STOP_SIGNAL = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("qualityqueue")

WEIGHTS = {
    "dynamic_range": 0.4,
    "spectral_rolloff": 0.2,
    "spectral_centroid": 0.2,
    "spectral_bandwidth": 0.2
}

def handle_signal(signal_received, frame):
    global STOP_SIGNAL
    logger.warning("Ctrl-C detected. Safely exiting...")
    STOP_SIGNAL = True

signal.signal(signal.SIGINT, handle_signal)

def ensure_default_dir():
    if not os.path.exists(DEFAULT_JSON_DIR):
        os.makedirs(DEFAULT_JSON_DIR)

def get_json_path(source, target, custom_path=None):
    if custom_path:
        return custom_path
    ensure_default_dir()
    json_name = f"{os.path.basename(source)}_{os.path.basename(target)}.json"
    return os.path.join(DEFAULT_JSON_DIR, json_name)

def load_json(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r') as file:
            return json.load(file)
    return {"matched": {}, "unmatched_target": [], "processed_source": {}}

def save_json(data, json_path):
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_cache():
    ensure_default_dir()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    ensure_default_dir()
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

def file_needs_processing(file_path, cache):
    if file_path in cache:
        cached_mtime = cache[file_path].get("mtime", 0)
        current_mtime = os.path.getmtime(file_path)
        if current_mtime == cached_mtime:
            return False
    return True

def compute_fingerprint(y, sr):
    dynamic_range = float(np.max(y) - np.min(y))
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.90)
    spectral_rolloff = float(np.mean(rolloff))
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_centroid = float(np.mean(centroid))
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    spectral_bandwidth = float(np.mean(bandwidth))
    return dynamic_range, spectral_rolloff, spectral_centroid, spectral_bandwidth

def analyze_audio_content(file_path):
    try:
        y, sr = librosa.load(file_path, sr=44100)
        if y is None or len(y) == 0:
            raise ValueError(f"Empty or invalid audio data in {file_path}")
        return compute_fingerprint(y, sr)
    except Exception as e:
        logger.error(f"Error analyzing audio for {file_path}: {e}")
        return None

def score_fingerprint(fp):
    if fp is None:
        return None
    (dr, ro, sc, sb) = fp
    return (dr * WEIGHTS["dynamic_range"] +
            ro * WEIGHTS["spectral_rolloff"] +
            sc * WEIGHTS["spectral_centroid"] +
            sb * WEIGHTS["spectral_bandwidth"])

def process_file(file_path):
    if STOP_SIGNAL:
        return None
    fp = analyze_audio_content(file_path)
    if fp is None:
        return None
    return {
        "file": file_path,
        "fingerprint": fp,
        "mtime": os.path.getmtime(file_path)
    }

def get_fingerprints(directory, verbose, processed_files, num_workers=4):
    fingerprints = {}
    cache = load_cache()

    file_list = [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.endswith(('.mp3', '.wav')) and filename not in processed_files
    ]

    file_list = [f for f in file_list if file_needs_processing(f, cache)]

    if verbose and file_list:
        logger.info(f"Processing {len(file_list)} files in {directory} with {num_workers} workers.")

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_file = {executor.submit(process_file, file): file for file in file_list}

        for future in as_completed(future_to_file):
            if STOP_SIGNAL:
                break
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result and result["fingerprint"] is not None:
                    fp = result["fingerprint"]
                    score = score_fingerprint(fp)
                    fingerprints[file_path] = fp
                    processed_files[os.path.basename(file_path)] = fp
                    cache[file_path] = {
                        "mtime": result["mtime"],
                        "fingerprint": fp
                    }

                    if verbose:
                        logger.info(f"Processed: {os.path.basename(file_path)} (score={score:.2f})")
                else:
                    logger.warning(f"Skipping file {os.path.basename(file_path)} due to analysis failure.")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")

    # Include cached files that didn't need reprocessing
    for filename in os.listdir(directory):
        if filename.endswith(('.mp3', '.wav')) and filename not in processed_files:
            full_path = os.path.join(directory, filename)
            if full_path in cache:
                fp = cache[full_path].get("fingerprint")
                if fp:
                    fingerprints[full_path] = fp
                    processed_files[filename] = fp

    save_cache(cache)
    return fingerprints

def compare_playlists(source_fingerprints, target_fingerprints, data):
    unmatched_target = set(data["unmatched_target"])
    for source_path, source_fp in source_fingerprints.items():
        matched = False
        for target_path, target_fp in target_fingerprints.items():
            if source_fp == target_fp:
                data["matched"][source_path] = target_path
                unmatched_target.discard(target_path)
                matched = True
                break
        # If not matched, it's a new track to potentially add during merge
    for target_path in target_fingerprints.keys():
        if target_path not in data["matched"].values():
            unmatched_target.add(target_path)
    data["unmatched_target"] = list(unmatched_target)
    return data

def merge_playlists(source_dir, target_dir, data, verbose):
    for track in data["unmatched_target"]:
        if verbose:
            logger.info(f"Deleting unmatched track: {track}")
        try:
            os.remove(track)
        except Exception as e:
            logger.error(f"Could not delete {track}: {e}")

    matched_sources = set(data["matched"].keys())
    for source_path in data["matched"]:
        destination_path = os.path.join(target_dir, os.path.basename(source_path))
        if source_path in matched_sources:
            dest_track = data["matched"][source_path]
            src_fp = analyze_audio_content(source_path)
            dst_fp = analyze_audio_content(dest_track)
            src_score = score_fingerprint(src_fp) if src_fp else -1
            dst_score = score_fingerprint(dst_fp) if dst_fp else -1

            if src_score > dst_score:
                if verbose:
                    logger.info(f"Replacing lower-quality destination track: {dest_track}")
                shutil.copy2(source_path, dest_track)
            else:
                if verbose:
                    logger.info(f"Keeping higher-quality destination track: {dest_track}")
        else:
            if verbose:
                logger.info(f"Copying new track to destination: {destination_path}")
            shutil.copy2(source_path, destination_path)

def main():
    parser = argparse.ArgumentParser(description="QualityQueue - A tool for managing playlists with high fidelity")
    parser.add_argument("source", help="Path to the source playlist directory")
    parser.add_argument("target", help="Path to the target playlist directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-m", "--merge", action="store_true", help="Merge source into target playlist")
    parser.add_argument("-j", "--json", help="Custom path for the JSON file (default: stored in user's home directory)")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Number of worker processes for processing")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")
    else:
        logger.setLevel(logging.INFO)

    if args.verbose:
        logger.info(f"Processing source directory: {args.source}")
        logger.info(f"Processing target directory: {args.target}")
        logger.info(f"Using {args.workers} workers for parallel processing.")

    json_path = get_json_path(args.source, args.target, args.json)

    if args.verbose:
        logger.info(f"Using JSON file: {json_path}")

    data = load_json(json_path)
    source_fingerprints = get_fingerprints(args.source, args.verbose, data["processed_source"], args.workers)
    target_fingerprints = get_fingerprints(args.target, args.verbose, {}, args.workers)

    data = compare_playlists(source_fingerprints, target_fingerprints, data)
    save_json(data, json_path)

    if args.merge:
        if args.verbose:
            logger.info("Merging source into target playlist...")
        merge_playlists(args.source, args.target, data, args.verbose)
        if args.verbose:
            logger.info("Merge completed successfully!")
    else:
        if args.verbose:
            logger.info("Processing completed. No changes were made to the target directory.")

if __name__ == "__main__":
    main()
