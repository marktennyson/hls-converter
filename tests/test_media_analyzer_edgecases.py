from hls_converter.media_analyzer import MediaAnalyzer
from pathlib import Path


def test_parse_video_stream_various_fps(monkeypatch, tmp_path):
    ma = MediaAnalyzer()
    streams = [{"codec_type":"video","width":640,"height":360,"duration":"5.0","avg_frame_rate":"30000/1001","bit_rate":"500000","codec_name":"h264"}]
    monkeypatch.setattr(ma, '_get_streams', lambda p: streams)
    monkeypatch.setattr(ma, '_get_format_info', lambda p: {})
    f = tmp_path / 'x.mp4'
    f.write_text('x')
    info = ma.analyze(f)
    assert info.video is not None
    assert info.video.fps > 29


def test_parse_audio_missing_bitrate(monkeypatch, tmp_path):
    ma = MediaAnalyzer()
    streams = [{"codec_type":"audio","codec_name":"aac","sample_rate":"48000","channels":2, "tags":{"language":"en"}}]
    monkeypatch.setattr(ma, '_get_streams', lambda p: streams)
    monkeypatch.setattr(ma, '_get_format_info', lambda p: {})
    f = tmp_path / 'x.mp4'
    f.write_text('x')
    info = ma.analyze(f)
    assert len(info.audio_tracks) == 1