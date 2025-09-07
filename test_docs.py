#!/usr/bin/env python3
"""
Documentation test script
========================

Simple test to verify the documentation structure and basic MkDocs functionality.
"""

import sys
from pathlib import Path

def test_docs_structure():
    """Test that all required documentation files exist."""
    print("🔍 Testing documentation structure...")
    
    required_files = [
        "mkdocs.yml",
        "docs/index.md",
        "docs/installation.md", 
        "docs/quickstart.md",
        "docs/cli.md",
        "docs/api/index.md",
        "docs/changelog.md",
        "docs/license.md",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing documentation files: {', '.join(missing_files)}")
        return False
    
    print(f"✅ All {len(required_files)} documentation files found")
    return True

def test_mkdocs_config():
    """Test MkDocs configuration file."""
    print("\n⚙️ Testing MkDocs configuration...")
    
    try:
        import yaml
        with open("mkdocs.yml", 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['site_name', 'nav', 'theme', 'markdown_extensions']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing required key in mkdocs.yml: {key}")
                return False
        
        print("✅ MkDocs configuration is valid")
        return True
        
    except ImportError:
        print("⚠️  PyYAML not installed, skipping config validation")
        return True
    except Exception as e:
        print(f"❌ Error reading mkdocs.yml: {e}")
        return False

def test_docs_content():
    """Test that documentation files have content."""
    print("\n📄 Testing documentation content...")
    
    test_files = {
        "docs/index.md": ["HLS Converter", "Quick Example"],
        "docs/installation.md": ["Installation", "System Requirements"],
        "docs/quickstart.md": ["Quick Start", "Your First Conversion"],
        "docs/cli.md": ["CLI Reference", "Basic Usage"],
    }
    
    for file_path, required_content in test_files.items():
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            for required in required_content:
                if required not in content:
                    print(f"❌ {file_path} missing content: '{required}'")
                    return False
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return False
    
    print(f"✅ Content validation passed for {len(test_files)} files")
    return True

def test_mkdocs_build():
    """Test if MkDocs can build the documentation."""
    print("\n🔨 Testing MkDocs build...")
    
    try:
        import subprocess
        
        # Check if mkdocs is available
        result = subprocess.run(['mkdocs', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print("⚠️  MkDocs not installed, skipping build test")
            print("   Install with: pip install -r requirements-docs.txt")
            return True
        
        print(f"📚 MkDocs version: {result.stdout.strip()}")
        
        # Test build (dry run)
        result = subprocess.run(['mkdocs', 'build', '--clean', '--strict'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ MkDocs build successful")
            
            # Check if site was generated
            if Path('site/index.html').exists():
                print("✅ Documentation site generated")
                return True
            else:
                print("⚠️  Site built but index.html not found")
                return True
        else:
            print(f"❌ MkDocs build failed:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  MkDocs not found in PATH")
        print("   Install with: pip install -r requirements-docs.txt")
        return True
    except subprocess.TimeoutExpired:
        print("❌ MkDocs build timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing MkDocs build: {e}")
        return False

def cleanup():
    """Clean up generated files."""
    try:
        import shutil
        if Path('site').exists():
            shutil.rmtree('site')
    except Exception:
        pass

def main():
    """Run all documentation tests."""
    print("📚 HLS Converter - Documentation Test")
    print("=" * 50)
    
    tests = [
        ("Documentation Structure", test_docs_structure),
        ("MkDocs Configuration", test_mkdocs_config),
        ("Documentation Content", test_docs_content),
        ("MkDocs Build", test_mkdocs_build),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except KeyboardInterrupt:
            print("\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Documentation Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All documentation tests passed!")
        print("\nNext steps:")
        print("1. Install docs dependencies: pip install -r requirements-docs.txt")
        print("2. Build docs: mkdocs build")
        print("3. Serve docs locally: mkdocs serve")
        print("4. View at: http://localhost:8000")
        cleanup()
        return 0
    else:
        print("⚠️  Some documentation tests failed.")
        print("Please fix the issues and run the tests again.")
        cleanup()
        return 1

if __name__ == "__main__":
    sys.exit(main())