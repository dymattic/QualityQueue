# 🎶 QualityQueue

**Elevate your playlists with intelligent merging and high-quality audio preservation.**

---

## 🛠 Features

- **Audio-Based Comparison**: Analyzes the actual audio content instead of relying on metadata to ensure true quality.
- **Intelligent Merging**: Consolidates playlists by prioritizing high-fidelity tracks when resolving duplicates.
- **Dynamic Quality Metrics**:
  - Uses **Dynamic Range** and **Spectral Rolloff** to assess audio fidelity.
- **JSON Caching**: Tracks progress in a JSON file to avoid redundant processing in subsequent runs.
- **Flexible Configuration**:
  - Optional **GPU-accelerated analysis** for faster processing with tools like OpenL3.
  - Customizable JSON storage location.

---

## 🚀 Why QualityQueue?

Managing downloaded playlists from multiple platforms like SoundCloud and Tidal often results in mismatched or low-quality tracks. **QualityQueue** helps organize these local files by intelligently merging them and ensuring the highest-quality versions of your tracks are preserved.

---

## 🎧 Features for Audiophiles and DJs

- Ensures **lossless fidelity** by analyzing the actual audio content, avoiding false positives from misleading metadata.
- Automatically removes mismatched or low-quality duplicates.
- Consolidates local playlists to ensure high audio quality and organization.

---

## 🛑 Prerequisites

### Install Conda
1. Download and install **Miniconda** or **Anaconda**:
   - [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (lightweight).
   - [Anaconda](https://www.anaconda.com/) (full-fledged).

2. Create a new Conda environment:
   ```bash
   conda create --name qualityqueue python=3.12
   ```

3. Activate the environment:
   ```bash
   conda activate qualityqueue
   ```

---

## 🔧 Installation

### 1. Install Dependencies
- Core dependencies:
  ```bash
  conda install numpy librosa
  ```
- For GPU acceleration (optional):
  ```bash
  conda install -c conda-forge openl3 soundfile
  ```

### 2. Clone the Repository
```bash
git clone https://github.com/your-repo/qualityqueue.git
cd qualityqueue
```

### 3. Install QualityQueue
Install the package locally in your Conda environment:
```bash
pip install .
```

---

## 💡 Usage

### Compare Playlists
Analyze and cache results without making any changes:
```bash
qualityqueue /path/to/source /path/to/target -v
```

### Merge Playlists
Intelligently merge source into target, prioritizing high-quality tracks:
```bash
qualityqueue /path/to/source /path/to/target -v --merge
```

### Enable GPU Acceleration
Speed up processing with GPU support:
```bash
qualityqueue /path/to/source /path/to/target -v --merge --gpu
```

### Customize JSON Location
Specify a custom JSON file path:
```bash
qualityqueue /path/to/source /path/to/target -v --merge --json /path/to/custom.json
```

---

## 🛠 Development Setup

1. Activate the Conda environment:
   ```bash
   conda activate qualityqueue
   ```

2. Install development dependencies:
   ```bash
   conda install pytest black flake8
   ```

3. Run tests:
   ```bash
   pytest
   ```

---

## 🤝 Contributing

Contributions are welcome! Fork the repository, create a branch, and submit a pull request. Let’s make **QualityQueue** even better together.

---

## 🎤 About the Creator

Hey there! I’m **DyMattic**, a DJ and software developer with a passion for music and tech. When I’m not rocking the VR rave scene, I’m crafting tools like **QualityQueue** to make life easier for fellow audiophiles and creators.

Check out my mixes on [SoundCloud](https://soundcloud.com/dymatic-music), and catch me at the next VR rave! ✨

---

## 📜 License

This project is licensed under the MIT License.

---
