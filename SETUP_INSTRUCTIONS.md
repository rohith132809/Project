# Setup Instructions - Single HTML File Integration

## Overview
Your voice authentication system now uses:
1. **One HTML file** (`voice-auth-complete.html`) - Contains all pages
2. **Updated Flask app** (`app_api.py`) - Provides API endpoints

## File Structure

```
your_project/
├── app_api.py                    # NEW - Flask app with API endpoints
├── voice-auth-complete.html      # NEW - Single unified HTML file
├── feature_extraction.py          # Your existing file
├── train_model_dl.py             # Your existing file
├── filekey.key                   # Encryption key (generate if missing)
├── dataset/                      # Voice samples storage
├── models/                       # Trained models storage
└── protected_media/              # Encrypted media storage
```

## Setup Steps

### 1. Replace Your Files

**Option A: Rename the new files**
```bash
# Backup your old files first
mv app.py app_old.py

# Rename the new API-enabled app
mv app_api.py app.py

# The HTML file should be in the same directory as app.py
```

**Option B: Use the new files directly**
```bash
# Run with the new filename
python app_api.py
```

### 2. Place HTML File Correctly

The `voice-auth-complete.html` file must be in the **same directory** as your Flask app (app.py or app_api.py).

```
your_project/
├── app.py (or app_api.py)
├── voice-auth-complete.html      ← Must be here!
├── feature_extraction.py
└── ...
```

### 3. Verify Your Flask App Route

In your Flask app, the main route serves the HTML file:

```python
@app.route("/")
def index():
    """Serve the single unified HTML page"""
    return send_from_directory(".", "voice-auth-complete.html")
```

This route looks for `voice-auth-complete.html` in the current directory.

## Key Changes from Original

### Old System (Multiple Templates)
```
app.py uses:
├── render_template("index.html")      # Auth page
├── render_template("hidden.html")     # Media page
└── render_template("upload.html")     # Upload page
```

### New System (Single HTML + API)
```
app_api.py provides:
├── GET  /                        → Serves voice-auth-complete.html
├── POST /api/authenticate        → Voice signup/signin
├── GET  /api/media/list         → List user's media files
├── GET  /api/media/<filename>   → Serve encrypted media
├── POST /api/upload             → Upload with copy/move
└── POST /api/logout             → Clear session
```

## API Endpoints Explained

### 1. Authentication Endpoint
**POST** `/api/authenticate`

**Request:**
```json
{
  "username": "john",
  "action": "signup"  // or "signin"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Voice recorded successfully",
  "type": "success",
  "extra": "User has 1 sample(s)"
}
```

### 2. List Media Endpoint
**GET** `/api/media/list`

**Response:**
```json
{
  "success": true,
  "username": "john",
  "images": ["photo1.jpg", "photo2.png"],
  "videos": ["video1.mp4"]
}
```

### 3. Upload Endpoint
**POST** `/api/upload`

**Form Data:**
- `file`: The file to upload
- `operation`: "copy" or "move"
- `original_path`: (Optional) Full path for deletion

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "type": "success"
}
```

## How It Works

1. **User visits** `http://localhost:5000/`
2. **Flask serves** `voice-auth-complete.html`
3. **JavaScript in HTML** makes API calls to Flask endpoints
4. **Flask processes** requests and returns JSON
5. **JavaScript updates** the UI dynamically

## Running the Application

```bash
# Make sure you're in the project directory
cd your_project

# Run the Flask app
python app_api.py

# Or if you renamed it:
python app.py

# Open browser to:
# http://localhost:5000
```

## Troubleshooting

### Problem: "404 Not Found" when visiting the main page

**Solution:**
```bash
# Check if HTML file is in the same directory as app.py
ls -l voice-auth-complete.html

# If not, move it:
mv /path/to/voice-auth-complete.html .
```

### Problem: "API endpoint not found"

**Solution:**
Make sure you're using `app_api.py` (or renamed it to `app.py`), not your old app.py file.

### Problem: "No module named 'feature_extraction'"

**Solution:**
Keep your existing `feature_extraction.py` and `train_model_dl.py` files in the same directory.

### Problem: "FileNotFoundError: filekey.key"

**Solution:**
Generate the encryption key:

```python
# Create a file: generate_key.py
from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("filekey.key", "wb") as f:
    f.write(key)

print("Encryption key generated!")
```

Then run:
```bash
python generate_key.py
```

## Important Notes

### ⚠️ No Templates Folder Needed
The single HTML file eliminates the need for a `templates/` folder. Everything is in one file.

### ⚠️ Session Management
Sessions are still managed server-side by Flask. The HTML just displays the UI.

### ⚠️ File Location for Move Operation
When using the "Move" feature, users must provide the **full absolute path** to the original file:
- Windows: `C:\Users\John\Pictures\photo.jpg`
- Linux: `/home/john/Pictures/photo.jpg`
- macOS: `/Users/john/Pictures/photo.jpg`

## Testing the System

### Test Copy Operation
1. Sign up with username
2. Go to Upload page
3. Select "Copy" option
4. Choose a file
5. Click Upload
6. **Result:** File uploaded, original remains

### Test Move Operation
1. Go to Upload page
2. Select "Move" option
3. Enter full file path
4. Choose the same file
5. Confirm deletion warning
6. Click Upload
7. **Result:** File uploaded, original **permanently deleted**

## Advantages of Single HTML File

✅ **Simpler deployment** - One HTML file to manage
✅ **Faster page transitions** - No page reloads
✅ **Better UX** - Smooth animations between pages
✅ **Easier maintenance** - All frontend code in one place
✅ **API-driven** - Clean separation of frontend/backend

## Security Considerations

1. **Change the secret key** in production:
   ```python
   app.secret_key = "your-secure-random-key-here"
   ```

2. **Use HTTPS** in production
3. **Implement rate limiting** for authentication attempts
4. **Add CSRF protection** for forms
5. **Validate file paths** before deletion

## Next Steps

1. ✅ Replace your old app.py with app_api.py
2. ✅ Place voice-auth-complete.html in the project root
3. ✅ Test the authentication flow
4. ✅ Test the copy/move upload functionality
5. ✅ Generate encryption key if missing
6. ✅ Customize secret key for production

---

**Need Help?**
- Check Flask console for error messages
- Verify file locations
- Test API endpoints with curl or Postman
- Review browser console for JavaScript errors
