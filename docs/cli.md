# CLI Reference

The HLS Converter command-line interface provides comprehensive options for video conversion. This reference covers all available commands and options.

## Basic Usage

```bash
hls-converter [OPTIONS] INPUT_FILE
```

## Command Structure

```
hls-converter input.mp4 [options]
             ↑         ↑
       input file   configuration options
```

## Global Options

### Help and Information

#### `--help`, `-h`
Show help message and exit.

```bash
hls-converter --help
```

#### `--version`, `-v`
Show program version and exit.

```bash
hls-converter --version
# Output: hls-converter 1.0.0
```

#### `--list-encoders`
List all available video and audio encoders on your system.

```bash
hls-converter --list-encoders
```

Example output:
```
Available Encoders
┏━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Type  ┃ Category ┃ Codec             ┃ Name                     ┃ Selected ┃
┡━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Video │ Hardware │ h264_videotoolbox │ VideoToolbox (macOS)     │ ✅       │
│ Video │ Software │ libx264           │ x264 Software            │          │
│ Audio │ Hardware │ aac_at            │ AudioToolbox AAC (macOS) │ ✅       │
└───────┴──────────┴───────────────────┴──────────────────────────┴──────────┘
```

#### `--analyze-only`
Analyze input file without performing conversion. Useful for checking video properties and optimal settings.

```bash
hls-converter input.mp4 --analyze-only
```

## Input/Output Options

### Input File
**Required.** Path to the input video file.

```bash
hls-converter /path/to/video.mp4
hls-converter "video with spaces.mov"
```

Supported formats: MP4, MKV, AVI, MOV, M4V, and other FFmpeg-supported formats.

### `--output`, `-o`
Specify output directory. If not provided, uses input filename without extension.

```bash
# Output to specific directory
hls-converter input.mp4 --output streaming_files

# Output to current directory with custom name  
hls-converter input.mp4 --output ./my_stream

# Absolute path
hls-converter input.mp4 --output /var/www/streams/video1
```

**Default behavior:**
- Input: `movie.mp4` → Output: `movie/`
- Input: `/path/video.mov` → Output: `/path/video/`

## Quality and Resolution Options

### `--resolutions`, `-r`
Comma-separated list of resolutions to generate.

**Available resolutions:** `144p`, `240p`, `360p`, `480p`, `720p`, `1080p`, `1440p`, `2160p`

```bash
# Mobile-friendly resolutions
hls-converter input.mp4 --resolutions 360p,480p,720p

# High-quality streaming
hls-converter input.mp4 --resolutions 720p,1080p,1440p

# Single resolution
hls-converter input.mp4 --resolutions 1080p

# All available resolutions
hls-converter input.mp4 --resolutions 144p,240p,360p,480p,720p,1080p,1440p,2160p
```

!!! note "Automatic Resolution Selection"
    If `--resolutions` is not specified, HLS Converter automatically selects optimal resolutions based on your input video:
    
    - **4K input** → `480p,720p,1080p,1440p,2160p`
    - **1080p input** → `360p,480p,720p,1080p`
    - **720p input** → `240p,360p,480p,720p`

### `--preset`, `-p`
Encoding speed vs quality preset.

**Available presets:** `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`

```bash
# Fastest encoding (lower quality)
hls-converter input.mp4 --preset ultrafast

# Balanced speed/quality (default)
hls-converter input.mp4 --preset fast

# Best quality (slower encoding)
hls-converter input.mp4 --preset slow
```

**Preset Comparison:**

| Preset | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| `ultrafast` | ⚡⚡⚡⚡⚡ | ⭐⭐ | Quick previews, testing |
| `fast` | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | **Default**, good balance |
| `medium` | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Web streaming |
| `slow` | ⚡⚡ | ⭐⭐⭐⭐⭐⭐ | Archive quality |

### `--crf`
Constant Rate Factor for software encoding. Lower values = better quality.

**Range:** `0-51` (default: `23`)

```bash
# Higher quality (larger files)
hls-converter input.mp4 --crf 18

# Standard quality  
hls-converter input.mp4 --crf 23

# Lower quality (smaller files)
hls-converter input.mp4 --crf 28
```

**CRF Guidelines:**
- `18-22`: Visually lossless quality
- `23-25`: High quality (default range)  
- `26-30`: Standard quality
- `31+`: Lower quality, smaller files

## Performance Options

