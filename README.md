# HLS Converter

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A **professional-grade HLS (HTTP Live Streaming) converter** with automatic optimization, hardware acceleration support, and dynamic bitrate adjustment. Convert any video file into adaptive bitrate HLS streams with just one command.

![HLS Converter Demo](https://via.placeholder.com/800x400/0066cc/white?text=HLS+Converter+Demo)

## ✨ Key Features

### 🚀 **Automatic Optimization**
- **Dynamic bitrate adjustment** based on input video resolution and quality
- **Hardware encoder detection** (VideoToolbox, NVENC, QuickSync, VAAPI, AMF)
- **Intelligent resolution ladder** generation for optimal streaming experience
- **Multi-threaded processing** utilizing all available CPU cores

### 🎬 **Professional Quality**
- **Adaptive bitrate streaming** with multiple quality levels
- **Audio track preservation** with language detection
- **Subtitle conversion** to WebVTT format
- **Optimized encoding settings** for streaming performance

### 🛠️ **Developer Friendly**
- **Class-based architecture** for easy integration
- **Comprehensive CLI** with extensive options
- **Rich console logging** with progress tracking
- **JSON configuration support**
- **Programmatic API** for custom workflows

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install hls-converter

# Or install from source
git clone https://github.com/your-username/hls-converter.git
cd hls-converter
pip install -e .
```

### Basic Usage

```bash
# Convert video with automatic optimization
hls-converter input.mp4

# Specify output directory
hls-converter input.mp4 --output /path/to/output

# Choose specific resolutions
hls-converter input.mp4 --resolutions 720p,1080p,1440p

# Use custom encoding preset
hls-converter input.mp4 --preset fast --crf 20
```

### Python API

```python
from hls_converter import HLSConverter

# Basic conversion
converter = HLSConverter()
results = converter.convert('input.mp4', 'output_directory')

# With custom configuration
from hls_converter import HLSConfig

config = HLSConfig(
    segment_duration=4,
    preset='medium',
    max_workers=6
)
converter = HLSConverter(config)
results = converter.convert('input.mp4', 'output_directory', ['720p', '1080p'])
```

## 📋 Requirements

### System Requirements
- **Python 3.8+**
- **FFmpeg 4.0+** with desired encoders installed
- **FFprobe** (usually comes with FFmpeg)

### Hardware Acceleration Support
The converter automatically detects and uses available hardware encoders:

| Platform | Supported Encoders |
|----------|-------------------|
| **macOS** | VideoToolbox (h264_videotoolbox), AudioToolbox (aac_at) |
| **Windows** | NVIDIA NVENC (h264_nvenc), Intel QuickSync (h264_qsv), AMD AMF (h264_amf) |
| **Linux** | NVIDIA NVENC, Intel VAAPI (h264_vaapi), AMD VAAPI |

## 🎛️ CLI Reference

### Basic Commands

```bash
# Show version
hls-converter --version

# Get help
hls-converter --help

# List available encoders
hls-converter --list-encoders

# Analyze video without conversion
hls-converter input.mp4 --analyze-only
```

### Quality & Resolution Options

```bash
# Specify resolutions (auto-detected if not provided)
hls-converter input.mp4 --resolutions 144p,360p,720p,1080p

# Encoding quality presets
hls-converter input.mp4 --preset fast        # Faster encoding
hls-converter input.mp4 --preset slow        # Better quality

# Custom CRF for software encoding (0-51, lower = better quality)
hls-converter input.mp4 --crf 18
```

### Performance Options

```bash
# Control parallel workers
hls-converter input.mp4 --workers 4

# Segment duration (seconds)
hls-converter input.mp4 --segment-duration 2

# GOP size for better seeking
hls-converter input.mp4 --gop-size 60
```

### Advanced Options

```bash
# Skip subtitle conversion
hls-converter input.mp4 --no-subtitles

# Include bitmap subtitles (usually skipped)
hls-converter input.mp4 --include-bitmap-subtitles

# Use configuration file
hls-converter input.mp4 --config config.json

# Save current settings to config file
hls-converter input.mp4 --save-config my-config.json

# Debug mode
hls-converter input.mp4 --debug

# Quiet mode
hls-converter input.mp4 --quiet
```

## ⚙️ Configuration

### JSON Configuration

Create a `config.json` file for reusable settings:

```json
{
  \"segment_duration\": 2,
  \"playlist_type\": \"vod\",
  \"gop_size\": 48,
  \"max_workers\": 4,
  \"preset\": \"fast\",
  \"crf\": 23,
  \"convert_subtitles\": true,
  \"skip_bitmap_subtitles\": true,
  \"bitrate_profiles\": [
    {
      \"name\": \"720p\",
      \"resolution\": [1280, 720],
      \"max_bitrate_kbps\": 2500,
      \"min_bitrate_kbps\": 1800,
      \"audio_bitrate_kbps\": 160
    },
    {
      \"name\": \"1080p\",
      \"resolution\": [1920, 1080],
      \"max_bitrate_kbps\": 5000,
      \"min_bitrate_kbps\": 3500,
      \"audio_bitrate_kbps\": 160
    }
  ]
}
```

Use the configuration:

```bash
hls-converter input.mp4 --config config.json
```

### Programmatic Configuration

```python
from hls_converter import HLSConfig, BitrateProfile

