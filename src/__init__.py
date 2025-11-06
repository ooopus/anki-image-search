# __init__.py (Anki Image Search Plugin Main File)

from anki.buildinfo import version as anki_version
from aqt import QAction, gui_hooks, mw

# --- Anki Version Check ---
MIN_ANKI_VERSION = "25.07"


def parse_version(version_str: str) -> tuple[int, int] | None:
    """Parse version string like '25.07.2' into (25, 7)"""
    try:
        parts = version_str.split(".")
        if len(parts) >= 2:
            major = int(parts[0])
            minor = int(parts[1])
            return (major, minor)
    except (ValueError, IndexError):
        pass
    return None


def check_anki_version() -> bool:
    """Check if the current Anki version meets the minimum requirement."""
    required = parse_version(MIN_ANKI_VERSION)
    current = parse_version(anki_version)

    if required is None:
        from aqt.utils import tooltip

        from .translator import _

        tooltip(_("无法解析最低支持版本: {}").format(MIN_ANKI_VERSION))
        return False

    is_parsable = current is not None
    is_sufficient = is_parsable and current >= required

    if not is_sufficient:
        from aqt.utils import showWarning, tooltip

        from .translator import _

        if is_parsable:
            showWarning(
                _(
                    "此插件需要 Anki {} 或更高版本。\n"
                    "当前版本: {}\n\n"
                    "请更新 Anki 以使用此插件。"
                ).format(MIN_ANKI_VERSION, anki_version)
            )
        else:
            tooltip(_("无法解析Anki版本: {}").format(anki_version))
        return False

    return True


def setup_plugin():
    """Loads config, sets up hooks, and adds menu item."""
    if not check_anki_version():
        return  # Stop setup if version is too old

    # Add the 'vendor' directory to Python's path
    import sys
    from pathlib import Path

    vendor_dir = Path(__file__).resolve().parent / "vendor"
    if vendor_dir.exists() and str(vendor_dir) not in sys.path:
        sys.path.insert(0, str(vendor_dir))

    from .hooks import setup_editor_button

    # Setup editor button
    gui_hooks.editor_did_init_buttons.append(setup_editor_button)

    # Add menu item
    add_menu_item()


# ---Startup---
# This code runs when Anki loads the addon
if __name__ != "__main__":
    mw.progress.single_shot(100, setup_plugin, False)  # Run once after 100ms delay


def add_menu_item():
    """Add menu item to Tools menu"""
    from .translator import _

    action = QAction(_("图片搜索设置..."), mw)
    action.triggered.connect(show_config_dialog)

    if hasattr(mw, "form") and hasattr(mw.form, "menuTools"):
        mw.form.menuTools.addAction(action)
    else:
        from aqt.utils import tooltip

        tooltip(_("警告: 无法添加图片搜索菜单项"), period=3000)


def show_config_dialog():
    """Show the configuration dialog."""
    from .state import get_app_state
    from .ui.config.dialog import ConfigDialog

    app_state = get_app_state()
    dialog = ConfigDialog(config=app_state.config)
    if dialog.exec():
        # Config is saved within the dialog
        pass
