# ui/browser_picker.py - Browser-based Image Picker Dialog

from aqt.qt import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWebEngineView,
    Qt,
)
from aqt.utils import showWarning, tooltip

from ..config.constants import GOOGLE_IMAGE_SEARCH_URL
from ..image_search import insert_image_to_field, save_image_to_media
from ..translator import _


class BrowserImagePickerDialog(QDialog):
    """Dialog with embedded browser for Google Images search"""

    def __init__(self, editor, search_query: str, target_field: str):
        super().__init__()
        print("[BrowserPicker] 初始化对话框")
        print(f"[BrowserPicker] 搜索词: {search_query}")
        print(f"[BrowserPicker] 目标字段: {target_field}")

        self.editor = editor
        self.search_query = search_query
        self.target_field = target_field
        self.selected_image_url = None
        self.init_ui()

    def init_ui(self):
        print("[BrowserPicker] 开始初始化UI")
        self.setWindowTitle(_("搜索图片 - {}").format(self.search_query))
        self.resize(1000, 700)

        layout = QVBoxLayout()

        # Instructions label
        from aqt.qt import QLabel

        instructions = QLabel(_("在下方浏览器中浏览图片，右键点击图片选择「插入图片」"))
        layout.addWidget(instructions)

        # Browser view
        print("[BrowserPicker] 创建QWebEngineView")
        self.browser = QWebEngineView()

        # Build Google Images URL
        import urllib.parse

        params = {
            "q": self.search_query,
            "udm": "2",  # Image search mode
        }
        url = f"{GOOGLE_IMAGE_SEARCH_URL}?{urllib.parse.urlencode(params)}"
        print(f"[BrowserPicker] Google Images URL: {url}")

        from aqt.qt import QUrl

        self.browser.setUrl(QUrl(url))
        print("[BrowserPicker] 已设置浏览器URL")

        # Enable custom context menu
        self.setup_context_menu()

        layout.addWidget(self.browser)

        # Bottom buttons
        button_layout = QHBoxLayout()

        self.insert_button = QPushButton(_("插入选中的图片"))
        self.insert_button.clicked.connect(self.on_insert_clicked)
        self.insert_button.setEnabled(False)
        self.insert_button.setToolTip(_("右键点击图片后，点击此按钮插入"))

        refresh_button = QPushButton(_("刷新"))
        refresh_button.clicked.connect(lambda: self.browser.reload())

        close_button = QPushButton(_("关闭"))
        close_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def setup_context_menu(self):
        """Setup JavaScript to handle image clicks"""
        print("[BrowserPicker] 设置上下文菜单")

        # Disable default context menu and use custom one
        self.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.on_custom_context_menu_requested)
        print("[BrowserPicker] 已禁用默认右键菜单，启用自定义菜单")

        # Connect multiple signals to debug page loading
        self.browser.loadStarted.connect(self.on_load_started)
        self.browser.loadProgress.connect(self.on_load_progress)
        self.browser.loadFinished.connect(self.inject_javascript)

        print("[BrowserPicker] 已连接页面加载信号")

    def on_load_started(self):
        """Called when page starts loading"""
        print("[BrowserPicker] ⏳ 页面开始加载")

    def on_load_progress(self, progress):
        """Called during page loading"""
        print(f"[BrowserPicker] ⏳ 页面加载进度: {progress}%")

    def on_custom_context_menu_requested(self, position):
        """Handle custom context menu request"""
        print(f"[BrowserPicker] 自定义右键菜单请求，位置: {position}")

        # Check if an image was selected via JavaScript
        js_code = """
        (function() {
            if (window.selectedImageUrl) {
                console.log('[AnkiImageSearch] 检测到选中的图片');
                return {
                    url: window.selectedImageUrl,
                    alt: window.selectedImageAlt || '',
                    hasSelection: true
                };
            }
            console.log('[AnkiImageSearch] 未检测到选中的图片');
            return {hasSelection: false};
        })();
        """

        self.browser.page().runJavaScript(
            js_code, lambda result: self.show_context_menu_at_position(position, result)
        )

    def show_context_menu_at_position(self, position, result):
        """Show context menu at the specified position"""
        print(f"[BrowserPicker] 在位置 {position} 显示上下文菜单，结果: {result}")
        from aqt.qt import QAction, QMenu

        menu = QMenu(self)

        if result and result.get("hasSelection"):
            # Image was selected
            self.selected_image_url = result.get("url")
            image_alt = result.get("alt", _("图片"))[:30]
            print(f"[BrowserPicker] 图片已选中: {self.selected_image_url}")
            print(f"[BrowserPicker] 图片描述: {image_alt}")

            insert_action = QAction(_("插入图片: {}").format(image_alt), self)
            insert_action.triggered.connect(self.on_insert_from_context_menu)
            menu.addAction(insert_action)

            menu.addSeparator()

            copy_action = QAction(_("复制图片URL"), self)
            copy_action.triggered.connect(
                lambda: self.copy_to_clipboard(self.selected_image_url)
            )
            menu.addAction(copy_action)

            # Enable the insert button
            self.insert_button.setEnabled(True)
            self.insert_button.setText(_("插入图片: {}").format(image_alt))
        else:
            # No image selected, show browser actions
            print("[BrowserPicker] 未选中图片，显示浏览器操作菜单")
            back_action = QAction(_("后退"), self)
            back_action.triggered.connect(self.browser.back)
            menu.addAction(back_action)

            forward_action = QAction(_("前进"), self)
            forward_action.triggered.connect(self.browser.forward)
            menu.addAction(forward_action)

            reload_action = QAction(_("刷新"), self)
            reload_action.triggered.connect(self.browser.reload)
            menu.addAction(reload_action)

        # Show menu at the cursor position in browser widget
        menu.exec(self.browser.mapToGlobal(position))

    def inject_javascript(self, success):
        """Inject JavaScript to handle image clicks"""
        print(f"[BrowserPicker] 页面加载完成，成功: {success}")
        if not success:
            print("[BrowserPicker] 页面加载失败，跳过JavaScript注入")
            return

        print("[BrowserPicker] 开始注入JavaScript")
        js_code = """
        (function() {
            console.log('[AnkiImageSearch] JavaScript 注入成功');

            // Add click listener to all images
            document.addEventListener('click', function(e) {
                if (e.target.tagName === 'IMG') {
                    // Store clicked image info
                    window.selectedImageUrl = e.target.src;
                    window.selectedImageAlt = e.target.alt || 'Image';

                    // Highlight the selected image
                    document.querySelectorAll('img').forEach(img => {
                        img.style.outline = '';
                    });
                    e.target.style.outline = '3px solid #0066cc';

                    // Notify that an image was selected
                    console.log('[AnkiImageSearch] 图片已选中:', window.selectedImageUrl);
                }
            });

            // Add right-click listener
            document.addEventListener('contextmenu', function(e) {
                if (e.target.tagName === 'IMG') {
                    window.selectedImageUrl = e.target.src;
                    window.selectedImageAlt = e.target.alt || 'Image';
                    console.log('[AnkiImageSearch] 图片被右键:', window.selectedImageUrl);
                }
            });
        })();
        """

        self.browser.page().runJavaScript(js_code)
        print("[BrowserPicker] JavaScript注入完成")

        # Poll for selected image
        self.check_selection_timer = None

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        from aqt.qt import QApplication

        QApplication.clipboard().setText(text)
        tooltip(_("已复制URL"))

    def on_insert_from_context_menu(self):
        """Insert image from context menu"""
        self.on_insert_clicked()

    def on_insert_clicked(self):
        """Download and insert the selected image"""
        print("[BrowserPicker] 开始插入图片")
        if not self.selected_image_url:
            print("[BrowserPicker] 错误：未选择图片")
            showWarning(_("请先右键点击一张图片"))
            return

        print(f"[BrowserPicker] 选中的图片URL: {self.selected_image_url}")

        # Show progress
        tooltip(_("正在下载图片..."))

        try:
            # Download image
            from ..image_search import GoogleImageSearch

            print("[BrowserPicker] 开始下载图片...")
            searcher = GoogleImageSearch()
            image_data = searcher.download_image(self.selected_image_url)

            if not image_data:
                print("[BrowserPicker] 下载失败：未获取到图片数据")
                showWarning(_("下载图片失败"))
                return

            print(f"[BrowserPicker] 下载成功，大小: {len(image_data)} 字节")

            # Save to media folder
            print("[BrowserPicker] 保存到媒体文件夹...")
            filename = save_image_to_media(
                image_data, self.selected_image_url, self.editor.note
            )

            if not filename:
                print("[BrowserPicker] 保存失败：未获取到文件名")
                showWarning(_("保存图片失败"))
                return

            print(f"[BrowserPicker] 保存成功，文件名: {filename}")

            # Insert into field
            print(f"[BrowserPicker] 插入到字段: {self.target_field}")
            success = insert_image_to_field(self.editor, self.target_field, filename)

            if success:
                print("[BrowserPicker] 插入成功")
                tooltip(_("图片已插入到 {}").format(self.target_field))
                self.accept()
            else:
                print("[BrowserPicker] 插入失败")
                showWarning(_("插入图片失败"))

        except Exception as e:
            print(f"[BrowserPicker] 异常: {str(e)}")
            import traceback
            traceback.print_exc()
            showWarning(_("错误: {}").format(str(e)))


def show_browser_image_picker(editor, search_query: str, target_field: str):
    """Show browser-based image picker dialog"""
    print("[BrowserPicker] show_browser_image_picker 被调用")
    print(f"[BrowserPicker] 参数 - 搜索词: {search_query}, 目标字段: {target_field}")
    dialog = BrowserImagePickerDialog(editor, search_query, target_field)
    print("[BrowserPicker] 显示对话框")

    # 使用show()而不是exec()，避免阻塞事件循环
    # 这样页面加载信号才能正常触发
    dialog.show()

    # 可选：设置为模态对话框（阻止用户操作其他窗口，但不阻塞事件循环）
    dialog.setModal(True)

    print("[BrowserPicker] 对话框已显示（非阻塞模式）")
