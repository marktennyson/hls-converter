# Installation

This guide covers all the ways to install HLS Converter on your system.

## System Requirements

### Required Software

- **Python 3.8 or higher**
- **FFmpeg 4.0+** with desired encoders
- **FFprobe** (usually included with FFmpeg)

### Recommended System Specs

- **RAM**: 4GB minimum, 8GB+ recommended for 4K videos
- **CPU**: Multi-core processor (4+ cores recommended)
- **Storage**: SSD recommended for better I/O performance
- **GPU**: Optional, for hardware acceleration support

## Installing Python Dependencies

### Option 1: Install from PyPI (Recommended)

```bash
pip install hls-converter
```

!!! note "Virtual Environment Recommended"
    It's recommended to install in a virtual environment to avoid conflicts:
    ```bash
    python -m venv hls-env
    source hls-env/bin/activate  # On Windows: hls-env\Scripts\activate
    pip install hls-converter
    ```

### Option 2: Install from Source

For the latest development version:

```bash
git clone https://github.com/marktennyson/hls-converter.git
cd hls-converter
pip install -e .
```

### Option 3: Development Installation

For contributors and developers:

```bash
git clone https://github.com/marktennyson/hls-converter.git
cd hls-converter
pip install -e ".[dev]"
```

This installs additional tools for development:

- `pytest` - Testing framework
- `black` - Code formatting
- `isort` - Import sorting  
- `flake8` - Code linting
- `mypy` - Type checking
- `pre-commit` - Git hooks

## Installing FFmpeg

FFmpeg is required for video processing. Choose your platform:

=== "macOS"

    **Using Homebrew (Recommended):**
    ```bash
    brew install ffmpeg
    ```

    **Using MacPorts:**
    ```bash
    sudo port install ffmpeg +universal
    ```

    **Verify Installation:**
    ```bash
    ffmpeg -version
    ffprobe -version
    ```

