"""
Command Line Interface for HLS Converter
========================================

Professional CLI with comprehensive argument parsing, help system,
and configuration management.
"""

import sys
import argparse
import json
import logging
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .converter import HLSConverter
from .config import HLSConfig

console = Console()


class HLSConverterCLI:
    """Command line interface for HLS Converter."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser."""
        parser = argparse.ArgumentParser(
            prog='hls-converter',
            description='Professional HLS (HTTP Live Streaming) converter with automatic optimization',
            epilog='Examples:\n'
                   '  hls-converter input.mp4\n'
                   '  hls-converter input.mp4 --output /path/to/output\n'
                   '  hls-converter input.mp4 --resolutions 720p,1080p\n'
                   '  hls-converter input.mp4 --config custom_config.json\n'
                   '  hls-converter --list-encoders\n',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Version
        parser.add_argument(
            '--version', '-v',
            action='version',
            version=f'%(prog)s {__version__}'
        )
        
        # Input/Output
        parser.add_argument(
            'input',
            nargs='?',
            type=Path,
            help='Input video file path'
        )
        
        parser.add_argument(
            '--output', '-o',
            type=Path,
            help='Output directory (default: same as input filename without extension)'
        )
        
        # Quality settings
        parser.add_argument(
            '--resolutions', '-r',
            type=str,
            help='Comma-separated list of resolutions (e.g., "720p,1080p"). '
                 'Available: 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p. '
                 'If not specified, automatically determined from input video.'
        )
        
        parser.add_argument(
            '--preset', '-p',
            choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
            default='fast',
            help='Encoding preset (default: fast)'
        )
        
        parser.add_argument(
            '--crf',
            type=int,
            default=23,
            help='Constant Rate Factor for software encoding (default: 23, range: 0-51)'
        )
        
        # Processing settings
        parser.add_argument(
            '--workers', '-w',
            type=int,
            help='Number of parallel workers (default: auto-detect optimal)'
        )
        
        parser.add_argument(
            '--segment-duration',
            type=int,
            default=2,
            help='HLS segment duration in seconds (default: 2)'
        )
        
        parser.add_argument(
            '--gop-size',
            type=int,
            default=48,
            help='GOP (Group of Pictures) size (default: 48)'
        )
        
        # Feature toggles
        parser.add_argument(
            '--no-subtitles',
            action='store_true',
            help='Skip subtitle conversion'
        )
        
        parser.add_argument(
            '--include-bitmap-subtitles',
            action='store_true',
            help='Include bitmap subtitles (may require OCR, usually skipped)'
        )
        
        # Configuration
        parser.add_argument(
            '--config', '-c',
            type=Path,
            help='JSON configuration file path'
        )
        
        parser.add_argument(
            '--save-config',
            type=Path,
            help='Save current configuration to JSON file'
        )
        
        # Information commands
        parser.add_argument(
            '--list-encoders',
            action='store_true',
            help='List available video and audio encoders'
        )
        
        parser.add_argument(
            '--analyze-only',
            action='store_true',
            help='Only analyze input file without conversion'
        )
        
        # Verbose/quiet modes
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Reduce output verbosity'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging'
        )
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI application.
        
        Args:
            args: Command line arguments (defaults to sys.argv)
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            parsed_args = self.parser.parse_args(args)
            return self._execute_command(parsed_args)
        
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
            return 130
        
        except Exception as e:
            if parsed_args.debug if 'parsed_args' in locals() else False:
                console.print_exception()
            else:
                console.print(f"[red]❌ Error: {e}[/red]")
            return 1
    
    def _execute_command(self, args: argparse.Namespace) -> int:
        """Execute the parsed command."""
        # Setup logging
        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
        elif args.quiet:
            logging.basicConfig(level=logging.WARNING)
        
        # Handle information commands first
        if args.list_encoders:
            return self._list_encoders()
        
        # Validate input file requirement
        if not args.input:
            console.print("[red]❌ Error: Input file is required[/red]")
            console.print("Use --help for usage information")
            return 1
        
        if not args.input.exists():
            console.print(f"[red]❌ Error: Input file not found: {args.input}[/red]")
            return 1
        
        # Load or create configuration
        config = self._load_configuration(args)
        
        # Save configuration if requested
        if args.save_config:
            self._save_configuration(config, args.save_config)
            console.print(f"[green]✅ Configuration saved to {args.save_config}[/green]")
            if not args.analyze_only:
                return 0
        
        # Determine output directory
        output_dir = args.output or args.input.with_suffix('')
        
        # Parse resolutions
        resolutions = None
        if args.resolutions:
            resolutions = [r.strip() for r in args.resolutions.split(',')]
            valid_resolutions = {'144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p'}
            invalid = [r for r in resolutions if r not in valid_resolutions]
            if invalid:
                console.print(f"[red]❌ Invalid resolution(s): {', '.join(invalid)}[/red]")
                console.print(f"Valid options: {', '.join(sorted(valid_resolutions))}")
                return 1
        
        # Create converter
        converter = HLSConverter(config)
        
        # Handle analyze-only mode
        if args.analyze_only:
            return self._analyze_file(converter, args.input)
        
        # Perform conversion
        try:
            results = converter.convert(args.input, output_dir, resolutions)
            
            if results['success']:
                console.print(f"\n[bold green]🎉 Conversion completed successfully![/bold green]")
                console.print(f"📋 Master playlist: {results['master_playlist']}")
                return 0
            else:
                console.print("[red]❌ Conversion failed[/red]")
                return 1
                
        except Exception as e:
            console.print(f"[red]❌ Conversion error: {e}[/red]")
            if args.debug:
                console.print_exception()
            return 1
    
    def _load_configuration(self, args: argparse.Namespace) -> HLSConfig:
        """Load configuration from file or create from arguments."""
        # Start with default configuration
        if args.config and args.config.exists():
            try:
                with open(args.config, 'r') as f:
                    config_dict = json.load(f)
                config = HLSConfig.from_dict(config_dict)
                console.print(f"[green]📄 Loaded configuration from {args.config}[/green]")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                console.print(f"[yellow]⚠️  Could not load config file: {e}[/yellow]")
                config = HLSConfig()
        else:
            config = HLSConfig()
        
        # Override with command line arguments
        if args.preset:
            config.preset = args.preset
        if args.crf:
            config.crf = args.crf
        if args.workers:
            config.max_workers = args.workers
        if args.segment_duration:
            config.segment_duration = args.segment_duration
        if args.gop_size:
            config.gop_size = args.gop_size
        if args.no_subtitles:
            config.convert_subtitles = False
        if args.include_bitmap_subtitles:
            config.skip_bitmap_subtitles = False
        
        return config
    
    def _save_configuration(self, config: HLSConfig, config_file: Path):
        """Save configuration to JSON file."""
        config_dict = config.to_dict()
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def _list_encoders(self) -> int:
        """List available encoders."""
        console.print(Panel(
            "[bold cyan]🔍 Detecting Available Encoders[/bold cyan]\n"
            "This may take a few moments...",
            title="Encoder Detection",
            border_style="cyan"
        ))
        
        from .encoder_detector import EncoderDetector
        detector = EncoderDetector()
        encoder_info = detector.detect_encoders()
        
        # Create encoders table
        table = Table(title="Available Encoders")
        table.add_column("Type", style="cyan")
        table.add_column("Category", style="yellow")
        table.add_column("Codec", style="green")
        table.add_column("Name", style="white")
        table.add_column("Selected", style="bold magenta")
        
        # Add video encoders
        for category in ['hardware', 'software']:
            for codec, name in encoder_info['all_encoders']['video'][category]:
                is_selected = "✅" if codec == encoder_info['video_encoder'] else ""
                table.add_row("Video", category.title(), codec, name, is_selected)
        
        # Add audio encoders
        for category in ['hardware', 'software']:
            for codec, name in encoder_info['all_encoders']['audio'][category]:
                is_selected = "✅" if codec == encoder_info['audio_encoder'] else ""
                table.add_row("Audio", category.title(), codec, name, is_selected)
        
        console.print("\n")
        console.print(table)
        
        # Show selected encoders
        console.print("\n")
        console.print(Panel(
            f"[bold green]🚀 Selected Video Encoder:[/bold green] {encoder_info['video_name']}\n"
            f"[bold green]🎵 Selected Audio Encoder:[/bold green] {encoder_info['audio_name']}",
            title="Current Selection",
            border_style="green"
        ))
        
        return 0
    
    def _analyze_file(self, converter: HLSConverter, input_file: Path) -> int:
        """Analyze input file without conversion."""
        console.print(Panel(
            f"[bold cyan]🔍 Analyzing Media File[/bold cyan]\n"
            f"File: {input_file}",
            title="Media Analysis",
            border_style="cyan"
        ))
        
        media_info = converter.media_analyzer.analyze(input_file)
        
        # Show recommended resolutions
        if media_info.video:
            recommended = converter.media_analyzer.get_optimal_resolutions(media_info.video)
            console.print(f"\n[bold yellow]📺 Recommended resolutions:[/bold yellow] {', '.join(recommended)}")
            
            # Show bitrate profiles that would be created
            profiles = HLSConfig.create_adaptive_profiles(
                media_info.video.width,
                media_info.video.height,
                media_info.video.bitrate
            )
            
            if profiles:
                console.print("\n[bold cyan]🎬 Adaptive Bitrate Profiles:[/bold cyan]")
                profile_table = Table()
                profile_table.add_column("Resolution", style="cyan")
                profile_table.add_column("Max Bitrate", style="green")
                profile_table.add_column("Min Bitrate", style="yellow")
                profile_table.add_column("Dimensions", style="white")
                
                for profile in profiles:
                    if profile.resolution_name in recommended:
                        profile_table.add_row(
                            profile.resolution_name,
                            f"{profile.max_bitrate_kbps}k",
                            f"{profile.min_bitrate_kbps}k",
                            f"{profile.resolution[0]}x{profile.resolution[1]}"
                        )
                
                console.print(profile_table)
        
        return 0


def main():
    """Main entry point for the CLI application."""
    cli = HLSConverterCLI()
    sys.exit(cli.run())