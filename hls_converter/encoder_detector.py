"""
Hardware and software encoder detection for HLS Converter
========================================================

Automatically detects available video and audio encoders, prioritizing
hardware acceleration when available.
"""

import subprocess
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class EncoderInfo:
    """Information about an available encoder."""
    codec: str
    name: str
    type: str  # 'hardware' or 'software'
    available: bool = False


class EncoderDetector:
    """Detects and manages available video and audio encoders."""
    
    def __init__(self):
        self._cache: Optional[Dict] = None
        self._test_timeout = 10
    
    def detect_encoders(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Detect all available encoders.
        
        Args:
            force_refresh: Force re-detection even if cached results exist
            
        Returns:
            Dictionary containing video and audio encoder information
        """
        if self._cache and not force_refresh:
            return self._cache
        
        console.print("[bold cyan]🔍 Detecting available encoders...[/bold cyan]")
        
        encoders = {
            'video': {'hardware': [], 'software': []},
            'audio': {'hardware': [], 'software': []}
        }
        
        # Video encoder candidates (ordered by preference)
        video_candidates = [
            # Hardware encoders
            EncoderInfo('h264_videotoolbox', 'VideoToolbox (macOS)', 'hardware'),
            EncoderInfo('h264_nvenc', 'NVIDIA NVENC', 'hardware'),
            EncoderInfo('h264_qsv', 'Intel QuickSync', 'hardware'),
            EncoderInfo('h264_vaapi', 'VAAPI (Linux)', 'hardware'),
            EncoderInfo('h264_amf', 'AMD AMF', 'hardware'),
            # Software encoders
            EncoderInfo('libx264', 'x264 Software', 'software'),
            EncoderInfo('h264', 'Generic H.264', 'software'),
        ]
        
        # Audio encoder candidates  
        audio_candidates = [
            # Hardware encoders
            EncoderInfo('aac_at', 'AudioToolbox AAC (macOS)', 'hardware'),
            # Software encoders
            EncoderInfo('aac', 'Generic AAC', 'software'),
            EncoderInfo('libfdk_aac', 'Fraunhofer FDK AAC', 'software'),
        ]
        
        # Test video encoders
        with console.status("[bold green]🧪 Testing video encoders..."):
            for encoder in video_candidates:
                encoder.available = self._test_encoder(encoder.codec, 'video')
                if encoder.available:
                    encoders['video'][encoder.type].append((encoder.codec, encoder.name))
                    console.print(f"[green]✅ Video: {encoder.name} ({encoder.codec})[/green]")
                else:
                    console.print(f"[dim]❌ Video: {encoder.name} ({encoder.codec})[/dim]")
        
        # Test audio encoders
        with console.status("[bold green]🧪 Testing audio encoders..."):
            for encoder in audio_candidates:
                encoder.available = self._test_encoder(encoder.codec, 'audio')
                if encoder.available:
                    encoders['audio'][encoder.type].append((encoder.codec, encoder.name))
                    console.print(f"[green]✅ Audio: {encoder.name} ({encoder.codec})[/green]")
                else:
                    console.print(f"[dim]❌ Audio: {encoder.name} ({encoder.codec})[/dim]")
        
        # Select best available encoders
        result = self._select_best_encoders(encoders)
        self._cache = result
        return result
    
    def _test_encoder(self, encoder: str, media_type: str) -> bool:
        """Test if a specific encoder is available."""
        try:
            cmd = ['ffmpeg', '-hide_banner', '-f', 'lavfi']
            
            if media_type == 'video':
                cmd.extend(['-i', 'testsrc=duration=0.1:size=320x240:rate=1'])
                cmd.extend(['-c:v', encoder, '-t', '0.1', '-f', 'null', '-'])
            else:  # audio
                cmd.extend(['-i', 'sine=frequency=1000:duration=0.1'])
                cmd.extend(['-c:a', encoder, '-t', '0.1', '-f', 'null', '-'])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._test_timeout
            )
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _select_best_encoders(self, encoders: Dict) -> Dict:
        """Select the best available encoders and format result."""
        video_encoder = None
        video_name = "Unknown"
        audio_encoder = None  
        audio_name = "Unknown"
        
        # Select video encoder (prefer hardware)
        if encoders['video']['hardware']:
            video_encoder = encoders['video']['hardware'][0][0]
            video_name = encoders['video']['hardware'][0][1]
            console.print(f"[bold green]🚀 Selected video encoder: {video_name}[/bold green]")
        elif encoders['video']['software']:
            video_encoder = encoders['video']['software'][0][0]
            video_name = encoders['video']['software'][0][1]
            console.print(f"[yellow]⚡ Selected video encoder: {video_name} (software fallback)[/yellow]")
        else:
            video_encoder = 'libx264'
            video_name = 'x264 Software (fallback)'
            console.print(f"[red]⚠️  No encoders detected, using fallback: {video_name}[/red]")
        
        # Select audio encoder (prefer hardware)
        if encoders['audio']['hardware']:
            audio_encoder = encoders['audio']['hardware'][0][0]
            audio_name = encoders['audio']['hardware'][0][1]
            console.print(f"[bold green]🎵 Selected audio encoder: {audio_name}[/bold green]")
        elif encoders['audio']['software']:
            audio_encoder = encoders['audio']['software'][0][0]
            audio_name = encoders['audio']['software'][0][1]
            console.print(f"[yellow]🎵 Selected audio encoder: {audio_name} (software fallback)[/yellow]")
        else:
            audio_encoder = 'aac'
            audio_name = 'Generic AAC (fallback)'
            console.print(f"[red]⚠️  No audio encoders detected, using fallback: {audio_name}[/red]")
        
        return {
            'video_encoder': video_encoder,
            'audio_encoder': audio_encoder,
            'video_name': video_name,
            'audio_name': audio_name,
            'all_encoders': encoders
        }
    
    def get_best_video_encoder(self) -> Tuple[str, str]:
        """Get the best available video encoder."""
        if not self._cache:
            self.detect_encoders()
        return self._cache['video_encoder'], self._cache['video_name']
    
    def get_best_audio_encoder(self) -> Tuple[str, str]:
        """Get the best available audio encoder."""
        if not self._cache:
            self.detect_encoders()
        return self._cache['audio_encoder'], self._cache['audio_name']
    
    def is_hardware_encoder(self, encoder: str) -> bool:
        """Check if an encoder is hardware-accelerated."""
        hardware_encoders = {
            'h264_videotoolbox', 'h264_nvenc', 'h264_qsv', 
            'h264_vaapi', 'h264_amf', 'aac_at'
        }
        return encoder in hardware_encoders
    
    def get_encoder_info(self) -> Dict:
        """Get detailed information about detected encoders."""
        if not self._cache:
            self.detect_encoders()
        return self._cache