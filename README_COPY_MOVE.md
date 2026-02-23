# Voice Authentication System - Copy/Move Feature

## Overview
This updated version of the voice authentication system includes a **Copy/Move** feature for file uploads, giving users control over whether to keep or permanently delete the original files from their system.

## Key Changes

### 1. **Modified app.py**
- Added `platform` and `subprocess` imports for cross-platform file deletion
- Created `permanent_delete()` function that securely deletes files across Windows, Linux, and macOS
- Updated `upload_media()` route to handle both copy and move operations
- Added message types (success, error, warning, info) for better user feedback

### 2. **New upload.html Template**
- Modern, user-friendly interface with clear copy/move options
- Radio buttons for selecting operation type (Copy or Move)
- Warning messages for move operations
- Optional file path input for specifying the original file location
- Visual feedback and confirmation dialogs
- Responsive design with gradient styling

## Features

### Copy Operation (Default)
- Uploads file to encrypted hidden area
- **Keeps the original file** on your computer
- Safe option with no data loss risk

### Move Operation
- Uploads file to encrypted hidden area
- **Permanently deletes the original file** from your system
- Bypasses recycle bin (file cannot be recovered)
- Requires confirmation before deletion
- Optional: Provide original file path for automatic deletion

## How It Works

### Permanent Deletion Process

The `permanent_delete()` function uses platform-specific methods:

**Windows:**
- Overwrites file with zeros before deletion
- Uses `os.remove()` (bypasses recycle bin when done programmatically)

**Linux:**
- Uses `shred -vfz -n 3` command for secure deletion
- Overwrites file multiple times before removal
- Falls back to `os.remove()` if shred is unavailable

**macOS:**
- Uses `rm -P` for secure deletion
- Falls back to `os.remove()` if command fails

## Usage Instructions

### 1. Basic Upload (Copy Mode)
```
1. Navigate to Upload page
2. Select a file
3. Keep "Copy" option selected (default)
4. Click "Upload File"
5. Original file remains on your computer
```

### 2. Secure Upload (Move Mode)
```
1. Navigate to Upload page
2. Select a file
3. Choose "Move" option
4. (Optional) Enter the full path to the original file
5. Click "Upload File"
6. Confirm the deletion warning
7. Original file is permanently deleted
```

### 3. File Path Examples

**Windows:**
```
C:\Users\YourName\Pictures\vacation.jpg
D:\Documents\report.pdf
```

**Linux/macOS:**
```
/home/username/Pictures/vacation.jpg
/Users/username/Documents/report.pdf
```

## Security Features

### Encryption
- All uploaded files are encrypted using Fernet (symmetric encryption)
- Files are encrypted **before** being saved to disk
- Only authenticated users can decrypt and view their files

### Permanent Deletion
- Files deleted using move operation cannot be recovered
- Multiple overwrite passes on Linux (using shred)
- Secure deletion on macOS (using rm -P)
- Zero-overwrite on Windows before deletion

### Authentication
- Voice biometric authentication required
- Deep learning model for speaker verification
- Confidence threshold (70%) for authentication

## Supported File Types

- **Images:** JPG, JPEG, PNG, GIF
- **Videos:** MP4, MOV, MKV
- **Documents:** PDF, DOC, DOCX

## Important Warnings

⚠️ **Move Operation Warnings:**
1. Deleted files **CANNOT** be recovered from recycle bin
2. Deletion is **PERMANENT** and irreversible
3. Always verify the file path before moving
4. Keep backups of important files
5. Test with non-important files first

## Installation Requirements

### New Dependencies
The updated system requires these additional packages:

```bash
# No new pip packages required, but ensure you have:
- platform (built-in)
- subprocess (built-in)
```

### Optional Tools for Enhanced Security

**Linux:**
```bash
sudo apt-get install coreutils  # For shred command
```

**macOS:**
```bash
# rm -P is built-in, no installation needed
```

## File Structure

```
project/
├── app.py                 # Main Flask application (UPDATED)
├── templates/
│   ├── index.html        # Login/signup page
│   ├── hidden.html       # Protected media area
│   └── upload.html       # Upload page (NEW)
├── dataset/              # Voice samples
├── models/               # Trained models
├── protected_media/      # Encrypted user files
└── filekey.key          # Encryption key
```

## Configuration

### Security Settings in app.py

```python
# Confidence threshold for voice authentication
CONF_THRESHOLD = 0.7  # 70% confidence required

# Recording settings
FS = 16000           # Sample rate
SECONDS = 5          # Recording duration

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif",
    "mp4", "mov", "mkv",
    "pdf", "doc", "docx"
}
```

## Troubleshooting

### File Path Issues
**Problem:** Original file not deleted after move operation
**Solution:** 
- Ensure you provided the complete, absolute file path
- Check file permissions (you must have delete rights)
- Verify the file exists at the specified location

### Browser Security
**Problem:** Cannot auto-populate file path
**Solution:**
- Browsers restrict access to file paths for security
- You must manually enter the full file path
- Copy-paste the path from File Explorer/Finder

### Permission Errors
**Problem:** "Permission denied" when deleting files
**Solution:**
- Close any programs using the file
- Check if file is read-only
- Run the application with appropriate permissions
- Ensure you own the file or have delete rights

## Best Practices

1. **Test First:** Try with non-important files before moving valuable data
2. **Verify Paths:** Always double-check file paths before moving
3. **Keep Backups:** Maintain separate backups of important files
4. **Use Copy Mode:** Use copy mode by default, move only when necessary
5. **Monitor Space:** Encrypted files take up storage space

## Technical Details

### Encryption Method
- **Algorithm:** Fernet (symmetric encryption)
- **Key Storage:** filekey.key file
- **Key Generation:** One-time generation, reusable

### Deletion Security Levels

**High (Linux with shred):**
- 3 passes of random data overwrite
- File content completely destroyed
- Metadata partially preserved

**Medium (macOS with rm -P):**
- Overwrites before deletion
- Secure removal

**Standard (Windows, fallbacks):**
- Direct deletion bypassing recycle bin
- Optional zero-overwrite

## Future Enhancements

Potential improvements for future versions:
1. Drag-and-drop file upload
2. Batch file upload
3. Progress bars for large files
4. File size limits and warnings
5. Storage quota management
6. File preview before upload
7. Move confirmation via email
8. Deletion audit log

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages in the Flask console
3. Verify file permissions and paths
4. Test with different file types

## License & Disclaimer

**Disclaimer:** This software permanently deletes files when using move operation. The developers are not responsible for data loss. Users should:
- Maintain proper backups
- Test thoroughly before production use
- Understand the risks of permanent deletion
- Verify compliance with local data regulations

---

**Version:** 2.0  
**Last Updated:** January 2026  
**Author:** Voice Auth System Team