### `--workers`, `-w`
Number of parallel processing workers.

```bash
# Use 4 parallel workers
hls-converter input.mp4 --workers 4

# Use all available CPU cores minus 1 (auto-detected)
hls-converter input.mp4  # Default behavior

# Single-threaded processing
hls-converter input.mp4 --workers 1
```

**Guidelines:**
- **Default**: Auto-detects optimal workers (usually CPU cores - 1)
- **High-end systems**: Can handle 6-8 workers
- **Limited memory**: Use 2-4 workers
- **Network storage**: Reduce workers to 2-3

### `--segment-duration`
HLS segment duration in seconds.

```bash
# 2-second segments (better seeking, more files)
hls-converter input.mp4 --segment-duration 2

# 6-second segments (better compression, fewer files)  
hls-converter input.mp4 --segment-duration 6

# 10-second segments (lowest overhead)
hls-converter input.mp4 --segment-duration 10
```

**Duration Trade-offs:**

| Duration | Seeking | Compression | Network | Files |
|----------|---------|-------------|---------|-------|
| 2s | ⚡ Fast | 📊 Lower | 🌐 Better | 📁 More |
| 6s | ⚡ Medium | 📊 Better | 🌐 Medium | 📁 Medium |
| 10s | ⚡ Slower | 📊 Best | 🌐 Higher latency | 📁 Fewer |

**Recommendations:**
- **Live streaming**: 2-4 seconds
- **VOD streaming**: 4-6 seconds  
- **Archive/download**: 6-10 seconds

### `--gop-size`
Group of Pictures (GOP) size. Affects seeking precision and compression.

```bash
# Better seeking (more keyframes)
hls-converter input.mp4 --gop-size 30

# Default (balanced)
hls-converter input.mp4 --gop-size 48

# Better compression (fewer keyframes)  
hls-converter input.mp4 --gop-size 120
```

**GOP Size Guidelines:**
- **30 frames**: Better seeking, larger files
- **48 frames**: Good balance (default)
- **120 frames**: Better compression, less precise seeking

## Audio and Subtitle Options

### `--no-subtitles`
Skip subtitle conversion entirely.

```bash
hls-converter input.mp4 --no-subtitles
```

### `--include-bitmap-subtitles`
Include bitmap subtitle formats (PGS, DVD). Usually skipped because they require OCR.

```bash
hls-converter input.mp4 --include-bitmap-subtitles
```

!!! warning "Bitmap Subtitles"
    Bitmap subtitles (PGS, DVD) cannot be directly converted to WebVTT text format. This option will attempt conversion but may fail or produce empty subtitle files.

## Configuration Options

### `--config`, `-c`
Load settings from JSON configuration file.

```bash
hls-converter input.mp4 --config my_settings.json
```

Example configuration file:
```json
{
  "segment_duration": 4,
  "preset": "medium",
  "crf": 20,
  "max_workers": 6,
  "convert_subtitles": true,
  "bitrate_profiles": [
    {
      "name": "720p",
      "resolution": [1280, 720],
      "max_bitrate_kbps": 2500,
      "min_bitrate_kbps": 1800
    }
  ]
}
```

### `--save-config`
Save current settings to JSON file for reuse.

```bash
# Save current settings
hls-converter input.mp4 --preset medium --crf 20 --save-config my_settings.json

# Later, reuse the settings
hls-converter another_video.mp4 --config my_settings.json
```

!!! tip "Configuration Priority"
    Settings are applied in this order (later overrides earlier):
    1. Default settings
    2. Configuration file (`--config`)
    3. Command-line arguments

## Logging Options

### `--quiet`, `-q`
Reduce output verbosity. Shows only essential information.

```bash
hls-converter input.mp4 --quiet
```

### `--debug`
Enable detailed debug logging. Shows FFmpeg commands, detailed progress, and error traces.

```bash
hls-converter input.mp4 --debug
```

**Debug output includes:**
- FFmpeg command lines
- Encoder detection details
- Detailed timing information
- Full error stack traces
- Step-by-step progress

## Practical Examples

### Quick Conversion Examples

=== "Basic Usage"
    ```bash
    # Convert with automatic settings
    hls-converter movie.mp4
    
    # Convert to specific directory
    hls-converter movie.mp4 --output ./streaming
    
    # Convert with custom resolutions
    hls-converter movie.mp4 --resolutions 720p,1080p
    ```

