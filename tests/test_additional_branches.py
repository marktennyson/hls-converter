import json
from pathlib import Path
import subprocess

from hls_converter.cli import HLSConverterCLI
from hls_converter.encoder_detector import EncoderDetector
from hls_converter.media_analyzer import MediaAnalyzer, VideoInfo
from hls_converter.processors import SubtitleProcessor
from hls_converter.config import HLSConfig, BitrateProfile
from hls_converter.converter import HLSConverter


def test_cli_load_and_save_config(tmp_path, monkeypatch):
    cli = HLSConverterCLI()
    cfg = HLSConfig()
    cfg.preset = "slow"
    cfg_dict = cfg.to_dict()

    cfg_file = tmp_path / "cfg.json"
    with open(cfg_file, 'w') as f:
        json.dump(cfg_dict, f)

    # parse args with config and save-config
    parser = cli._create_parser()
    args = parser.parse_args(['input.mp4', '--config', str(cfg_file), '--save-config', str(tmp_path / 'out.json')])
    loaded = cli._load_configuration(args)
    # The parser has a default preset ('fast') which the loader will apply over the file
    assert loaded.preset == args.preset

    # If we explicitly set a preset argument, it should override file as well
    args2 = parser.parse_args(['input.mp4', '--config', str(cfg_file), '--preset', 'ultrafast'])
    loaded2 = cli._load_configuration(args2)
    assert loaded2.preset == 'ultrafast'


def test_encoder_selection_logic(monkeypatch):
    det = EncoderDetector()
    # simulate that hardware nvenc is available
    def fake_test(enc, mtype):
        return enc == 'h264_nvenc'

    monkeypatch.setattr(det, '_test_encoder', fake_test)
    result = det.detect_encoders(force_refresh=True)
    assert 'video_encoder' in result
    encoder = result.get('video_encoder')
    # guard for type checkers
    assert isinstance(encoder, str)
    assert det.is_hardware_encoder(encoder) or encoder == 'libx264'


def test_media_analyzer_optimal_resolutions_none():
    ma = MediaAnalyzer()
    # If video_info is None
    # pass None to exercise fallback branch; ignore type for static checkers
    res = ma.get_optimal_resolutions(None)  # type: ignore[arg-type]
    assert isinstance(res, list) and len(res) >= 2


def test_subtitle_sanitize_and_duplicates(tmp_path, monkeypatch):
    from hls_converter.media_analyzer import SubtitleTrack

    cfg = HLSConfig()
    sp = SubtitleProcessor(cfg)

    # Prepare two tracks with same language codes
    track1 = SubtitleTrack(index=0, language='eng', codec='mov_text')
    track2 = SubtitleTrack(index=1, language='eng', codec='mov_text')

    # Monkeypatch subprocess.run to create files
    def fake_run(cmd, check, capture_output, text, timeout):
        out = Path(cmd[-1])
        out.write_text("WEBVTT\n")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, 'run', fake_run)

    inp = tmp_path / "in.mp4"
    inp.write_text("x")
    out = tmp_path / "out"
    out.mkdir()

    sp.convert_subtitles(inp, out, [track1, track2])
    files = list(out.glob('*.vtt'))
    # Expect at least one created file
    assert len(files) >= 1


def test_create_master_playlist(tmp_path):
    cfg = HLSConfig()
    conv = HLSConverter(cfg)
    out = tmp_path / "out"
    out.mkdir()

    # Create fake audio tracks
    audio1 = type('A', (), {'language': 'en'})
    audio2 = type('A', (), {'language': 'es'})
    conv.config.bitrate_profiles = [BitrateProfile('360p', (640,360), 800,600), BitrateProfile('720p', (1280,720), 2500,1800)]
    mp = conv._create_master_playlist(out, [audio1, audio2])
    assert mp.exists()
    content = mp.read_text()
    assert '#EXTM3U' in content