# Create custom bitrate profiles
profiles = [
    BitrateProfile(\"480p\", (854, 480), 1200, 900),
    BitrateProfile(\"720p\", (1280, 720), 2500, 1800),
    BitrateProfile(\"1080p\", (1920, 1080), 5000, 3500),
]

# Configure converter
config = HLSConfig(
    segment_duration=4,
    preset='medium',
    gop_size=60,
    bitrate_profiles=profiles
)
```

## 🎯 Dynamic Bitrate Adjustment

The converter automatically adjusts bitrates based on input video characteristics:

### Resolution-Based Adjustment
- **4K videos**: Generates full resolution ladder (144p → 2160p)
- **1080p videos**: Caps at 1080p, optimizes bitrates accordingly
- **720p videos**: Focuses on mobile-friendly resolutions

### Bitrate-Based Adjustment
- Analyzes input video bitrate
- Adjusts output bitrates to prevent quality loss
- Maintains proper bitrate ratios across resolutions

### Example Automatic Adjustments

| Input | Auto-Generated Resolutions | Bitrate Adjustments |
|-------|---------------------------|-------------------|
| **4K @ 20Mbps** | 480p, 720p, 1080p, 1440p, 2160p | Full bitrate range |
| **1080p @ 8Mbps** | 360p, 480p, 720p, 1080p | Reduced max bitrates |
| **720p @ 3Mbps** | 240p, 360p, 480p, 720p | Mobile-optimized |

## 📁 Output Structure

The converter generates a complete HLS package:

```
output_directory/
├── master.m3u8              # Master playlist
├── 720p/
│   ├── playlist.m3u8        # 720p video playlist
│   ├── chunk_000.ts
│   ├── chunk_001.ts
│   └── ...
├── 1080p/
│   ├── playlist.m3u8        # 1080p video playlist  
│   ├── chunk_000.ts
│   └── ...
├── audio_english/
│   ├── playlist.m3u8        # English audio playlist
│   ├── chunk_000.ts
│   └── ...
├── audio_spanish/           # Additional audio tracks
│   └── ...
├── english.vtt              # Subtitle files
├── spanish.vtt
└── ...
```

## 🔧 API Reference

### HLSConverter Class

```python
class HLSConverter:
    def __init__(self, config: Optional[HLSConfig] = None)
    
    def convert(self, input_file: str | Path, output_dir: str | Path, 
                resolutions: Optional[List[str]] = None) -> Dict[str, Any]
```

### HLSConfig Class

```python
@dataclass
class HLSConfig:
    segment_duration: int = 2
    playlist_type: str = \"vod\"
    gop_size: int = 48
    max_workers: Optional[int] = None
    preset: str = \"fast\"
    crf: int = 23
    convert_subtitles: bool = True
    skip_bitmap_subtitles: bool = True
    bitrate_profiles: List[BitrateProfile] = field(default_factory=list)
    
    @classmethod
    def create_adaptive_profiles(cls, input_width: int, input_height: int, 
                               input_bitrate: Optional[int] = None) -> List[BitrateProfile]
```

### MediaAnalyzer Class

```python
class MediaAnalyzer:
    def analyze(self, input_file: Path) -> MediaInfo
    def get_optimal_resolutions(self, video_info: VideoInfo) -> List[str]
```

### EncoderDetector Class

```python
class EncoderDetector:
    def detect_encoders(self, force_refresh: bool = False) -> Dict[str, Dict]
    def get_best_video_encoder(self) -> Tuple[str, str]
    def get_best_audio_encoder(self) -> Tuple[str, str]
```

## 🎬 Usage Examples

### Web Streaming Setup

```python
# Convert for web streaming with multiple qualities
from hls_converter import HLSConverter, HLSConfig

config = HLSConfig(
    segment_duration=6,  # Longer segments for better compression
    preset='slow',       # Better quality for web
    convert_subtitles=True
)

converter = HLSConverter(config)
results = converter.convert(
    'movie.mp4', 
    'web_output',
    ['360p', '720p', '1080p']  # Common web resolutions
)

print(f\"Streaming ready: {results['master_playlist']}\")
```

### Mobile-Optimized Conversion

```python
# Optimize for mobile devices
config = HLSConfig(
    segment_duration=2,   # Shorter segments for mobile
    preset='fast',        # Faster processing
    gop_size=30          # Smaller GOP for better seeking
)

converter = HLSConverter(config)
results = converter.convert(
    'video.mp4', 
    'mobile_output',
    ['240p', '360p', '480p', '720p']  # Mobile-friendly resolutions
)
```

### Batch Processing

```python
import os
from pathlib import Path

def batch_convert(input_dir: str, output_base: str):
    converter = HLSConverter()
    
    for video_file in Path(input_dir).glob('*.mp4'):
        output_dir = Path(output_base) / video_file.stem
        
        print(f\"Converting {video_file.name}...\")
        results = converter.convert(video_file, output_dir)
        
        if results['success']:
            print(f\"✅ Completed: {results['master_playlist']}\")
        else:
            print(f\"❌ Failed: {video_file.name}\")

# Convert all MP4 files in directory
batch_convert('/path/to/videos', '/path/to/hls_output')
```

### Custom Bitrate Profiles

```python
from hls_converter import HLSConfig, BitrateProfile

# Create custom profiles for specific use case
profiles = [
    BitrateProfile(\"low\", (640, 360), 800, 600),      # Low bandwidth
    BitrateProfile(\"med\", (1280, 720), 2000, 1500),   # Medium bandwidth  
    BitrateProfile(\"high\", (1920, 1080), 4000, 3000), # High bandwidth
]

config = HLSConfig(bitrate_profiles=profiles)
converter = HLSConverter(config)

results = converter.convert('input.mp4', 'custom_output')
```

## 🔍 Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Install FFmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**Hardware encoder not available**
```bash
# Check available encoders
hls-converter --list-encoders

# The converter will automatically fall back to software encoding
```

**Out of memory errors**
```bash
# Reduce parallel workers
hls-converter input.mp4 --workers 2

# Use faster preset to reduce memory usage
hls-converter input.mp4 --preset ultrafast
```

**Slow conversion**
```bash
# Use hardware encoding (auto-detected)
hls-converter --list-encoders  # Check if hardware encoders are available

# Use faster preset
hls-converter input.mp4 --preset ultrafast

# Reduce number of resolutions
hls-converter input.mp4 --resolutions 720p,1080p
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
hls-converter input.mp4 --debug
```

This will show:
- FFmpeg commands being executed
- Detailed encoder detection process
- Step-by-step conversion progress
- Error stack traces

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/hls-converter.git
cd hls-converter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install in development mode
pip install -e \".[dev]\"

# Run tests
pytest

# Format code
black hls_converter/
isort hls_converter/

# Type checking
mypy hls_converter/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FFmpeg project** for the powerful multimedia framework
- **Rich library** for beautiful console output
- **Python community** for excellent tooling and libraries

---

**Made with ❤️ for the streaming community**

*Star this project on GitHub if you find it useful!*