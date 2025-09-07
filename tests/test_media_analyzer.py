import json
from pathlib import Path
import subprocess
from hls_converter.media_analyzer import MediaAnalyzer, VideoInfo, AudioTrack, SubtitleTrack


class FakeCompleted:
    def __init__(self, stdout):
        self.stdout = stdout


def test_parse_video_stream(monkeypatch, tmp_path):
    ma = MediaAnalyzer()

    # Create fake ffprobe streams JSON
    streams = {
        "streams": [
            {"codec_type": "video", "width": 1280, "height": 720, "duration": "10.0", "avg_frame_rate": "25/1", "bit_rate": "2000000", "codec_name": "h264"},
            {"codec_type": "audio", "codec_name": "aac", "bit_rate": "160000", "sample_rate": "48000", "channels": 2, "tags": {"language": "en"}},
            {"codec_type": "subtitle", "codec_name": "mov_text", "tags": {"language": "eng"}}
        ]
    }

    # Mock _get_streams and _get_format_info
    monkeypatch.setattr(ma, "_get_streams", lambda p: streams['streams'])
    monkeypatch.setattr(ma, "_get_format_info", lambda p: {"format_name": "mp4"})

    f = tmp_path / "video.mp4"
    f.write_text("dummy")

    info = ma.analyze(f)
    # video may be Optional[VideoInfo]
    assert info.video is not None
    assert info.video.width == 1280
    assert info.video.height == 720
    assert len(info.audio_tracks) == 1
    assert len(info.subtitle_tracks) == 1
