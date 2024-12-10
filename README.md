# 🎶 QualityQueue

**Elevate your playlists with intelligent merging and high-quality audio analysis.**

---

## 🛠 Features

- **Audio-Based Comparison**: Analyzes the actual audio content rather than relying solely on metadata.
- **Intelligent Merging**: Prioritizes high-fidelity tracks when merging multiple playlists.
- **Advanced Fingerprinting**:
  - Uses **Dynamic Range**, **Spectral Rolloff**, **Spectral Centroid**, and **Spectral Bandwidth** to create a rich audio fingerprint.
  - Applies a **weighted scoring system** to determine track quality.
- **JSON Caching & Storage**: Caches previously computed fingerprints in `~/.qualityqueue`, minimizing redundant processing and allowing for quick subsequent runs.
- **Graceful Handling**:
  - Safe cancellation with `Ctrl-C`.
  - Detailed logging and error handling to skip problematic files without halting the entire process.
  
---

## 🚀 Why QualityQueue?

When you download playlists from platforms like SoundCloud or Tidal, it's easy to end up with mismatched versions, remixes, and low-quality duplicates. **QualityQueue** helps you tidy your local playlists, ensuring that only the best-quality tracks make the cut.

By analyzing the actual audio content and maintaining a cache for previously processed tracks, QualityQueue is both **accurate** and **efficient**, helping you manage your local music library with ease.

---

## 🎧 Ideal For

- **Audiophiles & DJs** who need consistent high-quality audio across their sets.
- **Music Enthusiasts** aiming to maintain a pristine local library without duplicate or low-quality tracks.
- **Anyone** who manages large, downloaded playlists and values fidelity and organization.

---

## 🛑 Prerequisites

1. **Conda Installation**:  
   Install **Miniconda** or **Anaconda** if you haven't already.
   - [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (lightweight)
   - [Anaconda](https://www.anaconda.com/) (full-fledged data science environment)

2. **Create and Activate Environment**:
   ```bash
   conda create --name qualityqueue python=3.12
   conda activate qualityqueue
   ```

---

## 🔧 Installation

### 1. Core Dependencies
Install core Python libraries with Conda:
```bash
conda install numpy librosa
```

*(Optional)* If you plan to potentially add GPU or other audio features in the future, you can explore additional packages like `soundfile` via:
```bash
conda install -c conda-forge soundfile
```

### 2. Clone the Repository
```bash
git clone https://github.com/your-repo/qualityqueue.git
cd qualityqueue
```

### 3. Install QualityQueue
Install QualityQueue into your Conda environment:
```bash
pip install .
```

---

## 💡 Usage

**Basic Comparison** (no changes made, just analysis and caching):
```bash
qualityqueue /path/to/source /path/to/target -v
```

**Merging Playlists** (prioritize higher-quality tracks from source to target):
```bash
qualityqueue /path/to/source /path/to/target -v --merge
```

**Customize JSON Location** (if you don't want to use `~/.qualityqueue`):
```bash
qualityqueue /path/to/source /path/to/target -v --merge --json /path/to/custom.json
```

### Additional Flags
- `-v` for verbose output (detailed logging).
- `-w` to specify the number of worker processes for parallel processing:
  ```bash
  qualityqueue /source /target -v -w 8
  ```
  This can speed up analysis on multi-core machines.

---

## 🛠 Development Setup

1. Activate your Conda environment:
   ```bash
   conda activate qualityqueue
   ```

2. Install development dependencies:
   ```bash
   conda install pytest black flake8
   ```

3. Run Tests:
   ```bash
   pytest
   ```

4. Code Formatting and Linting:
   ```bash
   black .
   flake8 .
   ```

---

## 🤝 Contributing

Contributions, feature requests, and bug reports are welcome!  
- **Fork** the repository  
- **Create a branch** for your feature or fix  
- **Submit a Pull Request**

We’ll review and merge changes to improve QualityQueue for everyone.

---

## 🎤 About the Creator

I’m **DyMattic**, a DJ and software developer with a keen interest in music tech. I created QualityQueue to help fellow audiophiles and DJs maintain top-notch local libraries. Check out my mixes on [SoundCloud](https://soundcloud.com/dymattic-music) and join the next VR rave!

---

## 📜 License

**QualityQueue** is licensed under the MIT License, making it free and open-source for personal and commercial use.

---

**Enjoy maintaining your music library with QualityQueue!**