import argparse
from pathlib import Path
from types import SimpleNamespace

from hls_converter.converter import HLSConverter
from hls_converter.cli import HLSConverterCLI
from hls_converter.config import HLSConfig, BitrateProfile


def test_cli_parser_basic():
    cli = HLSConverterCLI()
    parser = cli._create_parser()
    args = parser.parse_args(['input.mp4', '--crf', '20'])
    assert args.crf == 20


def test_converter_orchestration(monkeypatch, tmp_path):
    cfg = HLSConfig()
    conv = HLSConverter(cfg)

    # Create a dummy input file
    inp = tmp_path / "in.mp4"
    inp.write_text("x")

    out = tmp_path / "out"

    # Mock analyzer
    fake_video = SimpleNamespace(width=1280, height=720, duration=10.0, bitrate=2000)
    fake_media = SimpleNamespace(video=fake_video, audio_tracks=[], subtitle_tracks=[], file_size=1024)
    monkeypatch.setattr(conv.media_analyzer, 'analyze', lambda p: fake_media)
    monkeypatch.setattr(conv.media_analyzer, 'get_optimal_resolutions', lambda v: ['360p', '720p'])

    # Mock encoder detector by setting cache directly so get_best_video_encoder works
    conv.encoder_detector._cache = {
        'video_encoder': 'libx264',
        'audio_encoder': 'aac',
        'video_name': 'x264',
        'audio_name': 'aac',
        'all_encoders': {}
    }

    # Mock processors to no-op
    monkeypatch.setattr(conv.video_processor, '_run_ffmpeg_process', lambda *a, **k: {"status":"success","name":"v","duration":0.1})
    monkeypatch.setattr(conv.audio_processor, 'process_audio_rendition', lambda *a, **k: {"status":"success","name":"a","duration":0.1})
    monkeypatch.setattr(conv.subtitle_processor, 'convert_subtitles', lambda *a, **k: None)

    results = conv.convert(inp, out, resolutions=['360p'])
    assert results['success'] is True
    assert 'master_playlist' in results
