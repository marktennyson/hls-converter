#!/usr/bin/env python3
"""
Basic usage examples for HLS Converter
=====================================

This script demonstrates various ways to use the HLS Converter library.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import hls_converter
sys.path.insert(0, str(Path(__file__).parent.parent))

from hls_converter import HLSConverter, HLSConfig, BitrateProfile


def basic_conversion():
    """Basic video conversion with default settings."""
    print("🎬 Basic Conversion Example")
    print("=" * 40)
    
    # Create converter with default settings
    converter = HLSConverter()
    
    # Convert video (replace with actual video file)
    input_file = "sample_video.mp4"  # Replace with your video file
    output_dir = "hls_output"
    
    if not Path(input_file).exists():
        print(f"⚠️  Sample video file '{input_file}' not found.")
        print("   Please provide a real video file to test conversion.")
        return
    
    try:
        results = converter.convert(input_file, output_dir)
        print(f"✅ Conversion completed!")
        print(f"📋 Master playlist: {results['master_playlist']}")
        print(f"⚡ Processing speed: {results['processing_speed_mbps']:.2f} MB/s")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")


def custom_configuration():
    """Video conversion with custom configuration."""
    print("\n🔧 Custom Configuration Example")
    print("=" * 40)
    
    # Create custom configuration
    config = HLSConfig(
        segment_duration=4,      # 4-second segments
        preset='medium',         # Better quality
        crf=20,                 # Higher quality for software encoding
        max_workers=4,          # Limit parallel workers
        convert_subtitles=True  # Convert subtitles
    )
    
    converter = HLSConverter(config)
    
    input_file = "sample_video.mp4"
    output_dir = "hls_custom_output"
    
    if not Path(input_file).exists():
        print(f"⚠️  Sample video file '{input_file}' not found.")
        return
    
    # Convert with specific resolutions
    resolutions = ['480p', '720p', '1080p']
    
    try:
        results = converter.convert(input_file, output_dir, resolutions)
        print(f"✅ Custom conversion completed!")
        print(f"📺 Created {len(results['resolutions_created'])} video qualities")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")


def custom_bitrate_profiles():
    """Video conversion with custom bitrate profiles."""
    print("\n⚡ Custom Bitrate Profiles Example")
    print("=" * 40)
    
    # Define custom bitrate profiles
    profiles = [
        BitrateProfile("low", (640, 360), 800, 600),      # Low quality
        BitrateProfile("medium", (1280, 720), 2000, 1500), # Medium quality
        BitrateProfile("high", (1920, 1080), 4000, 3000),  # High quality
    ]
    
    config = HLSConfig(bitrate_profiles=profiles)
    converter = HLSConverter(config)
    
    input_file = "sample_video.mp4"
    output_dir = "hls_custom_bitrates"
    
    if not Path(input_file).exists():
        print(f"⚠️  Sample video file '{input_file}' not found.")
        return
    
    try:
        results = converter.convert(input_file, output_dir)
        print(f"✅ Custom bitrate conversion completed!")
        for profile in profiles:
            print(f"   📺 {profile.name}: {profile.max_bitrate_kbps}kbps max")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")


def analyze_media():
    """Analyze media file without conversion."""
    print("\n🔍 Media Analysis Example")
    print("=" * 40)
    
    converter = HLSConverter()
    input_file = "sample_video.mp4"
    
    if not Path(input_file).exists():
        print(f"⚠️  Sample video file '{input_file}' not found.")
        return
    
    # Analyze the media file
    media_info = converter.media_analyzer.analyze(Path(input_file))
    
    if media_info.video:
        v = media_info.video
        print(f"📺 Video: {v.width}x{v.height} @ {v.fps:.1f}fps")
        if v.bitrate:
            print(f"   Bitrate: {v.bitrate}kbps")
        print(f"   Duration: {v.duration:.1f}s")
        print(f"   Codec: {v.codec}")
    
    print(f"🎵 Audio tracks: {len(media_info.audio_tracks)}")
    for track in media_info.audio_tracks:
        print(f"   🎧 {track.language} ({track.codec})")
    
    print(f"💬 Subtitle tracks: {len(media_info.subtitle_tracks)}")
    for track in media_info.subtitle_tracks:
        print(f"   📄 {track.language} ({track.codec})")
    
    # Get recommended resolutions
    if media_info.video:
        recommended = converter.media_analyzer.get_optimal_resolutions(media_info.video)
        print(f"📋 Recommended resolutions: {', '.join(recommended)}")


def batch_processing():
    """Process multiple video files."""
    print("\n📦 Batch Processing Example")
    print("=" * 40)
    
    # Directory containing videos to process
    input_dir = Path("input_videos")  # Replace with your directory
    output_base = Path("batch_output")
    
    if not input_dir.exists():
        print(f"⚠️  Input directory '{input_dir}' not found.")
        print("   Create this directory and add some video files to test batch processing.")
        return
    
    converter = HLSConverter()
    
    # Find all video files
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v']
    video_files = []
    for ext in video_extensions:
        video_files.extend(input_dir.glob(f'*{ext}'))
    
    if not video_files:
        print("⚠️  No video files found in input directory.")
        return
    
    print(f"📁 Found {len(video_files)} video files to process...")
    
    for video_file in video_files:
        output_dir = output_base / video_file.stem
        
        print(f"\\n🎬 Processing: {video_file.name}")
        
        try:
            results = converter.convert(video_file, output_dir)
            if results['success']:
                print(f"   ✅ Completed in {results['total_duration']:.1f}s")
            else:
                print(f"   ❌ Failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def detect_encoders():
    """Detect available hardware and software encoders."""
    print("\n🔍 Encoder Detection Example")
    print("=" * 40)
    
    from hls_converter.encoder_detector import EncoderDetector
    
    detector = EncoderDetector()
    encoder_info = detector.detect_encoders()
    
    print("🎬 Video Encoders:")
    for category in ['hardware', 'software']:
        encoders = encoder_info['all_encoders']['video'][category]
        if encoders:
            print(f"   {category.title()}: {', '.join([name for codec, name in encoders])}")
    
    print("\\n🎵 Audio Encoders:")
    for category in ['hardware', 'software']:
        encoders = encoder_info['all_encoders']['audio'][category]
        if encoders:
            print(f"   {category.title()}: {', '.join([name for codec, name in encoders])}")
    
    print("\\n⭐ Selected Encoders:")
    print(f"   Video: {encoder_info['video_name']}")
    print(f"   Audio: {encoder_info['audio_name']}")


if __name__ == "__main__":
    print("🎥 HLS Converter - Usage Examples")
    print("=" * 50)
    
    # Run all examples
    try:
        detect_encoders()
        analyze_media()
        basic_conversion()
        custom_configuration()
        custom_bitrate_profiles()
        batch_processing()
        
        print("\\n🎉 All examples completed!")
        print("\\nTo use these examples with real video files:")
        print("1. Replace 'sample_video.mp4' with your actual video file")
        print("2. Create 'input_videos/' directory with video files for batch processing")
        print("3. Run: python examples/basic_usage.py")
        
    except KeyboardInterrupt:
        print("\\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()