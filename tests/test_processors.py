import subprocess
from pathlib import Path
from hls_converter.media_analyzer import SubtitleTrack
import pytest

from hls_converter.processors import SubtitleProcessor
from hls_converter.config import HLSConfig


def test_sanitize_language_and_skip_bitmap(monkeypatch, tmp_path):
    cfg = HLSConfig()
    cfg.skip_bitmap_subtitles = True
    sp = SubtitleProcessor(cfg)

    # Create fake subtitle tracks: one bitmap codec, one text codec
    bitmap = SubtitleTrack(index=0, language='eng', codec='hdmv_pgs_subtitle')
    text = SubtitleTrack(index=1, language='esp', codec='mov_text')

    # Mock subprocess.run so conversion of text works, bitmap skipped
    def fake_run(cmd, check, capture_output, text, timeout):
        # ffmpeg output file is last arg
        out_file = Path(cmd[-1])
        try:
            out_file.write_text("WEBVTT\n")
        except Exception:
            pass
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, 'run', fake_run)

    inp = tmp_path / "in.mp4"
    inp.write_text("x")
    out = tmp_path / "out"
    out.mkdir()

    sp.convert_subtitles(inp, out, [bitmap, text])

    # Check that text track created
    files = list(out.iterdir())
    assert any(f.suffix == '.vtt' for f in files)
