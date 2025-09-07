import subprocess
from pathlib import Path
import types

from hls_converter.cli import HLSConverterCLI
from hls_converter.processors import VideoProcessor, SubtitleProcessor
from hls_converter.config import HLSConfig
from hls_converter.media_analyzer import MediaAnalyzer
from hls_converter.encoder_detector import EncoderDetector
from hls_converter.converter import HLSConverter
import hls_converter.processors as proc_module


def test_cli_list_encoders_mixed(monkeypatch):
    fake = {
        'video_encoder': 'h264_nvenc',
        'audio_encoder': 'aac_at',
        'video_name': 'NVENC',
        'audio_name': 'AudioToolbox',
        'all_encoders': {
            'video': {'hardware': [('h264_nvenc', 'NVENC')], 'software': [('libx264', 'x264')]},
            'audio': {'hardware': [('aac_at', 'AudioToolbox')], 'software': [('aac', 'aac')]}
        }
    }

    monkeypatch.setattr(EncoderDetector, 'detect_encoders', lambda self, force_refresh=False: fake)
    rc = HLSConverterCLI().run(['--list-encoders'])
    assert rc == 0


def test_video_processor_logging_with_fake_time(monkeypatch, tmp_path):
    cfg = HLSConfig()
    det = EncoderDetector()
    det._cache = {'video_encoder':'libx264','video_name':'x264','audio_encoder':'aac','audio_name':'aac','all_encoders':{}}
    vp = VideoProcessor(det, cfg)

    # Fake Popen that yields progress lines
    class FakePopen:
        def __init__(self):
            self.stderr = self
            self._lines = iter(['out_time=00:00:01\n', 'speed=2.0x\n', 'frame=5\n', ''])
        def readline(self):
            return next(self._lines)
        def poll(self):
            return None
        def wait(self):
            return 0
        def read(self):
            return ''

    monkeypatch.setattr(subprocess, 'Popen', lambda *a, **k: FakePopen())

    # Patch time.time used in processors to force logging branch (last_log_time diff >=5)
    times = [0, 10, 10, 10, 10]
    def fake_time():
        return times.pop(0) if times else 100
    monkeypatch.setattr(proc_module.time, 'time', fake_time)

    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    out = tmp_path / 'out'
    out.mkdir()

    profile = types.SimpleNamespace(name='t', resolution=(640,360), max_bitrate_kbps=800, min_bitrate_kbps=600, scale_filter='640:360', resolution_name='360p')
    res = vp._run_ffmpeg_process(['ffmpeg'], 't', 'video', 10.0)
    assert res['status'] in ('success', 'error')


def test_subtitle_include_bitmap(monkeypatch, tmp_path):
    cfg = HLSConfig()
    cfg.skip_bitmap_subtitles = False
    sp = SubtitleProcessor(cfg)

    class T:
        def __init__(self, idx, lang, codec):
            self.index = idx
            self.language = lang
            self.codec = codec
        @property
        def map_index(self):
            return self.index
        def is_bitmap(self):
            return True

    from hls_converter.media_analyzer import SubtitleTrack
    t = SubtitleTrack(index=0, language='eng', codec='hdmv_pgs_subtitle')

    def fake_run(cmd, check, capture_output, text, timeout):
        out = Path(cmd[-1])
        out.write_text('WEBVTT\n')
        return subprocess.CompletedProcess(cmd, 0, stdout='', stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)

    inp = tmp_path / 'in.mp4'
    inp.write_text('x')
    out = tmp_path / 'out'
    out.mkdir()
    sp.convert_subtitles(inp, out, [t])
    assert any(p.suffix == '.vtt' for p in out.iterdir())


def test_media_analyzer_parsers_direct():
    ma = MediaAnalyzer()
    s = {'width':1280,'height':720,'duration':'12.0','avg_frame_rate':'30/1','bit_rate':'1200000','codec_name':'h264'}
    v = ma._parse_video_stream(s)
    assert v.width == 1280 and v.height == 720
    a = ma._parse_audio_stream({'codec_name':'aac','bit_rate':'160000','sample_rate':'48000','channels':2,'tags':{'language':'en'}}, 0)
    assert a.language.startswith('en')
    sub = ma._parse_subtitle_stream({'codec_name':'mov_text','tags':{'language':'eng'}}, 0)
    assert sub.language.startswith('eng')


def test_config_encoder_args_variants():
    cfg = HLSConfig()
    assert '-allow_sw' in cfg.get_encoder_specific_args('h264_videotoolbox')
    assert '-rc' in cfg.get_encoder_specific_args('h264_nvenc')
    assert '-crf' in cfg.get_encoder_specific_args('libx264')
    assert '-preset' in cfg.get_encoder_specific_args('h264_qsv')


def test_encoder_detector_is_hardware():
    det = EncoderDetector()
    assert det.is_hardware_encoder('h264_nvenc')
    assert not det.is_hardware_encoder('libx264')


def test_converter_ui_methods(tmp_path):
    cfg = HLSConfig()
    conv = HLSConverter(cfg)
    # Call banner and processing config display
    conv._show_banner()
    from hls_converter.media_analyzer import MediaInfo, VideoInfo
    fake_media = MediaInfo(video=VideoInfo(width=1280, height=720, duration=10.0, fps=25.0), audio_tracks=[], subtitle_tracks=[])
    conv._show_processing_config(fake_media, {'video_name':'x264','audio_name':'aac'}, ['360p'])
