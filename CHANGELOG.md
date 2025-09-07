# Changelog

All notable changes to HLS Converter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### 🎉 Initial Release

#### Added

**Core Features**
- Professional class-based HLS converter architecture
- Automatic hardware encoder detection (VideoToolbox, NVENC, QuickSync, VAAPI, AMF)
- Dynamic bitrate adjustment based on input video characteristics
- Multi-threaded parallel processing for optimal performance
- Comprehensive media analysis with FFprobe integration

**Encoding & Quality**
- Adaptive bitrate streaming with intelligent resolution ladder generation
- Support for 144p to 2160p (4K) video resolutions
- Automatic bitrate optimization based on input video quality
- Hardware-accelerated encoding with software fallback
- Audio track preservation with language detection
- Subtitle conversion to WebVTT format

**CLI Interface**
- Professional command-line interface with extensive options
- Encoder detection and listing (`--list-encoders`)
- Media analysis without conversion (`--analyze-only`)
- JSON configuration file support
- Comprehensive help system and usage examples
- Debug and quiet modes for different use cases

**Developer API**
- Clean, well-documented Python API
- Modular architecture with separate components:
  - `HLSConverter`: Main orchestrator class
  - `MediaAnalyzer`: Video/audio/subtitle analysis
  - `EncoderDetector`: Hardware/software encoder detection
  - `HLSConfig`: Configuration management
  - `BitrateProfile`: Quality level definitions
- Rich console logging with progress tracking
- Comprehensive error handling and reporting

**Project Structure**
- Professional open-source project structure
- Setup.py and pyproject.toml for distribution
- MIT license for commercial and personal use
- Comprehensive documentation and examples
- Contributing guidelines and development setup

#### Technical Specifications

**Supported Input Formats**
- MP4, MKV, AVI, MOV, M4V and other FFmpeg-supported formats
- H.264, H.265, VP9, AV1 video codecs
- AAC, MP3, AC3, DTS audio codecs
- SRT, ASS, VTT, PGS, DVD subtitle formats

**Output Format**
- HLS (HTTP Live Streaming) with M3U8 playlists
- MPEG-TS segments with configurable duration
- Multi-bitrate adaptive streaming
- Audio-only tracks with language support
- WebVTT subtitles for text-based tracks

**System Requirements**
- Python 3.8+ 
- FFmpeg 4.0+ with desired encoders
- macOS, Windows, Linux support
- Hardware acceleration support on compatible systems

**Performance Features**
- Automatic CPU core detection and optimization
- Configurable parallel worker threads
- Memory-efficient processing for large files
- Hardware acceleration detection and utilization
- Progress tracking and ETA calculation

#### Examples

**Basic CLI Usage**
```bash
# Convert with automatic settings
hls-converter input.mp4

# Specify quality levels
hls-converter input.mp4 --resolutions 720p,1080p,1440p

# Use hardware acceleration (auto-detected)
hls-converter input.mp4 --preset fast --workers 6
```

**Python API Usage**
```python
from hls_converter import HLSConverter, HLSConfig

# Basic conversion
converter = HLSConverter()
results = converter.convert('input.mp4', 'output_dir')

# Custom configuration
config = HLSConfig(segment_duration=4, preset='medium')
converter = HLSConverter(config)
results = converter.convert('input.mp4', 'output_dir', ['720p', '1080p'])
```

#### Architecture Improvements

**Compared to Legacy Version**
- ✅ **Class-based architecture** vs. procedural functions
- ✅ **Dynamic bitrate adjustment** vs. hardcoded bitrates  
- ✅ **Modular components** vs. monolithic script
- ✅ **Professional CLI** vs. basic argument parsing
- ✅ **Comprehensive testing** vs. no test coverage
- ✅ **Package distribution** vs. single script file
- ✅ **Rich documentation** vs. minimal comments
- ✅ **Error handling** vs. basic exception catching

**Performance Improvements**
- 🚀 **Parallel processing** of video renditions
- 🚀 **Hardware acceleration** detection and usage
- 🚀 **Optimized FFmpeg parameters** for streaming
- 🚀 **Memory-efficient** subtitle processing
- 🚀 **Progress tracking** with ETA calculation

#### Known Limitations

- Bitmap subtitle formats (PGS, DVD) require manual OCR
- Some hardware encoders may not be available on all systems
- Very large files (>50GB) may require increased memory
- Network storage may impact processing speed

#### Migration from Legacy Version

The new version is a complete rewrite with improved architecture:

**Old Usage:**
```bash
python rich_hls.py input.mp4 720p,1080p
```

**New Usage:**
```bash
hls-converter input.mp4 --resolutions 720p,1080p
```

**API Migration:**
```python
# Old: Direct function calls
# New: Object-oriented approach
converter = HLSConverter()
results = converter.convert(input_file, output_dir)
```

See [Migration Guide](docs/migration.md) for detailed instructions.

---

**Full Changelog:** https://github.com/your-username/hls-converter/commits/v1.0.0