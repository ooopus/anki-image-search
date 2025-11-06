# Usage Guide

## Overview

Anki Image Search is an add-on that allows you to search Google Images directly from the Anki card editor and insert selected images into your notes.

## Features

- 🔍 **Quick Search**: Search Google Images with a single click
- 🖼️ **Visual Selection**: Preview thumbnails before inserting
- ⚙️ **Configurable**: Customize search and target fields
- 🌐 **Multi-language**: Support for English and Chinese
- 💾 **Auto-save**: Images are automatically downloaded and stored in Anki's media folder

## Installation

1. Download the latest `AnkiImageSearch.ankiaddon` file
2. Open Anki
3. Go to **Tools → Add-ons → Install from file**
4. Select the downloaded file
5. Restart Anki

## Basic Usage

### 1. Configure Fields

Before using the add-on, configure which fields to use:

1. Go to **Tools → Image Search Settings**
2. Set **Search Field** to the field containing your search terms (e.g., "Word", "Expression")
3. Set **Target Field** to the field where images should be inserted (e.g., "Picture", "Image")
4. Click **OK** to save

### 2. Search and Insert Images

1. Open a note in the editor
2. Make sure your search field contains a search term (e.g., "cat", "追い出す")
3. Click the 🔍 button in the editor toolbar (or press **Ctrl+Shift+I**)
4. Wait for search results to load
5. Click on an image to select it
6. Click **Insert Image** to add it to your note
7. The image will be automatically downloaded and inserted into the target field

## Configuration Options

Access settings via **Tools → Image Search Settings**

### General Settings

- **Enable Plugin**: Toggle the add-on on/off
- **Language**: Choose interface language (Auto Detect, English, or Simplified Chinese)

### Field Configuration

- **Search Field**: Field name to use as search query
  - Example: "Word", "Front", "Expression"
- **Target Field**: Field name where images will be inserted
  - Example: "Picture", "Image", "Back"

### Search Settings

- **Max Results**: Number of images to display (5-50)
  - Default: 20
  - Higher values = more options but slower loading
- **Image Quality**: Quality preference
  - Low (Fast): Faster loading, lower quality
  - Medium: Balanced quality and speed (recommended)
  - High (Slow): Best quality, slower loading
- **Auto Download and Insert**: Automatically download without confirmation
  - When enabled: Clicking an image immediately inserts it
  - When disabled: You need to click "Insert Image" button

## Tips and Best Practices

### Search Terms

- Use specific, descriptive terms for better results
- For language learning, use native words (e.g., "追い出す" for Japanese)
- Avoid very common words that might have too many results

### Field Setup

- Make sure your note type has the configured fields
- You can use different field names, just update the configuration
- The target field can already contain content - new images will be appended

### Performance

- Start with lower max results (10-15) for faster loading
- Use Medium quality for daily use
- High quality is best for important cards or presentations

### Organization

- Images are stored in Anki's media folder with unique names
- Format: `image_search_[hash].[ext]`
- Media syncing works normally with AnkiWeb

## Keyboard Shortcuts

- **Ctrl+Shift+I**: Open image search (when editor is focused)

## Troubleshooting

### "Search field is empty"
- Make sure the configured search field contains text
- Check that you're using the correct field name in settings

### "Search field 'XXX' does not exist"
- The field name in settings doesn't match your note type
- Go to settings and update the field names to match your note type

### "No images found"
- Try a different search term
- Check your internet connection
- Google may have rate-limited your IP (wait a few minutes and try again)

### Images not loading
- Check your internet connection
- Some images may fail to load due to server issues
- Try searching again or choose a different image

### Button not appearing
- Check if add-on is enabled: Tools → Add-ons
- Restart Anki
- Verify plugin is enabled in settings

## Examples

### Example 1: Language Learning (Japanese)

**Setup:**
- Search Field: "Expression"
- Target Field: "Picture"

**Usage:**
1. Create a note with "追い出す" in Expression field
2. Click 🔍 button
3. Select an appropriate image showing "chasing out" or "expelling"
4. Image is inserted into Picture field

### Example 2: Vocabulary Building (English)

**Setup:**
- Search Field: "Word"
- Target Field: "Image"

**Usage:**
1. Create a note with "butterfly" in Word field
2. Click 🔍 button
3. Select a clear butterfly image
4. Image is inserted into Image field

### Example 3: Geography Study

**Setup:**
- Search Field: "Country"
- Target Field: "Flag"

**Usage:**
1. Create a note with "Japan" in Country field
2. Click 🔍 button
3. Select the Japanese flag image
4. Flag is inserted into Flag field

## Privacy and Data

- The add-on sends search queries to Google Images
- Images are downloaded from their original sources
- No personal data is collected or stored by the add-on
- Images are subject to their original copyright and usage terms

## Support

If you encounter issues:
1. Check this usage guide and troubleshooting section
2. Verify your configuration is correct
3. Try restarting Anki
4. Check the Anki console for error messages (Tools → Debug Console)

## Credits

This add-on uses:
- Google Images for image search
- BeautifulSoup for HTML parsing
- Requests for HTTP operations