=== "Quality Optimization"
    ```bash
    # High quality for archive
    hls-converter movie.mp4 --preset slow --crf 18
    
    # Fast conversion for testing
    hls-converter movie.mp4 --preset ultrafast
    
    # Balanced quality/speed
    hls-converter movie.mp4 --preset medium --crf 21
    ```

=== "Mobile Optimization"
    ```bash
    # Mobile-friendly streaming
    hls-converter movie.mp4 \
      --resolutions 240p,360p,480p,720p \
      --segment-duration 2 \
      --preset fast
    
    # Data-conscious settings  
    hls-converter movie.mp4 \
      --resolutions 240p,360p,480p \
      --crf 26
    ```

=== "Performance Tuning"
    ```bash
    # Maximum performance (if hardware allows)
    hls-converter movie.mp4 --workers 8 --preset ultrafast
    
    # Conservative resource usage
    hls-converter movie.mp4 --workers 2 --preset fast
    
    # Memory-constrained systems
    hls-converter movie.mp4 --workers 1 --segment-duration 10
    ```

### Advanced Workflows

=== "Batch Processing"
    ```bash
    # Convert all MP4 files
    for file in *.mp4; do
      hls-converter "$file" --output "hls_${file%.mp4}" \
        --resolutions 720p,1080p \
        --preset medium
    done
    ```

=== "Configuration Management"
    ```bash
    # Create reusable configuration
    hls-converter sample.mp4 \
      --preset medium \
      --segment-duration 4 \
      --resolutions 720p,1080p,1440p \
      --save-config production.json \
      --analyze-only  # Don't actually convert
    
    # Use configuration for production
    hls-converter movie1.mp4 --config production.json
    hls-converter movie2.mp4 --config production.json
    ```

=== "Testing and Analysis"
    ```bash
    # Analyze video without conversion
    hls-converter movie.mp4 --analyze-only
    
    # Check encoder capabilities
    hls-converter --list-encoders
    
    # Test with debug information
    hls-converter sample.mp4 --debug --resolutions 720p
    ```

## Exit Codes

The CLI returns different exit codes for scripting:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error (file not found, conversion failed) |
| `2` | Invalid arguments |
| `130` | Interrupted by user (Ctrl+C) |

Example usage in scripts:
```bash
if hls-converter movie.mp4 --quiet; then
  echo "Conversion successful"
  upload_to_cdn movie/
else
  echo "Conversion failed with code $?"
  exit 1
fi
```

## Environment Variables

### `FFMPEG_BINARY`
Override FFmpeg executable path:

```bash
export FFMPEG_BINARY="/usr/local/bin/ffmpeg"
hls-converter movie.mp4
```

### `HLS_CONVERTER_CONFIG`
Default configuration file:

```bash
export HLS_CONVERTER_CONFIG="/etc/hls-converter/default.json"
hls-converter movie.mp4  # Uses default config automatically
```

## Shell Completion

Enable tab completion for bash/zsh:

```bash
# Bash
eval "$(_HLS_CONVERTER_COMPLETE=source hls-converter)"

# Zsh  
eval "$(_HLS_CONVERTER_COMPLETE=source_zsh hls-converter)"

# Add to your shell profile for persistence
echo 'eval "$(_HLS_CONVERTER_COMPLETE=source hls-converter)"' >> ~/.bashrc
```

## Common Patterns

### Development Workflow
```bash
# Quick test conversion
hls-converter test.mp4 --preset ultrafast --resolutions 720p --quiet

# Production conversion  
hls-converter final.mp4 --config production.json --output /var/www/streams/
```

### CI/CD Pipeline
```bash
#!/bin/bash
set -e  # Exit on error

# Validate input
hls-converter "$1" --analyze-only --quiet || exit 1

# Convert with error handling
hls-converter "$1" \
  --output "./dist/${1%.*}" \
  --config ci-config.json \
  --quiet || {
    echo "Conversion failed for $1" >&2
    exit 1
}

echo "Successfully converted $1"
```

## Next Steps

- 📖 [Configuration Guide](configuration.md) - Learn about JSON configuration files
- 🎯 [Quality Settings](quality.md) - Optimize video quality for your use case
- 🐍 [Python API](api/index.md) - Integrate conversion into your applications
- 💻 [Batch Processing](batch.md) - Handle multiple files efficiently