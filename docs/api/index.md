# API Reference

The HLS Converter Python API provides a clean, object-oriented interface for integrating video conversion into your applications. This section covers all classes, methods, and configuration options.

## Overview

The API is designed around these core concepts:

- **HLSConverter**: Main orchestrator class that handles the conversion process
- **HLSConfig**: Configuration management with bitrate profiles and settings
- **MediaAnalyzer**: Analyzes input video characteristics  
- **EncoderDetector**: Detects available hardware and software encoders

## Quick API Example

```python
from hls_converter import HLSConverter, HLSConfig

# Basic conversion
converter = HLSConverter()
results = converter.convert('input.mp4', 'output_directory')

# Custom configuration
config = HLSConfig(
    segment_duration=4,
    preset='medium',
    max_workers=6
)
converter = HLSConverter(config)
results = converter.convert('input.mp4', 'output_dir', ['720p', '1080p'])
```

## Core Classes

### HLSConverter

::: hls_converter.converter.HLSConverter
    options:
      show_source: false
      members_order: source
      separate_signature: true

**Key Methods:**

- **`convert()`** - Main conversion method
- **`media_analyzer`** - Access to media analysis functionality  
- **`encoder_detector`** - Access to encoder detection

**Example Usage:**
```python
from hls_converter import HLSConverter

converter = HLSConverter()

# Convert with automatic settings
results = converter.convert('movie.mp4', 'hls_output')

# Convert specific resolutions
results = converter.convert('movie.mp4', 'hls_output', ['720p', '1080p'])

# Access conversion results
print(f"Master playlist: {results['master_playlist']}")
print(f"Processing time: {results['total_duration']:.1f}s")
print(f"Speed: {results['processing_speed_mbps']:.2f} MB/s")
```

### HLSConfig

::: hls_converter.config.HLSConfig
    options:
      show_source: false
      members_order: source

**Configuration Options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `segment_duration` | `int` | `2` | HLS segment duration in seconds |
| `playlist_type` | `str` | `"vod"` | HLS playlist type |
| `gop_size` | `int` | `48` | Group of Pictures size |
| `max_workers` | `int` | `None` | Number of parallel workers (auto-detect if None) |
| `preset` | `str` | `"fast"` | Encoding preset |
| `crf` | `int` | `23` | Constant Rate Factor for software encoding |
| `convert_subtitles` | `bool` | `True` | Whether to convert subtitles |
| `skip_bitmap_subtitles` | `bool` | `True` | Skip bitmap subtitle formats |

**Example Usage:**
```python
from hls_converter import HLSConfig

# Create custom configuration
config = HLSConfig(
    segment_duration=6,        # 6-second segments
    preset='medium',           # Better quality
    crf=20,                   # Higher quality
    max_workers=4,            # 4 parallel workers
    convert_subtitles=True    # Include subtitles
)

# Load from JSON file
with open('config.json', 'r') as f:
    config_dict = json.load(f)
config = HLSConfig.from_dict(config_dict)

# Save to JSON file  
config_dict = config.to_dict()
with open('config.json', 'w') as f:
    json.dump(config_dict, f, indent=2)
```

### BitrateProfile

::: hls_converter.config.BitrateProfile
    options:
      show_source: false
      members_order: source

**Creating Custom Profiles:**
```python
from hls_converter.config import BitrateProfile, HLSConfig

# Create custom bitrate profiles
profiles = [
    BitrateProfile("low", (640, 360), 800, 600),      # Low quality
    BitrateProfile("medium", (1280, 720), 2000, 1500), # Medium quality
    BitrateProfile("high", (1920, 1080), 4000, 3000),  # High quality
]

config = HLSConfig(bitrate_profiles=profiles)
```

### MediaAnalyzer

::: hls_converter.media_analyzer.MediaAnalyzer
    options:
      show_source: false
      members_order: source

**Usage Example:**
```python
from hls_converter.media_analyzer import MediaAnalyzer
from pathlib import Path

analyzer = MediaAnalyzer()
media_info = analyzer.analyze(Path('video.mp4'))

# Access video information
if media_info.video:
    print(f"Resolution: {media_info.video.width}x{media_info.video.height}")
    print(f"Duration: {media_info.video.duration:.1f}s")
    print(f"FPS: {media_info.video.fps:.1f}")
    print(f"Bitrate: {media_info.video.bitrate}kbps")

# Access audio tracks
for track in media_info.audio_tracks:
    print(f"Audio: {track.language} ({track.codec})")

# Access subtitle tracks
for track in media_info.subtitle_tracks:
    print(f"Subtitle: {track.language} ({track.codec})")
```

### EncoderDetector

::: hls_converter.encoder_detector.EncoderDetector
    options:
      show_source: false
      members_order: source

**Usage Example:**
```python
from hls_converter.encoder_detector import EncoderDetector

detector = EncoderDetector()
encoder_info = detector.detect_encoders()

# Get best encoders
video_encoder, video_name = detector.get_best_video_encoder()
audio_encoder, audio_name = detector.get_best_audio_encoder()

print(f"Video encoder: {video_name}")
print(f"Audio encoder: {audio_name}")

# Check if hardware encoding is available
is_hardware = detector.is_hardware_encoder(video_encoder)
print(f"Hardware acceleration: {is_hardware}")
```

## Data Classes

### VideoInfo

Information about video streams:

```python
@dataclass
class VideoInfo:
    width: int              # Video width in pixels
    height: int             # Video height in pixels  
    duration: float         # Duration in seconds
    fps: float             # Frames per second
    bitrate: Optional[int]  # Bitrate in kbps
    codec: Optional[str]    # Video codec name
```

### AudioTrack

Information about audio tracks:

