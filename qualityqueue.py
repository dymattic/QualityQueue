import os
import shutil
import json
import argparse
import time
import librosa
import numpy as np

DEFAULT_JSON_DIR = os.path.expanduser("~/.qualityqueue")

def analyze_audio_content(file_path):
    """
    Analyze the audio content of a file to estimate quality.
    Returns a tuple: (dynamic_range, spectral_rolloff)
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        dynamic_range = np.max(y) - np.min(y)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.90)[0].mean()
        return dynamic_range, spectral_rolloff
    except Exception as e:
        print(f"Error analyzing audio for {file_path}: {e}")
        return None, None

def get_json_path(source, target, custom_path=None):
    """
    Determine the JSON storage path.
    """
    if custom_path:
        return custom_path
    if not os.path.exists(DEFAULT_JSON_DIR):
        os.makedirs(DEFAULT_JSON_DIR)
    json_name = f"{os.path.basename(source)}_{os.path.basename(target)}.json"
    return os.path.join(DEFAULT_JSON_DIR, json_name)

def load_json(json_path):
    """
    Load existing JSON data or initialize a new structure.
    """
    if os.path.exists(json_path):
        with open(json_path, 'r') as file:
            return json.load(file)
    return {"matched": {}, "unmatched_target": [], "processed_source": {}}

def save_json(data, json_path):
    """
    Save data to the JSON file.
    """
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_fingerprints(directory, verbose, processed_files):
    """
    Generate fingerprints for all unprocessed audio files in a directory.
    """
    fingerprints = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename not in processed_files and filename.endswith(('.mp3', '.wav')):
            start_time = time.time()
            fingerprint = analyze_audio_content(file_path)  # Using audio content as the "fingerprint"
            duration = time.time() - start_time
            if fingerprint:
                fingerprints[file_path] = fingerprint
                processed_files[filename] = fingerprint
                if verbose:
                    print(f"Fingerprint generated for {filename} in {duration:.2f}s")
    return fingerprints

def compare_playlists(source_fingerprints, target_fingerprints, data):
    """
    Compare fingerprints between source and target directories.
    """
    unmatched_target = set(data["unmatched_target"])  # Retain previously unmatched tracks

    # Identify matches and unmatched tracks
    for source_path, source_fp in source_fingerprints.items():
        for target_path, target_fp in target_fingerprints.items():
            if source_fp == target_fp:
                data["matched"][source_path] = target_path
                unmatched_target.discard(target_path)
                break

    # Add unmatched target tracks
    for target_path in target_fingerprints.keys():
        if target_path not in data["matched"].values():
            unmatched_target.add(target_path)

    # Update unmatched targets in JSON
    data["unmatched_target"] = list(unmatched_target)
    return data

def merge_playlists(source_dir, target_dir, data, verbose):
    """
    Merge source into target, keeping the highest-quality version for matches.
    """
    for track in data["unmatched_target"]:
        if verbose:
            print(f"Deleting unmatched track: {track}")
        os.remove(track)

    matched_sources = set(data["matched"].keys())
    for source_path in source_fingerprints.keys():
        destination_path = os.path.join(target_dir, os.path.basename(source_path))

        if source_path in matched_sources:
            dest_track = data["matched"][source_path]
            src_quality = analyze_audio_content(source_path)
            dst_quality = analyze_audio_content(dest_track)

            if verbose:
                print(f"Comparing audio fidelity: Source={src_quality} Destination={dst_quality}")

            if (
                src_quality > dst_quality or
                dst_quality == (None, None)
            ):
                if verbose:
                    print(f"Replacing lower-fidelity destination track: {dest_track}")
                shutil.copy2(source_path, dest_track)
            else:
                if verbose:
                    print(f"Keeping higher-fidelity destination track: {dest_track}")
        else:
            if verbose:
                print(f"Copying new track to destination: {destination_path}")
            shutil.copy2(source_path, destination_path)

def main():
    parser = argparse.ArgumentParser(description="QualityQueue - A tool for managing playlists with high fidelity")
    parser.add_argument("source", help="Path to the source playlist directory")
    parser.add_argument("target", help="Path to the target playlist directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-m", "--merge", action="store_true", help="Merge source into target playlist")
    parser.add_argument("-j", "--json", help="Custom path for the JSON file (default: stored in user's home directory)")

    args = parser.parse_args()

    if args.verbose:
        print(f"Processing source directory: {args.source}")
        print(f"Processing target directory: {args.target}")

    json_path = get_json_path(args.source, args.target, args.json)

    if args.verbose:
        print(f"Using JSON file: {json_path}")

    data = load_json(json_path)
    source_fingerprints = get_fingerprints(args.source, args.verbose, data["processed_source"])
    target_fingerprints = get_fingerprints(args.target, args.verbose, {})

    data = compare_playlists(source_fingerprints, target_fingerprints, data)
    save_json(data, json_path)

    if args.merge:
        if args.verbose:
            print("\nMerging source into target playlist...")
        merge_playlists(args.source, args.target, data, args.verbose)
        if args.verbose:
            print("Merge completed successfully!")
    else:
        if args.verbose:
            print("\nProcessing completed. No changes were made to the target directory.")

if __name__ == "__main__":
    main()
