# Quick Start

Get up and running with HLS Converter in 5 minutes! This guide will walk you through your first video conversion.

## Prerequisites

Make sure you have completed the [installation](installation.md):

- ✅ Python 3.8+
- ✅ HLS Converter installed (`pip install hls-converter`)
- ✅ FFmpeg installed and in PATH

## Your First Conversion

### Step 1: Check Your Setup

Verify everything is working:

```bash
hls-converter --version
```

Expected output:
```
hls-converter 1.0.0
```

### Step 2: Check Available Encoders

See what hardware acceleration is available:

```bash
hls-converter --list-encoders
```

This will show you the best encoders HLS Converter detected on your system.

### Step 3: Convert Your First Video

=== "Basic Conversion"

    Convert a video with automatic optimization:

    ```bash
    hls-converter input.mp4
    ```

    This will:
    - 📊 Analyze your video automatically
    - 🎯 Choose optimal resolution ladder  
    - ⚡ Use hardware acceleration if available
    - 📁 Output to folder named `input/` (same as filename)

=== "Custom Output Directory"

    Specify where to save the HLS files:

    ```bash
    hls-converter input.mp4 --output streaming_output
    ```

=== "Specific Resolutions"

    Choose which quality levels to generate:

    ```bash
    hls-converter input.mp4 --resolutions 720p,1080p
    ```

### Step 4: Verify the Output

After conversion completes, you'll see output like:

```
🎉 All stream processing completed!

📊 Conversion Results
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Metric                ┃ Value           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Total Processing Time │ 45.3s           │
│ Processing Speed      │ 12.34 MB/s      │
│ Video Resolutions     │ 3               │
│ Audio Tracks         │ 1               │
│ Master Playlist      │ output/master.m3u8 │
└───────────────────────┴─────────────────┘
```

Check your output directory:

```bash
ls -la output/
```

You should see:
```
output/
├── master.m3u8          # ← Main playlist file
├── 720p/
│   ├── playlist.m3u8
│   ├── chunk_000.ts
│   └── ...
├── 1080p/
│   ├── playlist.m3u8  
│   ├── chunk_000.ts
│   └── ...
└── audio_english/
    ├── playlist.m3u8
    └── ...
```

## Testing Your HLS Stream

### Option 1: Online HLS Player

Upload your `master.m3u8` to any web server and test with online players:

- [HLS.js Demo](https://hls-js.netlify.app/demo/)
- [Video.js HLS](https://videojs-http-streaming.netlify.app/)

### Option 2: Local Testing with Python

Create a simple test server:

```bash
# Navigate to your output directory
cd output

# Start a local server (Python 3)
python -m http.server 8000

# Open http://localhost:8000/master.m3u8 in a compatible player
```

### Option 3: VLC Player

VLC can play HLS streams directly:

1. Open VLC
2. Go to **Media → Open Network Stream**
3. Enter: `file:///path/to/your/output/master.m3u8`
4. Click Play

## Common First-Time Scenarios

### Mobile-Optimized Streaming

For mobile apps or poor connections:

```bash
hls-converter input.mp4 \
  --resolutions 240p,360p,480p,720p \
  --segment-duration 2 \
  --preset fast
```

### High-Quality Web Streaming

For desktop web players with good connections:

```bash
hls-converter input.mp4 \
  --resolutions 720p,1080p,1440p \
  --segment-duration 6 \
  --preset medium
```

### Batch Processing

Convert multiple videos:

```bash
# Convert all MP4 files in current directory
for file in *.mp4; do
  hls-converter "$file" --output "hls_${file%.mp4}"
done
```

## Understanding the Output

### Master Playlist (`master.m3u8`)

This is the main entry point for HLS players. It references all quality levels:

```m3u8
#EXTM3U
#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="english",DEFAULT=YES,AUTOSELECT=YES,LANGUAGE="english",URI="audio_english/playlist.m3u8"
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720,CODECS="avc1.640029",AUDIO="audio"
720p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080,CODECS="avc1.640029",AUDIO="audio"
1080p/playlist.m3u8
```

### Quality-Specific Playlists

Each resolution has its own playlist (`720p/playlist.m3u8`):

```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:2
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:VOD
#EXTINF:2.000000,
chunk_000.ts
#EXTINF:2.000000,
chunk_001.ts
#EXT-X-ENDLIST
```

### Video Segments

The actual video data is stored in `.ts` (Transport Stream) files, typically 2-6 seconds each.

## Quick Tips

!!! tip "Performance"
    - Hardware acceleration can be 5-10x faster than software encoding
    - Use `--preset ultrafast` for fastest conversion (lower quality)
    - Use `--preset slow` for best quality (slower conversion)

!!! tip "Quality"
    - Let HLS Converter choose resolutions automatically for best results
    - For 4K source videos, include 1080p and 720p for compatibility
    - Shorter segments (2s) = better seeking, longer segments (6s) = better compression

!!! tip "Storage"
    - HLS files are typically 1.5-2x larger than original due to multiple resolutions
    - Consider 2-4 quality levels as optimal balance of quality vs storage

## Troubleshooting Quick Fixes

??? question "Conversion is very slow"
    
    ```bash
    # Use hardware encoding and faster preset
    hls-converter input.mp4 --preset ultrafast --workers 4
    
    # Check if hardware acceleration is working
    hls-converter --list-encoders
    ```

??? question "Output quality is poor"
    
    ```bash
    # Use better quality preset
    hls-converter input.mp4 --preset medium --crf 20
    ```

??? question "File too large"
    
    ```bash
    # Reduce number of quality levels
    hls-converter input.mp4 --resolutions 720p,1080p
    ```

??? question "Player won't load stream"
    
    - Verify `master.m3u8` exists and is not empty
    - Check that segment files (`.ts`) exist in quality folders
    - Ensure web server serves `.m3u8` with correct MIME type (`application/x-mpegURL`)

## Next Steps

Now that you've successfully converted your first video:

- 📖 [Learn more CLI options](cli.md) for advanced control
- ⚙️ [Configure custom settings](configuration.md) for your workflow  
- 🐍 [Use the Python API](api/index.md) to integrate into applications
- 🎯 [Optimize video quality](quality.md) for your specific needs
- 💻 [Set up batch processing](batch.md) for multiple files

## Example Projects

Here are some real-world examples to inspire your next steps:

!!! example "Video Streaming Website"
    ```python
    # Convert user uploads for adaptive streaming
    from hls_converter import HLSConverter
    
    def process_upload(video_file, user_id, video_id):
        converter = HLSConverter()
        output_dir = f"cdn/{user_id}/{video_id}"
        
        results = converter.convert(video_file, output_dir)
        
        # Save playlist URL to database
        save_to_db(video_id, results['master_playlist'])
        return results['master_playlist']
    ```

!!! example "Mobile App Backend" 
    ```python
    # Optimize for mobile viewing
    from hls_converter import HLSConverter, HLSConfig
    
    config = HLSConfig(
        segment_duration=2,  # Better for mobile networks
        preset='fast',       # Faster processing
    )
    
    converter = HLSConverter(config)
    results = converter.convert(
        'content.mp4', 
        'mobile_streams',
        ['240p', '360p', '720p']  # Mobile-friendly resolutions
    )
    ```