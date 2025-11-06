# Build Instructions

This document provides instructions for building and installing the Anki Image Search add-on.

## Prerequisites

- Python 3.9 or higher
- Anki 25.07 or higher installed

## Development Setup

1. **Clone or download the repository**
   ```bash
   cd D:\code\AnkiImageSearch
   ```

2. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install babel
   ```

3. **Compile translations** (if you modified translation files)
   ```bash
   cd src
   pybabel compile -d locales
   ```

## Building the Add-on

### Method 1: Manual Build

1. **Install runtime dependencies to vendor directory**
   ```bash
   pip install --target=src/vendor -r requirements.txt
   ```

2. **Compile translations**
   ```bash
   cd src
   pybabel compile -d locales
   cd ..
   ```

3. **Create the .ankiaddon file**

   On Windows (PowerShell):
   ```powershell
   Compress-Archive -Path src\* -DestinationPath AnkiImageSearch.ankiaddon -Force
   ```

   On Linux/Mac:
   ```bash
   cd src
   zip -r ../AnkiImageSearch.ankiaddon *
   cd ..
   ```

### Method 2: Development Installation

For development, you can symlink the `src` directory to Anki's add-ons folder:

1. **Locate Anki add-ons directory**
   - Windows: `%APPDATA%\Anki2\addons21\`
   - macOS: `~/Library/Application Support/Anki2/addons21/`
   - Linux: `~/.local/share/Anki2/addons21/`

2. **Create a directory with any name (e.g., `AnkiImageSearch`)**
   ```bash
   # Windows
   mkdir "%APPDATA%\Anki2\addons21\AnkiImageSearch"

   # Linux/Mac
   mkdir ~/.local/share/Anki2/addons21/AnkiImageSearch
   ```

3. **Copy or symlink the contents of `src` directory**

   On Windows (as Administrator):
   ```powershell
   mklink /D "%APPDATA%\Anki2\addons21\AnkiImageSearch" "D:\code\AnkiImageSearch\src"
   ```

   On Linux/Mac:
   ```bash
   ln -s /path/to/AnkiImageSearch/src ~/.local/share/Anki2/addons21/AnkiImageSearch
   ```

4. **Restart Anki**

## Translation Workflow

### Extract translatable strings
```bash
cd src
pybabel extract -F babel.cfg -o locales/messages.pot .
```

### Update existing translations
```bash
pybabel update -i locales/messages.pot -d locales
```

### Compile translations (required before using)
```bash
pybabel compile -d locales
```

## Code Quality

### Run linter
```bash
ruff check src/
```

### Auto-fix issues
```bash
ruff check --fix src/
```

### Format code
```bash
ruff format src/
```

## Testing

After installation:

1. Open Anki
2. Create a test note with fields like "Word" and "Picture"
3. Add a word to the "Word" field
4. Click the 🔍 button in the editor
5. Select an image from the search results
6. Verify the image is inserted into the "Picture" field

## Troubleshooting

### Import errors for requests/beautifulsoup4
Make sure you installed dependencies to the `src/vendor` directory:
```bash
pip install --target=src/vendor -r requirements.txt
```

### Translation not working
Compile the translation files:
```bash
cd src
pybabel compile -d locales
```

### Button not appearing in editor
1. Check if the add-on is enabled in Tools → Add-ons
2. Restart Anki
3. Check the configuration: Tools → Image Search Settings → Enable Plugin

### No images found
1. Check your internet connection
2. Try a different search term
3. Google may have rate-limited your IP (wait a few minutes)
