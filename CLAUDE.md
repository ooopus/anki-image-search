# CLAUDE.md

This file provides guidance to Claude Code when working with this Anki Image Search add-on.

## Project Overview

An Anki add-on that integrates Google Images search into the card editor. Users can search for images based on note field content and insert selected images into specified fields.

**Add-on Code**: TBD
**Minimum Anki Version**: 25.07
**Python Version**: 3.9+

## Architecture

### Core Components

- **`src/__init__.py`** - Entry point: version check, vendor setup, hook registration, menu creation
- **`src/state.py`** - Singleton `AppState` manages config and runtime state
- **`src/hooks.py`** - Anki hook implementations for editor integration (button + click handler)
- **`src/image_search.py`** - Google Images search and download logic (legacy HTML parsing)

### Configuration System

- **`src/config/types.py`** - `AppConfig` dataclass with defaults
- **`src/config/config.py`** - Load/save configuration logic
- **`src/config/enums.py`** - Enums for configuration options
- **`src/config/constants.py`** - Constants and defaults

Config stored in: `src/user_files/config.json`

### UI Components

- **`src/ui/config/dialog.py`** - Main configuration dialog
- **`src/ui/config/general.py`** - General settings tab
- **`src/ui/browser_picker.py`** - **[NEW]** Browser-based image picker using QWebEngineView
  - Embeds Google Images search page directly
  - Users click/right-click images to select
  - JavaScript injection for image selection handling
  - Avoids HTML parsing brittleness
- **`src/ui/image_picker.py`** - **[DEPRECATED]** Old thumbnail grid picker (HTML parsing approach)

### Translation System

Uses Babel for i18n:
- Supported languages: English (en_US), Chinese (zh_CN)
- Translation files: `src/locales/{lang}/LC_MESSAGES/messages.po`
- Template: `src/locales/messages.pot`

### Vendored Dependencies

Runtime dependencies in `src/vendor/`:
- `beautifulsoup4` - HTML parsing for image extraction
- `requests` - HTTP requests for image search and download

## Development Commands

### Translation Workflow

Extract strings:
```bash
cd src
pybabel extract -F babel.cfg -o locales/messages.pot .
```

Initialize language:
```bash
pybabel init -i locales/messages.pot -d locales -l <lang_code>
```

Update translations:
```bash
pybabel update -i locales/messages.pot -d locales
```

Compile translations:
```bash
pybabel compile -d locales
```

### Code Quality

Lint:
```bash
ruff check src/
```

Auto-fix:
```bash
ruff check --fix src/
```

Format:
```bash
ruff format src/
```

### Building Add-on

1. Install dependencies: `pip install --target=src/vendor -r requirements.txt`
2. Zip the `src/` directory
3. Rename to `.ankiaddon` extension

## Code Patterns

### Browser-Based Image Selection (Current Approach)

```python
from .ui.browser_picker import show_browser_image_picker

# Show embedded browser with Google Images
show_browser_image_picker(editor, search_query="cat", target_field="Picture")

# User interaction flow:
# 1. Google Images loads in QWebEngineView
# 2. User browses and clicks/right-clicks image
# 3. JavaScript extracts image URL
# 4. Download and insert via save_image_to_media()
```

### Legacy HTML Parsing (Deprecated)

```python
from .image_search import GoogleImageSearch

searcher = GoogleImageSearch()
results = searcher.search(query="hello", max_results=20)
# results = [{"url": "...", "thumbnail": "...", "title": "..."}, ...]

# Note: This approach is fragile due to Google's frequent HTML changes
```

### Image Download

```python
from .image_search import GoogleImageSearch, save_image_to_media

searcher = GoogleImageSearch()
image_data = searcher.download_image(image_url)
filename = save_image_to_media(image_data, image_url, note)
# Returns filename in Anki media folder
```

### Editor Button

```python
# Defined in hooks.py
def setup_editor_button(buttons, editor):
    button = editor.addButton(cmd="image_search", func=on_image_search_clicked, ...)
    buttons.append(button)
```

## Important Notes

- **Browser-Based Approach**: Uses QWebEngineView to embed Google Images directly
  - **Advantages**:
    - No HTML parsing - immune to Google's layout changes
    - Better user experience - real Google Images interface
    - Bypasses anti-scraping - browser-like behavior
    - No need to maintain CSS selectors
  - **Implementation**: JavaScript injection to capture user clicks on images

- **Media Folder**: Images saved to Anki's media folder using unique filenames
- **Error Handling**: Handle network errors gracefully with user feedback
- **Image Format**: Support JPG, PNG, GIF, WebP formats

## Key Design Decisions

### Why QWebEngineView over HTML Parsing?

The original approach used BeautifulSoup to parse Google Images HTML:
- **Problem**: Google frequently changes HTML structure (`class="islrc"` → `class="DS1iW"`)
- **Problem**: User-Agent sensitivity - different UAs return different HTML
- **Problem**: Anti-scraping detection

**Solution**: Embed full browser (QWebEngineView)
- Users browse real Google Images interface
- JavaScript extracts clicked image URLs
- Stable and maintainable long-term
