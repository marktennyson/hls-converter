# HLS Converter

<div align="center">

![HLS Converter Logo](https://via.placeholder.com/300x100/6366f1/white?text=HLS+Converter)

**Professional HLS (HTTP Live Streaming) converter with automatic optimization**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://hls-converter.readthedocs.io/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

## What is HLS Converter?

HLS Converter is a **professional-grade tool** for converting video files into HLS (HTTP Live Streaming) format with automatic optimization, hardware acceleration support, and dynamic bitrate adjustment. It transforms any video file into adaptive bitrate streams perfect for web streaming, mobile apps, and content delivery networks.

!!! tip "Key Benefits"
    - **🚀 Automatic optimization** - No manual bitrate calculations needed
    - **⚡ Hardware acceleration** - Uses VideoToolbox, NVENC, QuickSync when available  
    - **🎯 Intelligent quality** - Dynamic bitrate adjustment based on input video
    - **🔧 Developer friendly** - Clean Python API and comprehensive CLI

## Quick Example

=== "CLI"

    ```bash
    # Convert video with automatic optimization
    hls-converter input.mp4
    
    # Specify quality levels and output directory
    hls-converter input.mp4 --resolutions 720p,1080p --output ./streaming
    
    # List available hardware encoders
    hls-converter --list-encoders
    ```

=== "Python API"

    ```python
    from hls_converter import HLSConverter
    
    # Basic conversion
    converter = HLSConverter()
    results = converter.convert('input.mp4', 'output_directory')
    
    print(f"✅ Conversion completed!")
    print(f"📋 Master playlist: {results['master_playlist']}")
    print(f"⚡ Processing speed: {results['processing_speed_mbps']:.2f} MB/s")
    ```

=== "Configuration"

    ```python
    from hls_converter import HLSConverter, HLSConfig
    
    # Custom configuration
    config = HLSConfig(
        segment_duration=4,      # 4-second segments
        preset='medium',         # Better quality
        max_workers=6,          # Parallel processing
        convert_subtitles=True  # Include subtitles
    )
    
    converter = HLSConverter(config)
    results = converter.convert('movie.mp4', 'streaming_output', ['720p', '1080p'])
    ```

## Key Features

### 🎬 **Professional Quality**

- **Adaptive bitrate streaming** with multiple quality levels
- **Dynamic bitrate adjustment** based on input video characteristics  
- **Intelligent resolution ladder** generation for optimal streaming
- **Audio track preservation** with language detection
- **Subtitle conversion** to WebVTT format

### 🚀 **High Performance**

- **Hardware encoder detection** (VideoToolbox, NVENC, QuickSync, VAAPI, AMF)
- **Multi-threaded processing** utilizing all CPU cores
- **Optimized FFmpeg parameters** for streaming performance
- **Memory-efficient processing** for large video files
- **Progress tracking** with ETA calculation

### 🛠️ **Developer Experience**

- **Clean class-based architecture** for easy integration
- **Comprehensive CLI** with 20+ options and detailed help
- **Rich console logging** with beautiful progress bars  
- **JSON configuration** support for reproducible builds
- **Extensive documentation** and examples

### 🌐 **Cross-Platform**

- **Python 3.8+** support across platforms
- **macOS, Windows, Linux** compatibility
- **Hardware acceleration** on all major platforms
- **FFmpeg integration** with automatic encoder detection

## Output Structure

HLS Converter generates a complete streaming package:

```
output_directory/
├── master.m3u8              # Master playlist (entry point)
├── 720p/
│   ├── playlist.m3u8        # 720p video playlist
│   ├── chunk_000.ts         # Video segments
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
├── audio_spanish/           # Additional language tracks
│   └── ...
├── english.vtt              # Subtitle files
├── spanish.vtt
└── ...
```

## Why Choose HLS Converter?

| Feature | HLS Converter | Other Tools |
|---------|---------------|-------------|
| **Automatic Optimization** | ✅ Dynamic bitrate adjustment | ❌ Manual configuration required |
| **Hardware Acceleration** | ✅ Auto-detection & fallback | ⚠️ Manual setup needed |
| **Developer API** | ✅ Clean Python classes | ❌ Command-line only |
| **Progress Tracking** | ✅ Rich console with ETA | ❌ Basic or no feedback |
| **Multi-threading** | ✅ Parallel processing | ⚠️ Single-threaded |
| **Documentation** | ✅ Comprehensive docs | ❌ Minimal documentation |
| **Configuration** | ✅ JSON + CLI options | ❌ Limited options |
| **Subtitle Support** | ✅ WebVTT conversion | ⚠️ Basic or missing |

## Real-World Use Cases

!!! example "Web Streaming Platform"
    Convert user uploads to multiple quality levels for adaptive streaming:
    ```python
    converter = HLSConverter()
    results = converter.convert(
        'user_upload.mp4', 
        f'streams/{video_id}',
        ['360p', '720p', '1080p']
    )
    ```

!!! example "Mobile App Backend"
    Optimize videos for mobile consumption with smaller segments:
    ```python
    config = HLSConfig(segment_duration=2, preset='fast')
    converter = HLSConverter(config)
    results = converter.convert('content.mp4', 'mobile_streams')
    ```

!!! example "Batch Processing Pipeline"
    Process multiple videos in a content delivery workflow:
    ```python
    def process_video_queue(video_files):
        converter = HLSConverter()
        for video_file in video_files:
            results = converter.convert(video_file, f'cdn/{video_file.stem}')
            upload_to_cdn(results['master_playlist'])
    ```

## Getting Started

Ready to start converting videos? Choose your path:

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } **Quick Start**

    ---

    Get up and running in 5 minutes with our quick start guide

    [:octicons-arrow-right-24: Quick Start](quickstart.md)

-   :material-download:{ .lg .middle } **Installation**

    ---

    Install HLS Converter via pip or from source

    [:octicons-arrow-right-24: Installation Guide](installation.md)

-   :material-console:{ .lg .middle } **CLI Reference**

    ---

    Explore all command-line options and examples

    [:octicons-arrow-right-24: CLI Documentation](cli.md)

-   :material-api:{ .lg .middle } **Python API**

    ---

    Integrate HLS conversion into your Python applications

    [:octicons-arrow-right-24: API Reference](api/index.md)

</div>

## Community & Support

- **📖 Documentation**: Comprehensive guides and API reference
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/your-username/hls-converter/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/your-username/hls-converter/discussions)
- **🤝 Contributing**: See our [Contributing Guide](contributing.md)

---

<div align="center">
<small>**Made with ❤️ for the streaming community**</small><br>
<small>*Star this project on [GitHub](https://github.com/your-username/hls-converter) if you find it useful!*</small>
</div>