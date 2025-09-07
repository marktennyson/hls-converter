import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from hls_converter.cli import HLSConverterCLI
from hls_converter.converter import HLSConverter
from hls_converter.processors import AudioProcessor, VideoProcessor, SubtitleProcessor
from hls_converter.encoder_detector import EncoderDetector
from hls_converter.media_analyzer import SubtitleTrack, AudioTrack, VideoInfo
from hls_converter.config import HLSConfig


def test_cli_analyze_only(monkeypatch, tmp_path):
    inp = tmp_path / 'in.mp4'
    inp.write_text('x')

    cli = HLSConverterCLI()
    # Patch HLSConverter.__init__ to inject a fake media_analyzer on instances
    def fake_init(self, config=None):
        fake_media = SimpleNamespace(video=SimpleNamespace(width=640, height=360, duration=1.0, bitrate=800), audio_tracks=[], subtitle_tracks=[], file_size=0)
        self.media_analyzer = SimpleNamespace(analyze=lambda p: fake_media, get_optimal_resolutions=lambda v: ['360p'])

    monkeypatch.setattr(HLSConverter, '__init__', fake_init)
    rc = cli.run([str(inp), '--analyze-only'])
    assert rc == 0


def test_cli_conversion_failure(monkeypatch, tmp_path):
    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    cli = HLSConverterCLI()
    # Patch HLSConverter.convert to return failure
    monkeypatch.setattr(HLSConverter, 'convert', lambda self, a, b, c: {'success': False})
    rc = cli.run([str(inp)])
    assert rc == 1


def test_load_config_error(tmp_path):
    cfg_file = tmp_path / 'bad.json'
    cfg_file.write_text('{ invalid json')
    cli = HLSConverterCLI()
    parser = cli._create_parser()
    args = parser.parse_args(['input.mp4', '--config', str(cfg_file)])
    cfg = cli._load_configuration(args)
    assert isinstance(cfg, HLSConfig)


def test_audio_processor_with_bitrate(monkeypatch, tmp_path):
    cfg = HLSConfig()
    det = EncoderDetector()
    det._cache = {'audio_encoder':'aac','audio_name':'aac','video_encoder':'libx264','video_name':'x264','all_encoders':{}}
    ap = AudioProcessor(det, cfg)

    # Create a fake audio track with bitrate
    track = AudioTrack(index=0, language='en', codec='aac', bitrate=256, sample_rate=48000, channels=2)
    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    out = tmp_path / 'out'
    out.mkdir()

    # Monkeypatch subprocess.Popen via VideoProcessor._run_ffmpeg_process to return success
    monkeypatch.setattr(subprocess, 'Popen', lambda *a, **k: SimpleNamespace(stderr=SimpleNamespace(read=lambda: ''), wait=lambda: 0, poll=lambda: 0))
    res = ap.process_audio_rendition(track, inp, out, 1.0)
    assert res['status'] in ('success','error')


def test_subtitle_skip_bitmap(monkeypatch, tmp_path):
    cfg = HLSConfig()
    cfg.skip_bitmap_subtitles = True
    sp = SubtitleProcessor(cfg)
    t = SubtitleTrack(index=0, language='und', codec='hdmv_pgs_subtitle')
    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    out = tmp_path / 'out'
    out.mkdir()

    # Monkeypatch subprocess.run to ensure not called
    called = {'run': False}
    def fake_run(*a, **k):
        called['run'] = True
        return subprocess.CompletedProcess(a[0], 0, stdout='', stderr='')
    monkeypatch.setattr(subprocess, 'run', fake_run)
    sp.convert_subtitles(inp, out, [t])
    assert called['run'] is False


def test_video_processor_exception_on_popen(monkeypatch, tmp_path):
    cfg = HLSConfig()
    det = EncoderDetector()
    det._cache = {'video_encoder':'libx264','video_name':'x264','audio_encoder':'aac','audio_name':'aac','all_encoders':{}}
    vp = VideoProcessor(det, cfg)

    def raise_popen(*a, **k):
        raise RuntimeError('popen fail')

    monkeypatch.setattr(subprocess, 'Popen', raise_popen)
    res = vp._run_ffmpeg_process(['ffmpeg'], 'n', 'video', 1.0)
    assert res['status'] == 'error'


def test_encoder_detector_availability_mix(monkeypatch):
    det = EncoderDetector()
    # Setup _test_encoder to return True for hardware but False for others
    def fake_test(codec, mtype):
        return codec in ('h264_nvenc', 'aac_at')
    monkeypatch.setattr(det, '_test_encoder', fake_test)
    res = det.detect_encoders(force_refresh=True)
    assert 'video_encoder' in res and 'audio_encoder' in res
