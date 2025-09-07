#!/usr/bin/env python3
"""
Installation test script for HLS Converter
==========================================

This script tests that the HLS Converter package can be imported and basic
functionality works correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all main components can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from hls_converter import HLSConverter, HLSConfig, MediaAnalyzer, EncoderDetector
        print("✅ Main components imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    try:
        from hls_converter.config import BitrateProfile
        print("✅ BitrateProfile imported successfully")
    except ImportError as e:
        print(f"❌ BitrateProfile import failed: {e}")
        return False
    
    return True


def test_encoder_detection():
    """Test encoder detection functionality."""
    print("\\n🔧 Testing encoder detection...")
    
    try:
        from hls_converter.encoder_detector import EncoderDetector
        
        detector = EncoderDetector()
        encoder_info = detector.detect_encoders()
        
        print(f"✅ Video encoder: {encoder_info['video_name']}")
        print(f"✅ Audio encoder: {encoder_info['audio_name']}")
        
        return True
    except Exception as e:
        print(f"❌ Encoder detection failed: {e}")
        return False


def test_configuration():
    """Test configuration system."""
    print("\\n⚙️ Testing configuration...")
    
    try:
        from hls_converter import HLSConfig
        from hls_converter.config import BitrateProfile
        
        # Test default config
        config = HLSConfig()
        print(f"✅ Default config created: {len(config.bitrate_profiles)} profiles")
        
        # Test custom profiles
        profiles = HLSConfig.create_adaptive_profiles(1920, 1080, 5000)
        print(f"✅ Adaptive profiles created: {len(profiles)} profiles")
        
        # Test config serialization
        config_dict = config.to_dict()
        config2 = HLSConfig.from_dict(config_dict)
        print("✅ Configuration serialization works")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_cli_help():
    """Test CLI help system."""
    print("\\n📋 Testing CLI...")
    
    try:
        from hls_converter.cli import HLSConverterCLI
        
        cli = HLSConverterCLI()
        
        # Test help (should not raise exception)
        try:
            cli.parser.parse_args(['--help'])
        except SystemExit:
            # Expected behavior for --help
            pass
        
        print("✅ CLI help system works")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def test_ffmpeg_availability():
    """Test if FFmpeg is available."""
    print("\\n📹 Testing FFmpeg availability...")
    
    import subprocess
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\\n')[0]
            print(f"✅ FFmpeg found: {version_line}")
            return True
        else:
            print("❌ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        print("   Please install FFmpeg: https://ffmpeg.org/download.html")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg command timed out")
        return False
    except Exception as e:
        print(f"❌ FFmpeg test failed: {e}")
        return False


def test_basic_converter_creation():
    """Test basic converter creation without conversion."""
    print("\\n🎬 Testing converter creation...")
    
    try:
        from hls_converter import HLSConverter
        
        converter = HLSConverter()
        print("✅ HLSConverter created successfully")
        
        # Test that analyzer works
        analyzer = converter.media_analyzer
        print("✅ MediaAnalyzer accessible")
        
        # Test that encoder detector works
        detector = converter.encoder_detector
        print("✅ EncoderDetector accessible")
        
        return True
    except Exception as e:
        print(f"❌ Converter creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🎥 HLS Converter - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Encoder Detection", test_encoder_detection),
        ("Configuration Test", test_configuration),
        ("CLI Test", test_cli_help),
        ("FFmpeg Availability", test_ffmpeg_availability),
        ("Converter Creation", test_basic_converter_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except KeyboardInterrupt:
            print("\\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
    
    print("\\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! HLS Converter is ready to use.")
        print("\\nNext steps:")
        print("1. Try the CLI: hls-converter --help")
        print("2. Run examples: python examples/basic_usage.py")
        print("3. Convert a video: hls-converter your_video.mp4")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\\nCommon issues:")
        print("- FFmpeg not installed or not in PATH")
        print("- Missing Python dependencies (try: pip install -r requirements.txt)")
        print("- Package not installed (try: pip install -e .)")
        return 1


if __name__ == "__main__":
    sys.exit(main())