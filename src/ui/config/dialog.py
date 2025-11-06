# ui/config/dialog.py - Configuration Dialog

from aqt import mw
from aqt.qt import QDialog, QDialogButtonBox, QTabWidget, QVBoxLayout

from ...config.types import AppConfig
from ...state import get_app_state
from ...translator import _
from .general import GeneralSettings
from .templates import TemplateSettings


class ConfigDialog(QDialog):
    """Main configuration dialog"""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent or mw)
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(_("图片搜索设置"))
        self.resize(600, 500)

        layout = QVBoxLayout()

        # Tabbed interface
        self.tabs = QTabWidget()

        # General settings tab
        self.general_widget = GeneralSettings(self.config)
        self.tabs.addTab(self.general_widget, _("基本设置"))

        # Template settings tab
        self.template_widget = TemplateSettings(self.config)
        self.tabs.addTab(self.template_widget, _("模板配置"))

        layout.addWidget(self.tabs)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def accept(self):
        """Save configuration on accept"""
        # Get config from both tabs
        general_config = self.general_widget.get_config()
        template_config = self.template_widget.get_config()

        # Merge configurations
        new_config = general_config
        new_config = template_config  # This will preserve note_type_templates

        # Save to app state
        app_state = get_app_state()
        app_state.update_and_save_config(new_config)

        # Check if language changed
        if new_config.language != self.config.language:
            from ...translator import reload_translator

            reload_translator()

        super().accept()
