"""
Media analysis utilities for HLS Converter
==========================================

Analyzes input media files to extract metadata, video properties,
audio tracks, and subtitle information.
"""

import subprocess
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from rich.console import Console

console = Console()


@dataclass
class VideoInfo:
    """Video stream information."""
    width: int
    height: int
    duration: float
    fps: float
    bitrate: Optional[int] = None
    codec: Optional[str] = None
    
    @property
    def resolution(self) -> Tuple[int, int]:
        return (self.width, self.height)
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 1.0


@dataclass  
class AudioTrack:
    """Audio track information."""
    index: int
    language: str
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    
    @property
    def map_index(self) -> int:
        """FFmpeg map index for this track."""
        return self.index


@dataclass
class SubtitleTrack:
    """Subtitle track information."""
    index: int
    language: str
    codec: str
    
    @property
    def map_index(self) -> int:
        """FFmpeg map index for this track."""
        return self.index
    
    @property
    def is_bitmap(self) -> bool:
        """Check if subtitle is bitmap-based (cannot be converted to text)."""
        bitmap_codecs = {"hdmv_pgs_subtitle", "dvd_subtitle", "dvb_subtitle"}
        return self.codec.lower() in bitmap_codecs


@dataclass
class MediaInfo:
    """Complete media file information."""
    video: Optional[VideoInfo]
    audio_tracks: List[AudioTrack]
    subtitle_tracks: List[SubtitleTrack]
    format_name: Optional[str] = None
    file_size: Optional[int] = None


