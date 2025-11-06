# hooks.py - Anki Hook Implementations

from aqt.editor import Editor

from .state import get_config


def setup_editor_button(buttons: list[str], editor: Editor):
    """Add image search button to editor toolbar"""
    config = get_config()

    if not config.enabled:
        return buttons

    # Create button HTML
    button = editor.addButton(
        icon=None,
        cmd="image_search",
        func=lambda e: on_image_search_clicked(e),
        tip="Search and insert images (Ctrl+Shift+I)",
        keys="Ctrl+Shift+I",
        label="🔍",
    )

    buttons.append(button)
    return buttons


def on_image_search_clicked(editor: Editor):
    """Handle image search button click"""
    print("[Hooks] 图片搜索按钮被点击")
    from aqt import mw
    from aqt.utils import tooltip

    from .translator import _
    from .ui.browser_picker import show_browser_image_picker

    config = get_config()
    print(f"[Hooks] 配置加载完成")

    # Get current note
    note = editor.note
    if not note:
        print("[Hooks] 错误：未找到笔记")
        tooltip(_("请先选择一个笔记"))
        return

    print(f"[Hooks] 当前笔记ID: {note.id}")

    # Get note type name
    note_type = note.note_type()
    note_type_name = note_type["name"] if note_type else ""
    print(f"[Hooks] 笔记类型: {note_type_name}")

    # Get fields for this note type
    search_field, target_field = config.get_fields_for_note_type(note_type_name)
    print(f"[Hooks] 搜索字段: {search_field}, 目标字段: {target_field}")

    # Validate search field exists
    if search_field not in note:
        print(f"[Hooks] 错误：搜索字段 '{search_field}' 不存在")
        tooltip(_("搜索字段 '{}' 不存在").format(search_field))
        return

    # Get search query
    search_query = note[search_field]
    print(f"[Hooks] 原始搜索内容: {search_query[:100] if search_query else '(空)'}")

    if not search_query or not search_query.strip():
        print("[Hooks] 错误：搜索字段为空")
        tooltip(_("搜索字段为空"))
        return

    # Strip HTML tags from search query
    search_query = mw.col.media.strip(search_query)
    print(f"[Hooks] 清理后的搜索词: {search_query}")

    # Show browser-based image picker dialog
    print("[Hooks] 调用 show_browser_image_picker")
    show_browser_image_picker(editor, search_query, target_field)
