"""
Configuration management for HLS Converter
==========================================

Handles all configuration settings, bitrate profiles, and quality presets.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from pathlib import Path


@dataclass
class BitrateProfile:
    """Bitrate profile for different video resolutions."""
    name: str
    resolution: Tuple[int, int]  # (width, height)
    max_bitrate_kbps: int
    min_bitrate_kbps: int
    audio_bitrate_kbps: int = 160
    
    @property
    def scale_filter(self) -> str:
        """FFmpeg scale filter string."""
        return f"{self.resolution[0]}:{self.resolution[1]}"
    
    @property
    def resolution_name(self) -> str:
        """Human-readable resolution name."""
        return f"{self.resolution[1]}p"


@dataclass
class HLSConfig:
    """Main configuration class for HLS Converter."""
    
    # Output settings
    segment_duration: int = 2
    playlist_type: str = "vod"
    gop_size: int = 48
    
    # Processing settings
    max_workers: Optional[int] = None
    # Force CPU (software) encoding and disable hardware acceleration
    force_software_encoding: bool = False
    # When True, do not pass any hwaccel flags to FFmpeg (CPU decode)
    disable_hwaccel: bool = False
    # Threads passed to encoder (FFmpeg -threads). If None, defaults to CPU count
    encoder_threads: Optional[int] = None
    
    # Quality settings
    preset: str = "fast"
    crf: int = 23
    
    # Subtitle settings
    convert_subtitles: bool = True
    skip_bitmap_subtitles: bool = True
    
    # Default bitrate profiles (will be dynamically adjusted)
    bitrate_profiles: List[BitrateProfile] = field(default_factory=lambda: [
        # Ultra-low quality for very poor connections
        BitrateProfile("144p", (256, 144), 300, 200),
        BitrateProfile("240p", (426, 240), 500, 350),
        
        # Standard mobile quality
        BitrateProfile("360p", (640, 360), 800, 600),
        BitrateProfile("480p", (854, 480), 1200, 900),
        
        # HD quality
        BitrateProfile("720p", (1280, 720), 2500, 1800),
        BitrateProfile("1080p", (1920, 1080), 5000, 3500),
        
        # 4K quality
        BitrateProfile("1440p", (2560, 1440), 8000, 6000),
        BitrateProfile("2160p", (3840, 2160), 16000, 12000),
    ])
    
    @classmethod
    def create_adaptive_profiles(cls, input_width: int, input_height: int, 
                               input_bitrate: Optional[int] = None) -> List[BitrateProfile]:
        """
        Create adaptive bitrate profiles based on input video characteristics.
        
        Args:
            input_width: Input video width
            input_height: Input video height  
            input_bitrate: Input video bitrate in kbps (optional)
            
        Returns:
            List of BitrateProfile objects suitable for the input video
        """
        input_resolution = input_width * input_height
        suitable_profiles = []
        
        # Base profiles with adjusted bitrates
        base_profiles = [
            BitrateProfile("144p", (256, 144), 300, 200),
            BitrateProfile("240p", (426, 240), 500, 350),
            BitrateProfile("360p", (640, 360), 800, 600),
            BitrateProfile("480p", (854, 480), 1200, 900),
            BitrateProfile("720p", (1280, 720), 2500, 1800),
            BitrateProfile("1080p", (1920, 1080), 5000, 3500),
            BitrateProfile("1440p", (2560, 1440), 8000, 6000),
            BitrateProfile("2160p", (3840, 2160), 16000, 12000),
        ]
        
        # Filter profiles that don't exceed input resolution
        for profile in base_profiles:
            profile_resolution = profile.resolution[0] * profile.resolution[1]
            if profile_resolution <= input_resolution * 1.1:  # Allow 10% upscaling
                
                # Adjust bitrate based on input characteristics
                if input_bitrate:
                    # Scale bitrate based on resolution ratio and input bitrate
                    resolution_ratio = profile_resolution / input_resolution
                    adjusted_max = min(
                        profile.max_bitrate_kbps,
                        int(input_bitrate * resolution_ratio * 1.2)
                    )
                    adjusted_min = int(adjusted_max * 0.7)
                    
                    profile.max_bitrate_kbps = max(adjusted_max, profile.min_bitrate_kbps)
                    profile.min_bitrate_kbps = adjusted_min
                
                suitable_profiles.append(profile)
        
        # Ensure we have at least one profile
        if not suitable_profiles and base_profiles:
            suitable_profiles = [base_profiles[0]]  # Add lowest quality as fallback
        
        return suitable_profiles
    
    def get_encoder_specific_args(self, encoder: str) -> List[str]:
        """Get encoder-specific FFmpeg arguments."""
        args = []
        
        if encoder == "h264_videotoolbox":
            args.extend(["-allow_sw", "1"])
        elif encoder == "h264_nvenc":
            args.extend(["-preset", self.preset, "-rc", "vbr"])
        elif encoder == "libx264":
            args.extend(["-preset", self.preset, "-crf", str(self.crf)])
        elif encoder == "h264_qsv":
            args.extend(["-preset", self.preset])
        
        return args
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "segment_duration": self.segment_duration,
            "playlist_type": self.playlist_type,
            "gop_size": self.gop_size,
            "max_workers": self.max_workers,
            "force_software_encoding": self.force_software_encoding,
            "disable_hwaccel": self.disable_hwaccel,
            "encoder_threads": self.encoder_threads,
            "preset": self.preset,
            "crf": self.crf,
            "convert_subtitles": self.convert_subtitles,
            "skip_bitmap_subtitles": self.skip_bitmap_subtitles,
            "bitrate_profiles": [
                {
                    "name": p.name,
                    "resolution": p.resolution,
                    "max_bitrate_kbps": p.max_bitrate_kbps,
                    "min_bitrate_kbps": p.min_bitrate_kbps,
                    "audio_bitrate_kbps": p.audio_bitrate_kbps
                }
                for p in self.bitrate_profiles
            ]
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'HLSConfig':
        """Create configuration from dictionary."""
        profiles = [
            BitrateProfile(
                p["name"],
                tuple(p["resolution"]),
                p["max_bitrate_kbps"],
                p["min_bitrate_kbps"],
                p.get("audio_bitrate_kbps", 160)
            )
            for p in config_dict.get("bitrate_profiles", [])
        ]

        config = cls()
        config.segment_duration = config_dict.get("segment_duration", config.segment_duration)
        config.playlist_type = config_dict.get("playlist_type", config.playlist_type)
        config.gop_size = config_dict.get("gop_size", config.gop_size)
        config.max_workers = config_dict.get("max_workers", config.max_workers)
        config.force_software_encoding = config_dict.get("force_software_encoding", config.force_software_encoding)
        config.disable_hwaccel = config_dict.get("disable_hwaccel", config.disable_hwaccel)
        config.encoder_threads = config_dict.get("encoder_threads", config.encoder_threads)
        config.preset = config_dict.get("preset", config.preset)
        config.crf = config_dict.get("crf", config.crf)
        config.convert_subtitles = config_dict.get("convert_subtitles", config.convert_subtitles)
        config.skip_bitmap_subtitles = config_dict.get("skip_bitmap_subtitles", config.skip_bitmap_subtitles)

        if profiles:
            config.bitrate_profiles = profiles

        return config