=== "Windows"

    **Option 1: Download Pre-built Binaries**
    
    1. Download from [FFmpeg.org](https://ffmpeg.org/download.html#build-windows)
    2. Extract to `C:\ffmpeg`
    3. Add `C:\ffmpeg\bin` to your PATH environment variable
    4. Restart your command prompt

    **Option 2: Using Package Manager**
    
    With [Chocolatey](https://chocolatey.org/):
    ```bash
    choco install ffmpeg
    ```

    With [Scoop](https://scoop.sh/):
    ```bash
    scoop install ffmpeg
    ```

    **Verify Installation:**
    ```bash
    ffmpeg -version
    ffprobe -version
    ```

=== "Linux"

    **Ubuntu/Debian:**
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```

    **CentOS/RHEL/Fedora:**
    ```bash
    # Enable RPM Fusion repository first
    sudo dnf install ffmpeg ffmpeg-devel
    ```

    **Arch Linux:**
    ```bash
    sudo pacman -S ffmpeg
    ```

    **From Source (for latest features):**
    ```bash
    git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
    cd ffmpeg
    ./configure --enable-gpl --enable-libx264 --enable-libx265
    make -j$(nproc)
    sudo make install
    ```

    **Verify Installation:**
    ```bash
    ffmpeg -version
    ffprobe -version
    ```

## Hardware Acceleration Setup

HLS Converter automatically detects available hardware encoders. Here's how to enable them:

### VideoToolbox (macOS)

VideoToolbox is built into macOS and should work automatically:

```bash
# Check if VideoToolbox is available
ffmpeg -hide_banner -encoders | grep videotoolbox
```

### NVIDIA NVENC

**Requirements:**
- NVIDIA GPU with NVENC support (GTX 600 series or newer)
- Latest NVIDIA drivers

**Installation:**
```bash
# Most FFmpeg builds include NVENC support
ffmpeg -hide_banner -encoders | grep nvenc
```

### Intel QuickSync (QSV)

**Requirements:**
- Intel CPU with integrated graphics
- Intel Media SDK or oneVPL

**Linux Setup:**
```bash
# Install Intel Media SDK
sudo apt install intel-media-va-driver-non-free
```

### AMD AMF (Windows only)

**Requirements:**
- AMD GPU with VCE support
- AMD drivers

**Check Availability:**
```bash
ffmpeg -hide_banner -encoders | grep amf
```

## Verification

After installation, verify everything works:

### 1. Test Python Package

```bash
python -c "import hls_converter; print('✅ HLS Converter imported successfully')"
```

### 2. Test CLI

```bash
hls-converter --version
hls-converter --help
```

### 3. Test Encoder Detection

```bash
hls-converter --list-encoders
```

Expected output should show available encoders:
```
Available Encoders
┏━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Type  ┃ Category ┃ Codec             ┃ Name                     ┃ Selected ┃
┡━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Video │ Hardware │ h264_videotoolbox │ VideoToolbox (macOS)     │ ✅       │
│ Video │ Software │ libx264           │ x264 Software            │          │
│ Audio │ Hardware │ aac_at            │ AudioToolbox AAC (macOS) │ ✅       │
└───────┴──────────┴───────────────────┴──────────────────────────┴──────────┘
```

### 4. Run Installation Test

```bash
python test_installation.py
```

This runs comprehensive tests to ensure everything is working correctly.

## Troubleshooting

### Common Issues

??? question "FFmpeg not found"
    
    **Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`
    
    **Solution:**
    1. Verify FFmpeg is installed: `ffmpeg -version`
    2. Check if FFmpeg is in PATH: `which ffmpeg` (Unix) or `where ffmpeg` (Windows)
    3. Restart terminal/command prompt after installation
    4. On Windows, ensure FFmpeg bin directory is in PATH environment variable

??? question "Permission denied errors"
    
    **Error:** `PermissionError: [Errno 13] Permission denied`
    
    **Solutions:**
    1. Use virtual environment: `python -m venv venv && source venv/bin/activate`
    2. Install with `--user` flag: `pip install --user hls-converter`
    3. On Linux/macOS, avoid using `sudo` with pip

??? question "Hardware encoders not detected"
    
    **Issue:** Only software encoders are available
    
    **Solutions:**
    1. Update GPU drivers to latest version
    2. Verify GPU supports hardware encoding
    3. Check FFmpeg was compiled with hardware support:
       ```bash
       ffmpeg -hide_banner -encoders | grep -i nvenc  # NVIDIA
       ffmpeg -hide_banner -encoders | grep -i videotoolbox  # macOS
       ffmpeg -hide_banner -encoders | grep -i qsv  # Intel
       ```

??? question "Import errors after installation"
    
    **Error:** `ModuleNotFoundError: No module named 'hls_converter'`
    
    **Solutions:**
    1. Verify installation: `pip list | grep hls-converter`
    2. Check Python version: `python --version` (requires 3.8+)
    3. If using virtual environment, ensure it's activated
    4. Try reinstalling: `pip uninstall hls-converter && pip install hls-converter`

??? question "Slow conversion performance"
    
    **Issues:** Conversion is slower than expected
    
    **Solutions:**
    1. Enable hardware acceleration (check `--list-encoders`)
    2. Use faster preset: `--preset ultrafast`
    3. Reduce parallel workers if system is constrained: `--workers 2`
    4. Convert to SSD storage instead of network drives
    5. Close other resource-intensive applications

### Getting Help

If you're still having issues:

1. **Check the logs** with `--debug` flag for detailed error information
2. **Search existing issues** on [GitHub Issues](https://github.com/your-username/hls-converter/issues)
3. **Create a new issue** with:
   - Your operating system and version
   - Python version (`python --version`)
   - FFmpeg version (`ffmpeg -version`)  
   - Complete error message
   - Steps to reproduce the problem

## Next Steps

Once installation is complete:

- [📚 Quick Start Guide](quickstart.md) - Convert your first video
- [⚙️ Configuration](configuration.md) - Customize settings
- [🔧 CLI Reference](cli.md) - Explore all options
- [🐍 Python API](api/index.md) - Integrate into your code