class MediaAnalyzer:
    """Analyzes media files using FFprobe."""
    
    def __init__(self):
        self._ffprobe_timeout = 30
    
    def analyze(self, input_file: Path) -> MediaInfo:
        """
        Analyze a media file and return comprehensive information.
        
        Args:
            input_file: Path to the media file to analyze
            
        Returns:
            MediaInfo object containing all relevant information
        """
        console.print(f"[cyan]🔍 Analyzing media file: {input_file.name}[/cyan]")
        
        # Get basic format information
        format_info = self._get_format_info(input_file)
        
        # Get stream information
        streams = self._get_streams(input_file)
        
        # Parse streams
        video_info = None
        audio_tracks = []
        subtitle_tracks = []
        
        audio_index = 0
        subtitle_index = 0
        
        for stream in streams:
            codec_type = stream.get('codec_type', '').lower()
            
            if codec_type == 'video' and video_info is None:
                video_info = self._parse_video_stream(stream)
            elif codec_type == 'audio':
                audio_track = self._parse_audio_stream(stream, audio_index)
                audio_tracks.append(audio_track)
                audio_index += 1
            elif codec_type == 'subtitle':
                subtitle_track = self._parse_subtitle_stream(stream, subtitle_index)
                subtitle_tracks.append(subtitle_track)
                subtitle_index += 1
        
        # Get file size
        file_size = input_file.stat().st_size if input_file.exists() else None
        
        media_info = MediaInfo(
            video=video_info,
            audio_tracks=audio_tracks,
            subtitle_tracks=subtitle_tracks,
            format_name=format_info.get('format_name'),
            file_size=file_size
        )
        
        self._log_analysis_results(media_info, input_file)
        return media_info
    
    def _get_format_info(self, input_file: Path) -> Dict:
        """Get format information using ffprobe."""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_format',
            '-of', 'json',
            str(input_file)
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=self._ffprobe_timeout
            )
            data = json.loads(result.stdout)
            return data.get('format', {})
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            console.print(f"[red]⚠️  Error getting format info: {e}[/red]")
            return {}
    
    def _get_streams(self, input_file: Path) -> List[Dict]:
        """Get all stream information using ffprobe.""" 
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_streams',
            '-of', 'json',
            str(input_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self._ffprobe_timeout
            )
            data = json.loads(result.stdout)
            return data.get('streams', [])
        except (subprocess.CalledProcessError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            console.print(f"[red]⚠️  Error getting stream info: {e}[/red]")
            return []
    
    def _parse_video_stream(self, stream: Dict) -> VideoInfo:
        """Parse video stream information."""
        width = int(stream.get('width', 0))
        height = int(stream.get('height', 0))
        
        # Get duration (prefer stream duration, fallback to format duration)
        duration_str = stream.get('duration')
        duration = float(duration_str) if duration_str else 0.0
        
        # Get FPS
        fps_str = stream.get('avg_frame_rate', '0/1')
        try:
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den) if float(den) != 0 else 0.0
            else:
                fps = float(fps_str)
        except (ValueError, ZeroDivisionError):
            fps = 0.0
        
        # Get bitrate
        bitrate_str = stream.get('bit_rate')
        bitrate = int(bitrate_str) // 1000 if bitrate_str and bitrate_str.isdigit() else None
        
        codec = stream.get('codec_name')
        
        return VideoInfo(
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            bitrate=bitrate,
            codec=codec
        )
    
    def _parse_audio_stream(self, stream: Dict, index: int) -> AudioTrack:
        """Parse audio stream information."""
        tags = stream.get('tags', {})
        language = tags.get('language', f'und_{index}')
        
        # Get audio properties
        codec = stream.get('codec_name')
        
        bitrate_str = stream.get('bit_rate')
        bitrate = int(bitrate_str) // 1000 if bitrate_str and bitrate_str.isdigit() else None
        
        sample_rate_str = stream.get('sample_rate')
        sample_rate = int(sample_rate_str) if sample_rate_str and sample_rate_str.isdigit() else None
        
        channels = stream.get('channels')
        
        return AudioTrack(
            index=index,
            language=language,
            codec=codec,
            bitrate=bitrate,
            sample_rate=sample_rate,
            channels=channels
        )
    
    def _parse_subtitle_stream(self, stream: Dict, index: int) -> SubtitleTrack:
        """Parse subtitle stream information."""
        tags = stream.get('tags', {})
        language = tags.get('language', f'und_{index}')
        codec = stream.get('codec_name', '')
        
        return SubtitleTrack(
            index=index,
            language=language,
            codec=codec
        )
    
    def _log_analysis_results(self, media_info: MediaInfo, input_file: Path):
        """Log analysis results to console.""" 
        if media_info.video:
            v = media_info.video
            bitrate_info = f" @ {v.bitrate}kbps" if v.bitrate else ""
            console.print(f"[green]📺 Video: {v.width}x{v.height} ({v.fps:.1f}fps){bitrate_info}[/green]")
        
        if media_info.audio_tracks:
            console.print(f"[green]🎵 Found {len(media_info.audio_tracks)} audio track(s):[/green]")
            for track in media_info.audio_tracks:
                bitrate_info = f" @ {track.bitrate}kbps" if track.bitrate else ""
                channels_info = f" ({track.channels}ch)" if track.channels else ""
                console.print(f"  [dim]🎧 Track {track.index}: {track.language} ({track.codec}){bitrate_info}{channels_info}[/dim]")
        
        if media_info.subtitle_tracks:
            console.print(f"[green]💬 Found {len(media_info.subtitle_tracks)} subtitle track(s):[/green]") 
            for track in media_info.subtitle_tracks:
                bitmap_info = " (bitmap)" if track.is_bitmap else ""
                console.print(f"  [dim]📄 Track {track.index}: {track.language} ({track.codec}){bitmap_info}[/dim]")
        
        if media_info.file_size:
            size_mb = media_info.file_size / (1024 * 1024)
            console.print(f"[green]📊 File size: {size_mb:.1f} MB[/green]")
    
    def get_optimal_resolutions(self, video_info: VideoInfo) -> List[str]:
        """
        Determine optimal resolution ladder based on input video.
        
        Args:
            video_info: Video information from analysis
            
        Returns:
            List of resolution names suitable for the input video
        """
        if not video_info:
            return ["480p", "720p"]  # Safe fallback
        
        input_height = video_info.height
        
        # Standard resolution ladder
        all_resolutions = [
            (144, "144p"), (240, "240p"), (360, "360p"), (480, "480p"),
            (720, "720p"), (1080, "1080p"), (1440, "1440p"), (2160, "2160p")
        ]
        
        # Select resolutions that don't exceed input height significantly
        suitable = []
        for height, name in all_resolutions:
            if height <= input_height * 1.1:  # Allow slight upscaling
                suitable.append(name)
        
        # Ensure we have at least 2 resolutions for adaptive streaming
        if len(suitable) < 2:
            suitable = ["480p", "720p"] if input_height >= 720 else ["360p", "480p"]
        
        return suitable