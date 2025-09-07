import subprocess
from hls_converter.encoder_detector import EncoderDetector


class DummyResult:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_select_best_encoders_with_no_system(monkeypatch):
    # Force _test_encoder to return False for all
    det = EncoderDetector()
    monkeypatch.setattr(det, "_test_encoder", lambda codec, mtype: False)
    result = det.detect_encoders(force_refresh=True)
    assert result['video_encoder'] in ("libx264",)
    assert 'audio_encoder' in result


def test_get_best_encoder_cache(monkeypatch):
    det = EncoderDetector()
    # Provide a fake cache
    det._cache = {
        'video_encoder': 'libx264',
        'audio_encoder': 'aac',
        'video_name': 'x264',
        'audio_name': 'aac',
        'all_encoders': {'video': {'hardware': [], 'software': [('libx264','x264')]}, 'audio': {'hardware': [], 'software': [('aac','aac')]}}
    }
    v_enc, v_name = det.get_best_video_encoder()
    a_enc, a_name = det.get_best_audio_encoder()
    assert v_enc == 'libx264'
    assert a_enc == 'aac'
