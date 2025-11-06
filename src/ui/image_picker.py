# ui/image_picker.py - Image Selection Dialog

from typing import Any

from aqt import mw
from aqt.qt import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    Qt,
)
from aqt.utils import showWarning, tooltip

from ..config.constants import GRID_COLUMNS, IMAGE_PICKER_HEIGHT, IMAGE_PICKER_WIDTH
from ..image_search import (
    GoogleImageSearch,
    insert_image_to_field,
    save_image_to_media,
)
from ..translator import _


class ImageThumbnail(QWidget):
    """Widget displaying a single image thumbnail"""

    def __init__(self, image_data: dict[str, Any], parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.selected = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Image label (will load thumbnail asynchronously)
        self.image_label = QLabel()
        self.image_label.setFixedSize(180, 180)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.image_label.setStyleSheet(
        #     "QLabel { border: 2px solid #ccc;}"
        # )
        self.image_label.setText(_("加载中..."))

        # Title label
        title = self.image_data.get("title", "")
        if len(title) > 30:
            title = title[:27] + "..."
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)

        layout.addWidget(self.image_label)
        layout.addWidget(self.title_label)
        self.setLayout(layout)

        # Load thumbnail
        self.load_thumbnail()

    def load_thumbnail(self):
        """Load thumbnail image asynchronously"""
        from aqt.qt import QPixmap, QThread, pyqtSignal

        class ThumbnailLoader(QThread):
            finished = pyqtSignal(bytes)
            error = pyqtSignal(str)

            def __init__(self, url):
                super().__init__()
                self.url = url

            def run(self):
                try:
                    searcher = GoogleImageSearch()
                    image_data = searcher.download_image(self.url)
                    if image_data:
                        self.finished.emit(image_data)
                    else:
                        self.error.emit("Failed to download")
                except Exception as e:
                    self.error.emit(str(e))

        def on_loaded(image_data: bytes):
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data):
                scaled = pixmap.scaled(
                    180,
                    180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled)
            else:
                self.image_label.setText(_("加载失败"))

        def on_error(error: str):
            self.image_label.setText(_("加载失败"))

        # Use thumbnail URL for faster loading
        thumbnail_url = self.image_data.get("thumbnail") or self.image_data.get("url")
        if thumbnail_url and not thumbnail_url.startswith("data:"):
            self.loader = ThumbnailLoader(thumbnail_url)
            self.loader.finished.connect(on_loaded)
            self.loader.error.connect(on_error)
            self.loader.start()
        else:
            self.image_label.setText(_("无效图片"))

    def mousePressEvent(self, event):
        """Handle mouse click to select image"""
        if hasattr(self.parent(), "on_thumbnail_clicked"):
            self.parent().on_thumbnail_clicked(self)

    def set_selected(self, selected: bool):
        """Update selection state"""
        self.selected = selected
        if selected:
            self.image_label.setStyleSheet("QLabel { border: 3px solid #0066cc;}")
        else:
            self.image_label.setStyleSheet("QLabel { border: 2px solid #ccc;}")


class ImagePickerDialog(QDialog):
    """Dialog for selecting images from search results"""

    def __init__(
        self, editor, search_query: str, results: list[dict], target_field: str
    ):
        super().__init__()
        self.editor = editor
        self.search_query = search_query
        self.results = results
        self.target_field = target_field
        self.selected_thumbnail = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(_("选择图片 - {}").format(self.search_query))
        self.resize(IMAGE_PICKER_WIDTH, IMAGE_PICKER_HEIGHT)

        layout = QVBoxLayout()

        # Info label
        info_label = QLabel(_("找到 {} 张图片，点击选择：").format(len(self.results)))
        layout.addWidget(info_label)

        # Scroll area for thumbnails
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Container for thumbnail grid
        container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)

        # Add thumbnails
        row, col = 0, 0
        for result in self.results:
            thumbnail = ImageThumbnail(result, container)
            self.grid_layout.addWidget(thumbnail, row, col)

            col += 1
            if col >= GRID_COLUMNS:
                col = 0
                row += 1

        container.setLayout(self.grid_layout)
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()

        self.insert_button = QPushButton(_("插入图片"))
        self.insert_button.clicked.connect(self.on_insert_clicked)
        self.insert_button.setEnabled(False)

        cancel_button = QPushButton(_("取消"))
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def on_thumbnail_clicked(self, thumbnail: ImageThumbnail):
        """Handle thumbnail selection"""
        # Deselect previous
        if self.selected_thumbnail:
            self.selected_thumbnail.set_selected(False)

        # Select new
        self.selected_thumbnail = thumbnail
        thumbnail.set_selected(True)
        self.insert_button.setEnabled(True)

    def on_insert_clicked(self):
        """Insert selected image into note field"""
        if not self.selected_thumbnail:
            return

        image_data = self.selected_thumbnail.image_data
        image_url = image_data.get("url")

        if not image_url:
            showWarning(_("无效的图片URL"))
            return

        # Show progress
        tooltip(_("正在下载图片..."))

        # Download image
        searcher = GoogleImageSearch()
        downloaded_data = searcher.download_image(image_url)

        if not downloaded_data:
            showWarning(_("下载图片失败"))
            return

        # Save to media folder
        filename = save_image_to_media(downloaded_data, image_url, self.editor.note)

        if not filename:
            showWarning(_("保存图片失败"))
            return

        # Insert into field
        success = insert_image_to_field(self.editor, self.target_field, filename)

        if success:
            tooltip(_("图片已插入到 {}").format(self.target_field))
            self.accept()
        else:
            showWarning(_("插入图片失败"))


def show_image_picker(editor, search_query: str, target_field: str, max_results: int):
    """Show image picker dialog"""
    # Show searching message
    tooltip(_("正在搜索图片..."))

    # Search for images
    searcher = GoogleImageSearch()
    results = searcher.search(search_query, max_results)

    if not results:
        showWarning(_("未找到图片，请尝试其他搜索词"))
        return

    # Show picker dialog
    dialog = ImagePickerDialog(editor, search_query, results, target_field)
    dialog.exec()
