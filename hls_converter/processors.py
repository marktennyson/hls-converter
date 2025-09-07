"""
Media processing components for HLS Converter
===========================================

Individual processors for video, audio, and subtitle streams.
Each processor handles its specific media type with optimized settings.
"""

import os
import subprocess
import time
import multiprocessing as mp
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

from .config import HLSConfig, BitrateProfile
from .encoder_detector import EncoderDetector
from .media_analyzer import AudioTrack, SubtitleTrack

console = Console()


class BaseProcessor:
    """Base class for media processors."""
    
    def __init__(self, encoder_detector: EncoderDetector, config: HLSConfig):
        self.encoder_detector = encoder_detector
        self.config = config
        self.cpu_count = mp.cpu_count()
        self.optimal_workers = config.max_workers or max(2, min(self.cpu_count - 1, 8))


class VideoProcessor(BaseProcessor):
    """Processes video streams for HLS output."""
    
    def process_video_rendition(self, profile: BitrateProfile, input_file: Path, 
                              output_dir: Path, total_duration: float) -> Dict[str, Any]:
        """
        Process a single video rendition.
        
        Args:
            profile: Bitrate profile for this rendition
            input_file: Input video file
            output_dir: Output directory
            total_duration: Total video duration for progress calculation
            
        Returns:
            Dictionary containing processing results
        """
        folder = output_dir / profile.name
        folder.mkdir(parents=True, exist_ok=True)
        
        # Get best video encoder
        video_encoder, _ = self.encoder_detector.get_best_video_encoder()
        
        # Build FFmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-hide_banner", "-nostats", "-loglevel", "error",
            "-hwaccel", "auto",
            "-i", str(input_file),
            "-vf", f"scale={profile.scale_filter}",
            "-c:v", video_encoder,
        ]
        
        # Add encoder-specific options
        encoder_args = self.config.get_encoder_specific_args(video_encoder)
        cmd.extend(encoder_args)
        
        # Add bitrate and quality settings
        cmd.extend([
            "-b:v", f"{profile.max_bitrate_kbps}k",
            "-maxrate", f"{int(profile.max_bitrate_kbps * 1.2)}k",
            "-bufsize", f"{int(profile.max_bitrate_kbps * 2)}k",
            "-g", str(self.config.gop_size),
            "-keyint_min", str(self.config.gop_size),
            "-sc_threshold", "0",
            "-threads", str(max(2, self.cpu_count // self.optimal_workers)),
            "-an", "-sn",  # No audio/subtitles in video renditions
            "-hls_time", str(self.config.segment_duration),
            "-hls_playlist_type", self.config.playlist_type,
            "-hls_flags", "independent_segments+temp_file",
            "-hls_segment_filename", str(folder / "chunk_%03d.ts"),
            "-progress", "pipe:2",
            str(folder / "playlist.m3u8")
        ])
        
        return self._run_ffmpeg_process(cmd, profile.name, "video", total_duration)
    
    def _run_ffmpeg_process(self, cmd: List[str], name: str, process_type: str, 
                          total_duration: float) -> Dict[str, Any]:
        """Run FFmpeg process with enhanced progress monitoring and detailed logging."""
        start_time = time.time()
        process = None
        
        try:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                universal_newlines=True
            )
            
            # Enhanced progress tracking variables
            current_speed = "0x"
            current_time = "00:00:00"
            progress_seconds = 0.0
            frames_processed = 0
            current_fps = 0.0
            current_bitrate = "0kbits/s"
            current_q = "0.0"
            total_size = "0kB"
            last_log_time = time.time()
            log_interval = 3.0  # Log every 3 seconds for more frequent updates
            
            # Extract target resolution from command for logging
            target_resolution = "Unknown"
            for i, arg in enumerate(cmd):
                if arg == "-vf" and i + 1 < len(cmd):
                    scale_filter = cmd[i + 1]
                    if "scale=" in scale_filter:
                        target_resolution = scale_filter.split("scale=")[1].split(",")[0]
                        break
            
            console.print(f"[cyan]🎬 Starting {process_type} processing for {name} (Target: {target_resolution})...[/cyan]")
            
            while True:
                if process.stderr:
                    output = process.stderr.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        
                        # Parse comprehensive progress information from FFmpeg
                        if '=' in line:
                            # Handle multiple key=value pairs in one line
                            parts = line.split()
                            for part in parts:
                                if '=' in part:
                                    key, value = part.split('=', 1)
                                    
                                    if key == 'speed':
                                        current_speed = value
                                    elif key == 'out_time':
                                        current_time = value
                                        try:
                                            time_parts = current_time.split(':')
                                            if len(time_parts) == 3:
                                                hours, minutes, seconds = map(float, time_parts)
                                                progress_seconds = hours * 3600 + minutes * 60 + seconds
                                        except (ValueError, IndexError):
                                            pass
                                    elif key == 'frame':
                                        try:
                                            frames_processed = int(value)
                                        except (ValueError, TypeError):
                                            pass
                                    elif key == 'fps':
                                        try:
                                            current_fps = float(value)
                                        except (ValueError, TypeError):
                                            pass
                                    elif key == 'bitrate':
                                        current_bitrate = value
                                    elif key == 'q':
                                        current_q = value
                                    elif key == 'total_size':
                                        total_size = value
                        
                        # Log detailed progress periodically
                        current_log_time = time.time()
                        if current_log_time - last_log_time >= log_interval:
                            percentage = ""
                            eta = ""
                            
                            if total_duration > 0 and progress_seconds > 0:
                                pct = min(100, (progress_seconds / total_duration) * 100)
                                percentage = f"{pct:.1f}%"
                                
                                if pct > 0 and pct < 100:
                                    elapsed = current_log_time - start_time
                                    remaining = (elapsed / (pct / 100)) - elapsed
                                    eta_hours = int(remaining // 3600)
                                    eta_minutes = int((remaining % 3600) // 60)
                                    eta_seconds = int(remaining % 60)
                                    
                                    if eta_hours > 0:
                                        eta = f"ETA: {eta_hours:02d}:{eta_minutes:02d}:{eta_seconds:02d}"
                                    else:
                                        eta = f"ETA: {eta_minutes:02d}:{eta_seconds:02d}"
                            
                            # Enhanced logging with all available metrics
                            elapsed_time = current_log_time - start_time
                            elapsed_min, elapsed_sec = divmod(int(elapsed_time), 60)
                            elapsed_str = f"{elapsed_min:02d}:{elapsed_sec:02d}"
                            
                            # Build comprehensive status message
                            status_parts = [
                                f"[bold blue]{process_type.title()}[/bold blue] [cyan]{name}[/cyan]:",
                                f"[yellow]{current_time}[/yellow]"
                            ]
                            
                            if percentage:
                                status_parts.append(f"([green]{percentage}[/green])")
                            
                            if current_fps > 0:
                                status_parts.append(f"[magenta]{current_fps:.1f}fps[/magenta]")
                            
                            if current_bitrate != "0kbits/s":
                                status_parts.append(f"[blue]{current_bitrate}[/blue]")
                            
                            if current_speed != "0x":
                                status_parts.append(f"[red]{current_speed}[/red]")
                            
                            if frames_processed > 0:
                                status_parts.append(f"[dim]{frames_processed} frames[/dim]")
                            
                            if total_size != "0kB":
                                status_parts.append(f"[dim]{total_size}[/dim]")
                            
                            status_parts.append(f"[dim]({elapsed_str})[/dim]")
                            
                            if eta:
                                status_parts.append(f"[yellow]{eta}[/yellow]")
                            
                            console.print(" ".join(status_parts))
                            last_log_time = current_log_time
                else:
                    break
            
            return_code = process.wait()
            duration = time.time() - start_time
            
            if return_code == 0:
                # Calculate average processing stats
                avg_fps = frames_processed / duration if duration > 0 else 0
                speed_multiplier = 0
                if current_speed and current_speed.endswith('x'):
                    try:
                        speed_multiplier = float(current_speed[:-1])
                    except ValueError:
                        pass
                
                return {
                    "status": "success", 
                    "name": name, 
                    "duration": duration, 
                    "type": process_type, 
                    "speed": current_speed,
                    "frames_processed": frames_processed,
                    "avg_fps": avg_fps,
                    "final_bitrate": current_bitrate,
                    "output_size": total_size,
                    "target_resolution": target_resolution,
                    "speed_multiplier": speed_multiplier,
                    "quality": current_q
                }
            else:
                stderr_output = process.stderr.read() if process.stderr else "Unknown error"
                return {
                    "status": "error", 
                    "name": name, 
                    "duration": duration, 
                    "error": stderr_output, 
                    "type": process_type,
                    "target_resolution": target_resolution
                }
        
        except Exception as e:
            # Clean up process
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass
            
            duration = time.time() - start_time
            return {
                "status": "error", 
                "name": name, 
                "duration": duration, 
                "error": str(e), 
                "type": process_type
            }


class AudioProcessor(BaseProcessor):
    """Processes audio streams for HLS output."""
    
    def process_audio_rendition(self, track: AudioTrack, input_file: Path, 
                              output_dir: Path, total_duration: float) -> Dict[str, Any]:
        """
        Process a single audio rendition.
        
        Args:
            track: Audio track information
            input_file: Input video file
            output_dir: Output directory
            total_duration: Total duration for progress calculation
            
        Returns:
            Dictionary containing processing results
        """
        lang = track.language
        folder = output_dir / f"audio_{lang}"
        folder.mkdir(parents=True, exist_ok=True)
        
        # Get best audio encoder
        audio_encoder, _ = self.encoder_detector.get_best_audio_encoder()
        
        # Determine optimal audio bitrate based on input
        audio_bitrate = "160k"  # Default
        if track.bitrate:
            # Use input bitrate but cap it reasonably for streaming
            optimal_bitrate = min(track.bitrate, 320)
            audio_bitrate = f"{optimal_bitrate}k"
        
        # Build FFmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-hide_banner", "-nostats", "-loglevel", "error",
            "-hwaccel", "auto",
            "-i", str(input_file),
            "-map", f"0:a:{track.map_index}",
            "-c:a", audio_encoder,
            "-b:a", audio_bitrate,
            "-ar", "48000",  # Standard sample rate for HLS
            "-threads", str(max(2, self.cpu_count // self.optimal_workers)),
            "-vn", "-sn",  # No video/subtitles
            "-hls_time", str(self.config.segment_duration),
            "-hls_playlist_type", self.config.playlist_type,
            "-hls_flags", "independent_segments+temp_file",
            "-hls_segment_filename", str(folder / "chunk_%03d.ts"),
            "-progress", "pipe:2",
            str(folder / "playlist.m3u8")
        ]
        
        # Reuse video processor's FFmpeg runner
        video_processor = VideoProcessor(self.encoder_detector, self.config)
        return video_processor._run_ffmpeg_process(cmd, lang, "audio", total_duration)


class SubtitleProcessor(BaseProcessor):
    """Processes subtitle streams for HLS output."""
    
    def __init__(self, config: HLSConfig):
        self.config = config
    
    def convert_subtitles(self, input_file: Path, output_dir: Path, 
                         subtitle_tracks: List[SubtitleTrack]) -> None:
        """
        Convert subtitle tracks to WebVTT format.
        
        Args:
            input_file: Input video file
            output_dir: Output directory
            subtitle_tracks: List of subtitle tracks to convert
        """
        if not subtitle_tracks:
            console.print("[yellow]ℹ️  No subtitle tracks found[/yellow]")
            return
        
        console.print(f"[cyan]💬 Converting {len(subtitle_tracks)} subtitle tracks to WebVTT...[/cyan]")
        
        # Track language counts for duplicate handling
        lang_counts = defaultdict(int)
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Converting subtitles...", total=len(subtitle_tracks))
            
            for track in subtitle_tracks:
                track_start = time.time()
                lang_raw = track.language
                codec = track.codec.lower()
                
                # Skip bitmap subtitles if configured
                if self.config.skip_bitmap_subtitles and track.is_bitmap:
                    console.print(f"[yellow]⚠️  Skipping bitmap subtitle ({codec}) for {lang_raw}[/yellow]")
                    progress.advance(task)
                    continue
                
                # Sanitize language name
                lang = self._sanitize_language(lang_raw)
                
                # Handle duplicate languages
                suffix = f"_{lang_counts[lang]}" if lang_counts[lang] > 0 else ""
                output_file = output_dir / f"{lang}{suffix}.vtt"
                
                console.print(f"[dim]♾️  Converting {lang_raw} -> {output_file.name}[/dim]")
                
                # Build conversion command
                cmd = [
                    "ffmpeg", "-y", "-i", str(input_file),
                    "-map", f"0:s:{track.map_index}",
                    "-vn", "-an",  # No video/audio
                    "-c:s", "webvtt",
                    str(output_file)
                ]
                
                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
                    track_duration = time.time() - track_start
                    console.print(f"[green]✅ Created {output_file.name} in {track_duration:.1f}s[/green]")
                    lang_counts[lang] += 1
                    
                except subprocess.CalledProcessError as e:
                    track_duration = time.time() - track_start
                    error_msg = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
                    console.print(
                        f"[red]❌ Failed {lang_raw} ({codec}) after {track_duration:.1f}s: "
                        f"{error_msg[:100]}...[/red]"
                    )
                except subprocess.TimeoutExpired:
                    console.print(f"[red]⏰ Timeout converting {lang_raw} ({codec})[/red]")
                
                progress.advance(task)
        
        console.print("[green]✅ Subtitle conversion completed[/green]")
    
    def _sanitize_language(self, lang: str) -> str:
        """Sanitize language code for filename usage."""
        # Common language code mappings
        lang_map = {
            'eng': 'english', 'en': 'english',
            'spa': 'spanish', 'es': 'spanish',
            'fre': 'french', 'fr': 'french',
            'ger': 'german', 'de': 'german',
            'ita': 'italian', 'it': 'italian',
            'por': 'portuguese', 'pt': 'portuguese',
            'rus': 'russian', 'ru': 'russian',
            'chi': 'chinese', 'zh': 'chinese',
            'jpn': 'japanese', 'ja': 'japanese',
            'kor': 'korean', 'ko': 'korean',
            'ara': 'arabic', 'ar': 'arabic',
            'hin': 'hindi', 'hi': 'hindi'
        }
        
        # Clean and normalize
        cleaned = lang.lower().strip()
        normalized = lang_map.get(cleaned, cleaned)
        
        # Keep only alphanumeric, dash, underscore
        sanitized = "".join(
            ch if (ch.isalnum() or ch in ("-", "_")) else "_" 
            for ch in normalized
        )
        
        return sanitized or "english"