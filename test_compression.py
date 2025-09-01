#!/usr/bin/env python3
"""
Test script to verify tar.gz compression functionality
"""
import tarfile
import tempfile
from pathlib import Path

def test_tar_compression():
    """Test creating a tar.gz file"""
    # Create temporary files to compress
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create some test files
        test_file1 = temp_path / "database1.sql"
        test_file2 = temp_path / "database2.sql"
        
        test_file1.write_text("-- Database 1 backup\nCREATE TABLE test1 (id INT);")
        test_file2.write_text("-- Database 2 backup\nCREATE TABLE test2 (id INT);")
        
        # Create tar.gz file
        tar_file = temp_path / "test_backup.tar.gz"
        
        print("Creating tar.gz archive...")
        try:
            with tarfile.open(tar_file, 'w:gz') as tf:
                tf.add(test_file1, arcname=test_file1.name)
                tf.add(test_file2, arcname=test_file2.name)
            
            print(f"✅ Successfully created: {tar_file}")
            print(f"📊 File size: {tar_file.stat().st_size} bytes")
            
            # List contents
            print("\n📦 Archive contents:")
            with tarfile.open(tar_file, 'r:gz') as tf:
                for member in tf.getmembers():
                    print(f"  - {member.name} ({member.size} bytes)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating tar.gz: {e}")
            return False

if __name__ == "__main__":
    print("Testing tar.gz compression functionality...")
    success = test_tar_compression()
    if success:
        print("\n🎉 Tar.gz compression test passed!")
    else:
        print("\n💥 Tar.gz compression test failed!")
