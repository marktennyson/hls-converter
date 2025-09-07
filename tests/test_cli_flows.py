import sys
from pathlib import Path
import json

from hls_converter.cli import HLSConverterCLI
from hls_converter.encoder_detector import EncoderDetector
from hls_converter.converter import HLSConverter


def test_cli_list_encoders(monkeypatch, capsys):
    cli = HLSConverterCLI()

    # Patch EncoderDetector.detect_encoders to return deterministic data
    fake = {'video_encoder':'libx264','audio_encoder':'aac','video_name':'x264','audio_name':'aac','all_encoders':{'video':{'hardware':[], 'software':[('libx264','x264')]}, 'audio':{'hardware':[], 'software':[('aac','aac')]}}}
    monkeypatch.setattr(EncoderDetector, 'detect_encoders', lambda self, force_refresh=False: fake)

    # Run the CLI with --list-encoders
    rc = HLSConverterCLI().run(['--list-encoders'])
    assert rc == 0


def test_cli_missing_input(capsys):
    cli = HLSConverterCLI()
    rc = cli.run([])
    assert rc == 1


def test_cli_input_not_exists(tmp_path):
    cli = HLSConverterCLI()
    p = tmp_path / 'nofile.mp4'
    rc = cli.run([str(p)])
    assert rc == 1


def test_cli_save_and_analyze(monkeypatch, tmp_path):
    # Create input file
    inp = tmp_path / 'in.mp4'
    inp.write_text('x')

    outcfg = tmp_path / 'outcfg.json'

    # Patch HLSConverter.convert to not actually run
    def fake_convert(self, input_file, output_dir, resolutions):
        return {'success': True, 'master_playlist': str(output_dir / 'master.m3u8')}

    monkeypatch.setattr(HLSConverter, 'convert', fake_convert)

    rc = HLSConverterCLI().run([str(inp), '--save-config', str(outcfg)])
    assert rc == 0