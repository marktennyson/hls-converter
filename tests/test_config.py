import pytest
from hls_converter.config import HLSConfig, BitrateProfile


def test_bitrate_profile_properties():
    p = BitrateProfile("720p", (1280, 720), 2500, 1800)
    assert p.scale_filter == "1280:720"
    assert p.resolution_name == "720p"


def test_hlsconfig_to_from_dict_roundtrip():
    cfg = HLSConfig()
    cfg.segment_duration = 4
    cfg.preset = "slow"
    cfg.crf = 18
    d = cfg.to_dict()

    new = HLSConfig.from_dict(d)
    assert new.segment_duration == 4
    assert new.preset == "slow"
    assert new.crf == 18


def test_create_adaptive_profiles_basic():
    # Small resolution should include 360p and below
    profiles = HLSConfig.create_adaptive_profiles(640, 360, input_bitrate=1000)
    assert any(p.resolution_name == "360p" for p in profiles)


def test_get_encoder_specific_args():
    cfg = HLSConfig()
    cfg.preset = "fast"
    cfg.crf = 20
    assert "-preset" in cfg.get_encoder_specific_args("libx264")
    assert cfg.get_encoder_specific_args("h264_nvenc")