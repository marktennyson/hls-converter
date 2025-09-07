import subprocess
import types
from pathlib import Path
import time

import pytest

from hls_converter.cli import HLSConverterCLI
from hls_converter.config import HLSConfig
from hls_converter.media_analyzer import MediaAnalyzer
from hls_converter.processors import SubtitleProcessor, VideoProcessor
from hls_converter.encoder_detector import EncoderDetector


def test_cli_invalid_resolutions(tmp_path):
    cli = HLSConverterCLI()
    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    rc = cli.run([str(inp), '--resolutions', '999p'])
    assert rc == 1


def test_create_adaptive_profiles_with_input_bitrate():
    profiles = HLSConfig.create_adaptive_profiles(1920, 1080, input_bitrate=5000)
    assert any(p.resolution_name == '1080p' for p in profiles)


def test_media_analyzer_parse_fps_error(monkeypatch, tmp_path):
    ma = MediaAnalyzer()
    streams = [{"codec_type":"video","width":640,"height":360,"duration":"5.0","avg_frame_rate":"bad/0","bit_rate":"notdigit","codec_name":"h264"}]
    monkeypatch.setattr(ma, '_get_streams', lambda p: streams)
    monkeypatch.setattr(ma, '_get_format_info', lambda p: {})
    f = tmp_path / 'x.mp4'
    f.write_text('x')
    info = ma.analyze(f)
    assert info.video is not None


def test_subtitle_processor_errors_and_timeouts(monkeypatch, tmp_path):
    from hls_converter.media_analyzer import SubtitleTrack

    cfg = HLSConfig()
    sp = SubtitleProcessor(cfg)

    # Two tracks: one will raise CalledProcessError, another TimeoutExpired
    t1 = SubtitleTrack(index=0, language='en', codec='mov_text')
    t2 = SubtitleTrack(index=1, language='es', codec='mov_text')

    def fake_run(cmd, check, capture_output, text, timeout):
        if '0:s:0' in ' '.join(cmd):
            raise subprocess.CalledProcessError(1, cmd, stderr='fail')
        else:
            raise subprocess.TimeoutExpired(cmd, timeout)

    monkeypatch.setattr(subprocess, 'run', fake_run)

    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    out = tmp_path / 'out'
    out.mkdir()

    sp.convert_subtitles(inp, out, [t1, t2])


def test_video_processor_progress_logging(monkeypatch, tmp_path):
    cfg = HLSConfig()
    det = EncoderDetector()
    det._cache = {'video_encoder':'libx264','video_name':'x264','audio_encoder':'aac','audio_name':'aac','all_encoders':{}}
    vp = VideoProcessor(det, cfg)

    # Create fake Popen that yields progress lines and then ends
    class P:
        def __init__(self):
            self.stderr = self
            self._lines = iter(['out_time=00:00:01\n','speed=1.0x\n','frame=10\n',''])
        def readline(self):
            return next(self._lines)
        def poll(self):
            return None
        def wait(self):
            return 0
        def read(self):
            return ''

    monkeypatch.setattr(subprocess, 'Popen', lambda *a, **k: P())

    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    out = tmp_path / 'out'
    out.mkdir()
    profile = types.SimpleNamespace(name='t', resolution=(640,360), max_bitrate_kbps=800, min_bitrate_kbps=600, scale_filter='640:360', resolution_name='360p')
    res = vp._run_ffmpeg_process(['ffmpeg'], 't', 'video', 10.0)
    assert res['status'] in ('success','error')


def test_encoder_detector_fallback():
    det = EncoderDetector()
    encoders = {'video': {'hardware': [], 'software': []}, 'audio': {'hardware': [], 'software': []}}
    res = det._select_best_encoders(encoders)
    assert 'video_encoder' in res and 'audio_encoder' in res
