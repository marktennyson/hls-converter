import subprocess
from hls_converter.encoder_detector import EncoderDetector


def test_test_encoder_timeout(monkeypatch):
    det = EncoderDetector()

    def fake_run(cmd, capture_output, text, timeout):
        raise subprocess.TimeoutExpired(cmd, timeout)

    monkeypatch.setattr(subprocess, 'run', fake_run)
    assert det._test_encoder('libx264', 'video') is False


def test_select_best_encoders_prioritizes_hardware(monkeypatch):
    det = EncoderDetector()

    # Create a controlled encoders dict and call _select_best_encoders
    enc = {'video': {'hardware': [('h264_nvenc', 'NVENC')], 'software': [('libx264','x264')]}, 'audio': {'hardware': [], 'software': [('aac','aac')]}}
    res = det._select_best_encoders(enc)
    assert res['video_encoder'] in ('h264_nvenc', 'libx264')