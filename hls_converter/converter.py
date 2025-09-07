"""
Main HLS Converter class
=======================

The main converter class that orchestrates the entire HLS conversion process
using the media analyzer, encoder detector, and configuration system.
"""

import time
import multiprocessing as mp
from pathlib import Path
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn, ProgressColumn
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

from .config import HLSConfig, BitrateProfile
from .encoder_detector import EncoderDetector
from .media_analyzer import MediaAnalyzer, MediaInfo
from .processors import VideoProcessor, AudioProcessor, SubtitleProcessor

console = Console()


class HLSConverter:
    """
    Professional HLS converter with automatic optimization and hardware acceleration.
    
    Features:
    - Automatic encoder detection and hardware acceleration
    - Dynamic bitrate adjustment based on input video characteristics
    - Multi-threaded parallel processing
    - Comprehensive logging and progress tracking
    - Subtitle conversion support
    """
    
    def __init__(self, config: Optional[HLSConfig] = None):
        """
        Initialize HLS converter.
        
        Args:
            config: Optional HLS configuration. If None, uses default configuration.
        """
        self.config = config or HLSConfig()
        self.encoder_detector = EncoderDetector()
        self.media_analyzer = MediaAnalyzer()
        
        # Processing components
        self.video_processor = VideoProcessor(self.encoder_detector, self.config)
        self.audio_processor = AudioProcessor(self.encoder_detector, self.config)
        self.subtitle_processor = SubtitleProcessor(self.config)
        
        # Performance settings
        self.cpu_count = mp.cpu_count()
        self.optimal_workers = self.config.max_workers or self.cpu_count
        
    def convert(self, input_file: str | Path, output_dir: str | Path, 
                resolutions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Convert video to HLS format with adaptive bitrate streaming.
        
        Args:
            input_file: Path to input video file
            output_dir: Directory to output HLS files
            resolutions: Optional list of resolutions to generate (e.g., ["720p", "1080p"])
                        If None, automatically determines based on input video
        
        Returns:
            Dictionary containing conversion results and statistics
        """
        input_path = Path(input_file)
        output_path = Path(output_dir)
        
        # Validate inputs
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Display banner
        self._show_banner()
        
        # Initialize timing
        start_time = time.time()
        step_timings = {}
        total_steps = 5
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True
        ) as overall_progress:
            overall_task = overall_progress.add_task(
                "[bold cyan]🎥 HLS Conversion Progress...", total=total_steps
            )
            
            # Step 1: Detect encoders
            step_start = time.time()
            console.print("[bold blue]Step 1/5: Detecting available encoders[/bold blue]")
            encoder_info = self.encoder_detector.detect_encoders()
            step_timings["Encoder Detection"] = time.time() - step_start
            overall_progress.advance(overall_task)
            
            # Step 2: Analyze media
            step_start = time.time()
            console.print("[bold blue]Step 2/5: Analyzing input media[/bold blue]")
            media_info = self.media_analyzer.analyze(input_path)
            step_timings["Media Analysis"] = time.time() - step_start
            overall_progress.advance(overall_task)
            
            # Step 3: Configure adaptive bitrates
            step_start = time.time()
            console.print("[bold blue]Step 3/5: Configuring adaptive bitrate profiles[/bold blue]")
            
            # Determine resolutions - prioritize user input
            if resolutions is None:
                # Only auto-determine if user didn't specify
                resolutions = self.media_analyzer.get_optimal_resolutions(media_info.video) if media_info.video is not None else []
            
            # Create adaptive bitrate profiles
            if media_info.video:
                adaptive_profiles = HLSConfig.create_adaptive_profiles(
                    media_info.video.width,
                    media_info.video.height,
                    media_info.video.bitrate
                )
                
                if resolutions:
                    # User specified resolutions - enforce them regardless of input
                    self.config.bitrate_profiles = [
                        profile for profile in adaptive_profiles
                        if profile.resolution_name in resolutions
                    ]
                    
                    # If user requested resolutions not in adaptive profiles, create them
                    missing_resolutions = set(resolutions) - {p.resolution_name for p in self.config.bitrate_profiles}
                    for res in missing_resolutions:
                        if res in ["2160p", "1440p", "1080p", "720p", "480p", "360p"]:
                            # Create profile for missing resolution
                            res_map = {
                                "2160p": (3840, 2160, 15000, 8000),
                                "1440p": (2560, 1440, 10000, 6000), 
                                "1080p": (1920, 1080, 5000, 3000),
                                "720p": (1280, 720, 3000, 1500),
                                "480p": (854, 480, 1500, 800),
                                "360p": (640, 360, 800, 400)
                            }
                            if res in res_map:
                                width, height, max_br, min_br = res_map[res]
                                profile = BitrateProfile(
                                    name=res.replace("p", ""),
                                    resolution=(width, height),
                                    max_bitrate_kbps=max_br,
                                    min_bitrate_kbps=min_br
                                )
                                self.config.bitrate_profiles.append(profile)
                else:
                    # No resolutions specified, use all adaptive profiles
                    self.config.bitrate_profiles = adaptive_profiles
            
            self._show_processing_config(media_info, encoder_info, resolutions)
            step_timings["Configuration"] = time.time() - step_start
            overall_progress.advance(overall_task)
            
            # Step 4: Process media streams
            step_start = time.time()
            console.print("[bold blue]Step 4/5: Processing video, audio, and subtitle streams[/bold blue]")
            
            # Process all streams in parallel
            self._process_streams(input_path, output_path, media_info)
            
            step_timings["Stream Processing"] = time.time() - step_start
            overall_progress.advance(overall_task)
            
            # Step 5: Create master playlist
            step_start = time.time()
            console.print("[bold blue]Step 5/5: Creating master playlist[/bold blue]")
            master_playlist_path = self._create_master_playlist(output_path, media_info.audio_tracks)
            step_timings["Playlist Creation"] = time.time() - step_start
            overall_progress.advance(overall_task)
        
        # Calculate final results
        total_duration = time.time() - start_time
        file_size_mb = media_info.file_size / (1024 * 1024) if media_info.file_size else 0
        processing_speed = file_size_mb / total_duration if total_duration > 0 else 0
        
        results = {
            "success": True,
            "input_file": str(input_path),
            "output_dir": str(output_path),
            "master_playlist": str(master_playlist_path),
            "total_duration": total_duration,
            "processing_speed_mbps": processing_speed,
            "resolutions_created": resolutions,
            "audio_tracks": len(media_info.audio_tracks),
            "subtitle_tracks": len(media_info.subtitle_tracks),
            "step_timings": step_timings,
            "encoder_info": encoder_info
        }
        
        self._show_completion_summary(results, step_timings, total_duration)
        return results
    
    def _show_banner(self):
        """Display application banner."""
        console.print(Panel(
            "[bold cyan]🎥 HLS Converter v1.0.0[/bold cyan]\n"
            "🚀 Professional adaptive bitrate streaming converter\n"
            "✨ Automatic hardware acceleration and optimization",
            title="🎬 HLS Converter",
            border_style="cyan"
        ))
    
    def _show_processing_config(self, media_info: MediaInfo, encoder_info: Dict, resolutions: List[str]):
        """Show processing configuration."""
        duration_str = ""
        if media_info.video and media_info.video.duration > 0:
            minutes, seconds = divmod(int(media_info.video.duration), 60)
            hours, minutes = divmod(minutes, 60)
            duration_str = f" (Duration: {hours:02d}:{minutes:02d}:{seconds:02d})"
        
        console.print(Panel(
            f"[bold cyan]🚀 Processing Configuration[/bold cyan]\n"
            f"💻 CPU Cores: {self.cpu_count}\n"
            f"⚡ Workers: {self.optimal_workers}\n"
            f"🎬 Video Encoder: {encoder_info['video_name']}\n"
            f"🎵 Audio Encoder: {encoder_info['audio_name']}\n"
            f"📺 Video Resolutions: {', '.join(resolutions)}\n"
            f"🎧 Audio Tracks: {len(media_info.audio_tracks)}\n"
            f"💬 Subtitle Tracks: {len(media_info.subtitle_tracks)}{duration_str}",
            title="🔧 Configuration",
            border_style="cyan"
        ))
    
    def _process_streams(self, input_path: Path, output_path: Path, media_info: MediaInfo):
        """Process all media streams in parallel."""
        tasks = []
        
        # Prepare video tasks
        video_tasks = [
            (profile, input_path, output_path, media_info.video.duration if media_info.video else 0.0)
            for profile in self.config.bitrate_profiles
        ]
        
        # Prepare audio tasks
        audio_tasks = [
            (track, input_path, output_path, media_info.video.duration if media_info.video else 0.0)
            for track in media_info.audio_tracks
        ]
        
        total_tasks = len(video_tasks) + len(audio_tasks)
        completed_tasks = 0

        # Unified progress for renditions with extra columns for fps and speed using task fields
        class StatsColumn(ProgressColumn):
            def render(self, task):  # type: ignore[override]
                speed = task.fields.get("speed", "—")
                fps = task.fields.get("fps", "—")
                t = task.fields.get("time", "00:00:00")
                total_t = task.fields.get("total_time", "—")
                return Text(f"t {t}/{total_t} • fps {fps} • {speed}")

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            StatsColumn(),
            console=console,
            transient=False
        ) as progress:
            main_task = progress.add_task("[cyan]Processing all renditions...", total=total_tasks)

            # Process video renditions
            if video_tasks:
                console.print(f"[bold blue]🎬 Processing {len(video_tasks)} video renditions...[/bold blue]")
                with ThreadPoolExecutor(max_workers=self.optimal_workers) as executor:
                    # Create a per-rendition task row to update in-place
                    task_rows = {}
                    futures = []
                    for profile, in_path, out_path, duration in video_tasks:
                        # Precompute total duration string (HH:MM:SS)
                        if duration and duration > 0:
                            mins, secs = divmod(int(duration), 60)
                            hrs, mins = divmod(mins, 60)
                            total_time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
                        else:
                            total_time_str = "—"

                        row_id = progress.add_task(
                            f"[cyan]Video {profile.name} ({profile.resolution[0]}x{profile.resolution[1]})",
                            total=duration if duration and duration > 0 else 1.0,
                            speed="—",
                            fps="—",
                            time="00:00:00",
                            total_time=total_time_str,
                        )
                        task_rows[profile.name] = row_id
                        futures.append(
                            executor.submit(
                                self.video_processor.process_video_rendition,
                                profile, in_path, out_path, duration,
                                progress, row_id
                            )
                        )
                    future_to_task = {fut: None for fut in futures}

                    for future in as_completed(future_to_task):
                        result = future.result()
                        completed_tasks += 1

                        if result["status"] == "success":
                            # Build comprehensive completion message
                            details = [f"{result['duration']:.1f}s"]

                            if result.get('speed'):
                                details.append(f"speed: {result['speed']}")

                            if result.get('avg_fps', 0) > 0:
                                details.append(f"avg: {result['avg_fps']:.1f}fps")

                            if result.get('frames_processed', 0) > 0:
                                details.append(f"{result['frames_processed']} frames")

                            if result.get('final_bitrate') and result['final_bitrate'] != "0kbits/s":
                                details.append(f"bitrate: {result['final_bitrate']}")

                            if result.get('target_resolution') and result['target_resolution'] != "Unknown":
                                details.append(f"res: {result['target_resolution']}")

                            details_str = f" ({', '.join(details)})" if details else ""
                            console.print(f"[green]✅ Video {result['name']} completed{details_str}[/green]")
                        else:
                            console.print(f"[red]❌ Video {result['name']} failed: {result['error']}[/red]")

                        progress.advance(main_task)

            # Process audio renditions
            if audio_tasks:
                console.print(f"[bold blue]🎵 Processing {len(audio_tasks)} audio renditions...[/bold blue]")
                with ThreadPoolExecutor(max_workers=self.optimal_workers) as executor:
                    task_rows = {}
                    futures = []
                    for track, in_path, out_path, duration in audio_tasks:
                        label = f"[cyan]Audio {track.language}"
                        if duration and duration > 0:
                            mins, secs = divmod(int(duration), 60)
                            hrs, mins = divmod(mins, 60)
                            total_time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
                        else:
                            total_time_str = "—"

                        row_id = progress.add_task(
                            label,
                            total=duration if duration and duration > 0 else 1.0,
                            speed="—",
                            fps="—",
                            time="00:00:00",
                            total_time=total_time_str,
                        )
                        task_rows[track.language] = row_id
                        futures.append(
                            executor.submit(
                                self.audio_processor.process_audio_rendition,
                                track, in_path, out_path, duration,
                                progress, row_id
                            )
                        )
                    future_to_task = {fut: None for fut in futures}

                    for future in as_completed(future_to_task):
                        result = future.result()
                        completed_tasks += 1

                        if result["status"] == "success":
                            # Build comprehensive completion message for audio
                            details = [f"{result['duration']:.1f}s"]

                            if result.get('speed'):
                                details.append(f"speed: {result['speed']}")

                            if result.get('final_bitrate') and result['final_bitrate'] != "0kbits/s":
                                details.append(f"bitrate: {result['final_bitrate']}")

                            if result.get('output_size') and result['output_size'] != "0kB":
                                details.append(f"size: {result['output_size']}")

                            details_str = f" ({', '.join(details)})" if details else ""
                            console.print(f"[green]✅ Audio {result['name']} completed{details_str}[/green]")
                        else:
                            console.print(f"[red]❌ Audio {result['name']} failed: {result['error']}[/red]")

                        progress.advance(main_task)
        
        # Process subtitles (if enabled)
        if self.config.convert_subtitles and media_info.subtitle_tracks:
            console.print("[bold blue]💬 Converting subtitles to WebVTT...[/bold blue]")
            self.subtitle_processor.convert_subtitles(input_path, output_path, media_info.subtitle_tracks)
        
        console.print("[bold green]🎉 All stream processing completed![/bold green]")
    
    def _create_master_playlist(self, output_dir: Path, audio_tracks: List) -> Path:
        """Create HLS master playlist."""
        master_path = output_dir / "master.m3u8"
        lines = ["#EXTM3U"]
        
        # Audio groups
        for track in audio_tracks:
            lang = track.language
            is_default = "YES" if track == audio_tracks[0] else "NO"
            lines.append(
                f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="{lang}",'
                f'DEFAULT={is_default},AUTOSELECT=YES,LANGUAGE="{lang}",'
                f'URI="audio_{lang}/playlist.m3u8"'
            )
        
        # Video streams
        for profile in self.config.bitrate_profiles:
            bandwidth = profile.max_bitrate_kbps * 1000  # Convert to bps
            resolution_str = f"{profile.resolution[0]}x{profile.resolution[1]}"
            lines.append(
                f'#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},'
                f'RESOLUTION={resolution_str},CODECS="avc1.640029",AUDIO="audio"'
            )
            lines.append(f'{profile.name}/playlist.m3u8')
        
        with open(master_path, 'w') as f:
            f.write('\n'.join(lines))
        
        console.print(f"[green]✅ Created master playlist: {master_path}[/green]")
        return master_path
    
    def _show_completion_summary(self, results: Dict, step_timings: Dict, total_duration: float):
        """Show conversion completion summary."""
        # Results table
        table = Table(title="Conversion Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Processing Time", f"{total_duration:.1f}s")
        table.add_row("Processing Speed", f"{results['processing_speed_mbps']:.2f} MB/s")
        table.add_row("Video Resolutions", str(len(results['resolutions_created'])))
        table.add_row("Audio Tracks", str(results['audio_tracks']))
        table.add_row("Subtitle Tracks", str(results['subtitle_tracks']))
        table.add_row("CPU Workers Used", f"{self.optimal_workers}/{self.cpu_count}")
        table.add_row("Master Playlist", results['master_playlist'])
        
        console.print("\n")
        console.print(table)
        
        # Step timing breakdown
        timing_table = Table(title="Performance Breakdown")
        timing_table.add_column("Step", style="cyan")
        timing_table.add_column("Duration", style="green")
        timing_table.add_column("Percentage", style="yellow")
        
        for step_name, duration in step_timings.items():
            percentage = (duration / total_duration) * 100
            timing_table.add_row(step_name, f"{duration:.2f}s", f"{percentage:.1f}%")
        
        console.print("\n")
        console.print(timing_table)
        
        # Success message
        console.print("\n")
        console.print(Panel(
            f"[bold green]🎉 HLS conversion completed successfully![/bold green]\n"
            f"📋 Master playlist: {results['master_playlist']}\n"
            f"⚡ Processing speed: {results['processing_speed_mbps']:.2f} MB/s",
            title="🎉 Success",
            border_style="green"
        ))