import subprocess
import json
import time
from types import SimpleNamespace
from pathlib import Path

import pytest

from hls_converter.cli import HLSConverterCLI
from hls_converter.converter import HLSConverter
from hls_converter.encoder_detector import EncoderDetector
from hls_converter.media_analyzer import MediaAnalyzer
from hls_converter.processors import VideoProcessor, SubtitleProcessor
from hls_converter.config import HLSConfig


class FakeCompleted:
    def __init__(self, stdout=''):
        self.stdout = stdout


class FakePopen:
    def __init__(self, lines=None, returncode=0):
        self.stderr = self
        self._lines = iter(lines or ['frame=1\n', 'out_time=00:00:01\n', 'speed=1.0x\n', ''])
        self._returncode = returncode

    def readline(self):
        return next(self._lines)

    def read(self):
        return ''

    def poll(self):
        return None

    def wait(self):
        return self._returncode

    def terminate(self):
        pass

    def kill(self):
        pass


def test_force_full_coverage(monkeypatch, tmp_path):
    # Monkeypatch subprocess.run to handle ffprobe and ffmpeg commands
    def fake_run(cmd, capture_output=False, text=False, timeout=None, check=False):
        # Simulate ffprobe JSON output when called with -show_streams or -show_format
        if '-show_streams' in cmd or '-show_format' in cmd:
            data = {}
            if '-show_streams' in cmd:
                data = {'streams': [
                    {'codec_type':'video','width':1920,'height':1080,'duration':'10.0','avg_frame_rate':'25/1','bit_rate':'4000000','codec_name':'h264'},
                    {'codec_type':'audio','codec_name':'aac','bit_rate':'160000','sample_rate':'48000','channels':2,'tags':{'language':'en'}},
                    {'codec_type':'subtitle','codec_name':'mov_text','tags':{'language':'eng'}}
                ]}
            else:
                data = {'format': {'format_name': 'mp4'}}
            return FakeCompleted(stdout=json.dumps(data))

        # For conversion commands, just return success
        return FakeCompleted(stdout='')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    # Monkeypatch Popen to FakePopen
    monkeypatch.setattr(subprocess, 'Popen', lambda *a, **k: FakePopen())

    # Create a temporary input file
    inp = tmp_path / 'in.mp4'
    inp.write_text('x')

    # Create HLSConverter and run convert to exercise many branches
    cfg = HLSConfig()
    cfg.convert_subtitles = True
    conv = HLSConverter(cfg)

    # Ensure encoder detector picks values from our fake_run
    conv.encoder_detector._cache = {'video_encoder':'libx264','video_name':'x264','audio_encoder':'aac','audio_name':'aac','all_encoders':{'video':{'hardware':[], 'software':[('libx264','x264')]}, 'audio':{'hardware':[], 'software':[('aac','aac')]}}}

    out = tmp_path / 'out'
    out.mkdir()

    # Run conversion which will call processors; our fake Popen will simulate progress
    results = conv.convert(inp, out, resolutions=None)
    assert results['success'] is True

    # Also exercise CLI analyze-only path and list-encoders
    cli = HLSConverterCLI()
    # monkeypatch EncoderDetector.detect_encoders to return ours
    monkeypatch.setattr(EncoderDetector, 'detect_encoders', lambda self, force_refresh=False: conv.encoder_detector._cache)
    rc = cli.run(['--list-encoders'])
    assert rc == 0