```python
@dataclass
class AudioTrack:
    index: int                    # Track index
    language: str                 # Language code
    codec: Optional[str]          # Audio codec
    bitrate: Optional[int]        # Bitrate in kbps
    sample_rate: Optional[int]    # Sample rate in Hz
    channels: Optional[int]       # Number of channels
```

### SubtitleTrack

Information about subtitle tracks:

```python
@dataclass
class SubtitleTrack:
    index: int        # Track index
    language: str     # Language code
    codec: str        # Subtitle codec
```

## Advanced Usage

### Custom Bitrate Profiles

Create profiles based on input video characteristics:

```python
from hls_converter import HLSConfig

# Analyze input video first
converter = HLSConverter()
media_info = converter.media_analyzer.analyze(Path('input.mp4'))

if media_info.video:
    # Create adaptive profiles
    profiles = HLSConfig.create_adaptive_profiles(
        media_info.video.width,
        media_info.video.height,
        media_info.video.bitrate
    )
    
    config = HLSConfig(bitrate_profiles=profiles)
    converter = HLSConverter(config)
```

### Progress Monitoring

Monitor conversion progress with callbacks:

```python
import time
from hls_converter import HLSConverter

def progress_callback(step, progress, eta=None):
    print(f"Step: {step}, Progress: {progress:.1f}%", end="")
    if eta:
        print(f", ETA: {eta}")
    else:
        print()

# Note: Callback support may be added in future versions
converter = HLSConverter()
results = converter.convert('input.mp4', 'output')
```

### Error Handling

Handle conversion errors gracefully:

```python
from hls_converter import HLSConverter
from hls_converter.exceptions import ConversionError, EncoderError

try:
    converter = HLSConverter()
    results = converter.convert('input.mp4', 'output')
    
    if results['success']:
        print(f"✅ Conversion completed: {results['master_playlist']}")
    else:
        print("❌ Conversion failed")
        
except FileNotFoundError:
    print("❌ Input file not found")
except ConversionError as e:
    print(f"❌ Conversion error: {e}")
except EncoderError as e:
    print(f"❌ Encoder error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

### Batch Processing

Process multiple files efficiently:

```python
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from hls_converter import HLSConverter

def convert_video(video_file, output_base):
    converter = HLSConverter()
    output_dir = output_base / video_file.stem
    
    try:
        results = converter.convert(video_file, output_dir)
        return {'file': video_file.name, 'success': True, 'playlist': results['master_playlist']}
    except Exception as e:
        return {'file': video_file.name, 'success': False, 'error': str(e)}

# Process videos in parallel
video_files = list(Path('input_videos').glob('*.mp4'))
output_base = Path('hls_output')

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [
        executor.submit(convert_video, video_file, output_base)
        for video_file in video_files
    ]
    
    for future in futures:
        result = future.result()
        if result['success']:
            print(f"✅ {result['file']}: {result['playlist']}")
        else:
            print(f"❌ {result['file']}: {result['error']}")
```

### Integration with Web Frameworks

#### Flask Integration

```python
from flask import Flask, request, jsonify
from hls_converter import HLSConverter
import uuid

app = Flask(__name__)
converter = HLSConverter()

@app.route('/convert', methods=['POST'])
def convert_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    video_file = request.files['video']
    video_id = str(uuid.uuid4())
    
    # Save uploaded file
    input_path = f'uploads/{video_id}.mp4'
    video_file.save(input_path)
    
    # Convert to HLS
    output_dir = f'streams/{video_id}'
    results = converter.convert(input_path, output_dir)
    
    return jsonify({
        'video_id': video_id,
        'master_playlist': results['master_playlist'],
        'duration': results['total_duration']
    })
```

#### Django Integration

```python
from django.http import JsonResponse
from django.views import View
from hls_converter import HLSConverter

class VideoConvertView(View):
    def post(self, request):
        converter = HLSConverter()
        
        video_file = request.FILES.get('video')
        if not video_file:
            return JsonResponse({'error': 'No video file'}, status=400)
        
        # Process video
        results = converter.convert(video_file.temporary_file_path(), 'media/streams/')
        
        return JsonResponse({
            'success': True,
            'playlist': results['master_playlist'],
            'processing_time': results['total_duration']
        })
```

## API Best Practices

### Resource Management

```python
# Use context managers when available (future feature)
with HLSConverter() as converter:
    results = converter.convert('input.mp4', 'output')

# Current best practice: reuse converter instances
converter = HLSConverter()
for video_file in video_files:
    results = converter.convert(video_file, f'output_{video_file.stem}')
```

### Configuration Management

```python
# Store configuration in environment/config files
import os
from hls_converter import HLSConfig

config = HLSConfig(
    segment_duration=int(os.getenv('HLS_SEGMENT_DURATION', '4')),
    preset=os.getenv('HLS_PRESET', 'medium'),
    max_workers=int(os.getenv('HLS_MAX_WORKERS', '4'))
)

converter = HLSConverter(config)
```

### Performance Optimization

```python
# For high-throughput scenarios
from hls_converter import HLSConverter, HLSConfig

# Use hardware encoding when available
config = HLSConfig(
    preset='fast',           # Faster encoding
    max_workers=2,          # Limit workers to avoid memory issues
    segment_duration=6      # Longer segments for better compression
)

converter = HLSConverter(config)
```

## Next Steps

- 📖 [Configuration Guide](../configuration.md) - Deep dive into configuration options
- 🎯 [Quality Settings](../quality.md) - Optimize video quality settings
- 🔧 [Advanced Topics](../advanced/profiles.md) - Custom profiles and integration patterns
- 🏗️ [Architecture](../architecture.md) - Understanding the internal architecture