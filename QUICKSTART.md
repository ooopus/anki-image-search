# Quick Start Guide

Get started with Anki Image Search in 5 minutes!

## Installation

### For Users

1. Download `AnkiImageSearch.ankiaddon` (when available)
2. In Anki: **Tools → Add-ons → Install from file**
3. Select the downloaded file
4. Restart Anki

### For Developers

```bash
# 1. Install dependencies to vendor folder
cd D:\code\AnkiImageSearch
pip install --target=src/vendor -r requirements.txt

# 2. Compile translations
cd src
pybabel compile -d locales
cd ..

# 3. Install to Anki (Windows example)
# Create symlink to Anki addons folder
mklink /D "%APPDATA%\Anki2\addons21\AnkiImageSearch" "D:\code\AnkiImageSearch\src"

# 4. Restart Anki
```

## First Use

### 1. Configure the Add-on

1. Open Anki
2. Go to **Tools → Image Search Settings** (图片搜索设置)
3. Set up your fields:
   - **Search Field**: `Word` (or whatever field contains your search terms)
   - **Target Field**: `Picture` (or whatever field should receive images)
4. Click **OK**

### 2. Add Images to Your Cards

1. Open or create a note with your search term
   - Example: Add "cat" to the Word field
2. Click the **🔍** button in the editor toolbar
   - Shortcut: **Ctrl+Shift+I**
3. Wait for images to load (a few seconds)
4. Click on an image you like
5. Click **Insert Image** (插入图片)
6. Done! The image is now in your Picture field

## Example Setup

### Japanese Learning

**Configuration:**
```
Search Field: Expression
Target Field: Picture
Max Results: 20
```

**Usage:**
- Add "追い出す" → Get images of "chasing out"
- Add "桜" → Get images of cherry blossoms
- Add "猫" → Get images of cats

### English Vocabulary

**Configuration:**
```
Search Field: Word
Target Field: Image
Max Results: 15
```

**Usage:**
- Add "elephant" → Get elephant images
- Add "mountain" → Get mountain images
- Add "celebration" → Get celebration images

## Tips

1. **Use specific search terms** for better results
2. **Start with 15-20 max results** for good balance
3. **Use Medium quality** for everyday use
4. **The image is stored permanently** in Anki's media folder
5. **Images sync with AnkiWeb** like any other media

## Keyboard Shortcut

- **Ctrl+Shift+I**: Open image search (when in editor)

## Troubleshooting

### Button not showing?
- Check: Tools → Add-ons → make sure it's enabled
- Restart Anki

### "Search field not found"?
- Go to Tools → Image Search Settings
- Update the field name to match your note type

### No images loading?
- Check internet connection
- Try a different search term
- Google may rate-limit (wait a few minutes)

## What's Next?

- Read [USAGE.md](USAGE.md) for detailed usage guide
- Read [BUILD.md](BUILD.md) for development instructions
- Customize settings: Tools → Image Search Settings

## Support

Having issues? Check:
1. [USAGE.md](USAGE.md) - Full usage guide
2. [BUILD.md](BUILD.md) - Build and installation
3. Anki Debug Console - Tools → Debug Console (for error messages)
