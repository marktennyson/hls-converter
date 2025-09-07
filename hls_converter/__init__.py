"""
HLS Converter - Professional HLS streaming converter
===========================================

A powerful, class-based HLS (HTTP Live Streaming) converter with automatic
bitrate adjustment, hardware acceleration support, and comprehensive logging.

Key Features:
- Automatic hardware encoder detection (VideoToolbox, NVENC, QuickSync, etc.)
- Dynamic bitrate adjustment based on input video resolution  
- Multi-threaded parallel processing
- Rich console logging with progress tracking
- Subtitle conversion to WebVTT
- Professional CLI interface

Usage:
    from hls_converter import HLSConverter
    
    converter = HLSConverter()
    converter.convert('input.mp4', 'output_dir')

Author: HLS Converter Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "HLS Converter Team"

from .converter import HLSConverter
from .config import HLSConfig
from .media_analyzer import MediaAnalyzer
from .encoder_detector import EncoderDetector

__all__ = ["HLSConverter", "HLSConfig", "MediaAnalyzer", "EncoderDetector"]