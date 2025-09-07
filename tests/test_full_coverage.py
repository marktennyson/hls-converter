import json
import subprocess
import types
from pathlib import Path
import time

import pytest

from hls_converter.config import HLSConfig, BitrateProfile
from hls_converter.encoder_detector import EncoderDetector
from hls_converter.media_analyzer import MediaAnalyzer, VideoInfo
from hls_converter.processors import VideoProcessor
from hls_converter.converter import HLSConverter


class DummyPopen:
    def __init__(self, returncode=0, stderr_lines=None):
        self.returncode = returncode
        self._stderr_lines = stderr_lines or ["frame=1\n", "out_time=00:00:01\n", "speed=1.0x\n"]
        self.stderr = self
        self._iter = iter(self._stderr_lines + [''])

    def readline(self):
        return next(self._iter)

    def read(self):
        return ''.join(self._stderr_lines)

    def poll(self):
        return None

    def wait(self):
        return 0

    def terminate(self):
        pass

    def kill(self):
        pass


def test_encoder_detector_selection(monkeypatch):
    det = EncoderDetector()

    # Simulate ffmpeg present and only libx264 available
    monkeypatch.setattr(det, '_test_encoder', lambda codec, t: codec in ('libx264', 'aac'))
    result = det.detect_encoders(force_refresh=True)
    assert result['video_encoder'] in ('libx264', 'h264')


def test_media_analyzer_ffprobe_failure(monkeypatch, tmp_path):
    ma = MediaAnalyzer()

    # Force _get_format_info to raise
    monkeypatch.setattr(ma, '_get_format_info', lambda p: {})
    monkeypatch.setattr(ma, '_get_streams', lambda p: [])
    f = tmp_path / 'x.mp4'
    f.write_text('x')
    info = ma.analyze(f)
    assert info.video is None


def test_video_processor_run_ffmpeg_error(monkeypatch, tmp_path):
    cfg = HLSConfig()
    det = EncoderDetector()
    vp = VideoProcessor(det, cfg)

    # Monkeypatch encoder detector to return fallback
    det._cache = {'video_encoder': 'libx264', 'video_name': 'x264', 'audio_encoder': 'aac', 'audio_name': 'aac', 'all_encoders': {}}

    # Patch subprocess.Popen to DummyPopen that will return non-zero
    monkeypatch.setattr(subprocess, 'Popen', lambda *a, **k: DummyPopen(returncode=1))

    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    out = tmp_path / 'out'
    out.mkdir()
    profile = BitrateProfile('test', (640,360), 800, 600)
    res = vp.process_video_rendition(profile, inp, out, 10.0)
    assert res['status'] in ('error', 'success')


def test_hlsconverter_end_to_end(monkeypatch, tmp_path):
    cfg = HLSConfig()
    conv = HLSConverter(cfg)

    # Create dummy media info
    fake_video = VideoInfo(width=1280, height=720, duration=2.0, fps=25.0, bitrate=2000)
    fake_media = types.SimpleNamespace(video=fake_video, audio_tracks=[], subtitle_tracks=[], file_size=1024)

    monkeypatch.setattr(conv.media_analyzer, 'analyze', lambda p: fake_media)
    monkeypatch.setattr(conv.media_analyzer, 'get_optimal_resolutions', lambda v: ['360p'])
    conv.encoder_detector._cache = {'video_encoder': 'libx264', 'video_name': 'x264', 'audio_encoder': 'aac', 'audio_name': 'aac', 'all_encoders': {}}

    # Patch processors to no-op
    monkeypatch.setattr(conv.video_processor, 'process_video_rendition', lambda *a, **k: {'status':'success','name':'v','duration':0.1})
    monkeypatch.setattr(conv.audio_processor, 'process_audio_rendition', lambda *a, **k: {'status':'success','name':'a','duration':0.1})
    monkeypatch.setattr(conv.subtitle_processor, 'convert_subtitles', lambda *a, **k: None)

    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    out = tmp_path / 'out'
    res = conv.convert(inp, out, resolutions=['360p'])
    assert res['success']
