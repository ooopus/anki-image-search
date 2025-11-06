# ui/config/general.py - General Settings Widget

from dataclasses import replace

from aqt.qt import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    Qt,
)

from ...config.enums import ImageFormat, ImageQuality
from ...config.languages import LanguageCode
from ...config.types import AppConfig
from ...translator import _


class GeneralSettings(QWidget):
    """General settings widget"""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # General group
        general_group = QGroupBox(_("基本设置"))
        general_layout = QFormLayout()

        # Enabled checkbox
        self.enabled_checkbox = QCheckBox(_("启用插件"))
        self.enabled_checkbox.setChecked(self.config.enabled)
        general_layout.addRow(_("状态:"), self.enabled_checkbox)

        # Language selector
        self.language_combo = QComboBox()
        language_options = {
            LanguageCode.AUTO: _("自动检测"),
            LanguageCode.EN_US: _("English"),
            LanguageCode.ZH_CN: _("简体中文"),
        }
        for lang_code, lang_name in language_options.items():
            self.language_combo.addItem(lang_name, lang_code)

        # Set current language
        current_index = self.language_combo.findData(self.config.language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)

        general_layout.addRow(_("语言:"), self.language_combo)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # Search settings group
        search_group = QGroupBox(_("搜索设置"))
        search_layout = QFormLayout()

        # Max results
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(5, 50)
        self.max_results_spin.setValue(self.config.max_results)
        search_layout.addRow(_("最大结果数:"), self.max_results_spin)

        # Image quality
        self.quality_combo = QComboBox()
        quality_options = {
            ImageQuality.LOW: _("低 (快速)"),
            ImageQuality.MEDIUM: _("中等"),
            ImageQuality.HIGH: _("高 (慢速)"),
        }
        for quality, label in quality_options.items():
            self.quality_combo.addItem(label, quality)

        # Set current quality
        current_quality_index = self.quality_combo.findData(self.config.image_quality)
        if current_quality_index >= 0:
            self.quality_combo.setCurrentIndex(current_quality_index)

        search_layout.addRow(_("图片质量:"), self.quality_combo)

        # Auto download
        self.auto_download_checkbox = QCheckBox(_("自动下载并插入"))
        self.auto_download_checkbox.setChecked(self.config.auto_download)
        search_layout.addRow(_("下载方式:"), self.auto_download_checkbox)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Format conversion group
        format_group = QGroupBox(_("格式转换 (需要 FFmpeg)"))
        format_layout = QFormLayout()

        # Enable format conversion
        self.convert_format_checkbox = QCheckBox(_("启用格式转换"))
        self.convert_format_checkbox.setChecked(self.config.convert_format)
        self.convert_format_checkbox.toggled.connect(self.on_convert_format_toggled)
        format_layout.addRow(_("转换:"), self.convert_format_checkbox)

        # Output format selector
        self.output_format_combo = QComboBox()
        format_options = {
            ImageFormat.ORIGINAL: _("保持原格式"),
            ImageFormat.WEBP: _("WebP (推荐)"),
            ImageFormat.PNG: _("PNG (无损)"),
            ImageFormat.JPG: _("JPG/JPEG (有损)"),
        }
        for fmt, label in format_options.items():
            self.output_format_combo.addItem(label, fmt)

        # Set current format
        current_format_index = self.output_format_combo.findData(
            self.config.output_format
        )
        if current_format_index >= 0:
            self.output_format_combo.setCurrentIndex(current_format_index)

        format_layout.addRow(_("输出格式:"), self.output_format_combo)

        # Quality slider
        quality_container = QWidget()
        quality_layout = QVBoxLayout()
        quality_layout.setContentsMargins(0, 0, 0, 0)

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(50, 100)
        self.quality_slider.setValue(self.config.ffmpeg_quality)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(10)
        self.quality_slider.valueChanged.connect(self.on_quality_changed)

        self.quality_label = QLabel(f"{self.config.ffmpeg_quality}%")
        self.quality_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_label)
        quality_container.setLayout(quality_layout)

        format_layout.addRow(_("转换质量:"), quality_container)

        # FFmpeg status
        from ...ffmpeg_utils import check_ffmpeg

        ffmpeg_available, ffmpeg_msg = check_ffmpeg()
        status_color = "green" if ffmpeg_available else "red"
        status_icon = "✓" if ffmpeg_available else "✗"
        self.ffmpeg_status_label = QLabel(f'<span style="color:{status_color}">{status_icon} {ffmpeg_msg}</span>')
        format_layout.addRow(_("FFmpeg 状态:"), self.ffmpeg_status_label)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Update enabled state
        self.on_convert_format_toggled(self.config.convert_format)

        layout.addStretch()
        self.setLayout(layout)

    def on_convert_format_toggled(self, checked: bool):
        """Handle format conversion checkbox toggle"""
        self.output_format_combo.setEnabled(checked)
        self.quality_slider.setEnabled(checked)
        self.quality_label.setEnabled(checked)

    def on_quality_changed(self, value: int):
        """Update quality label when slider changes"""
        self.quality_label.setText(f"{value}%")

    def get_config(self) -> AppConfig:
        """Get configuration from UI"""
        return replace(
            self.config,
            enabled=self.enabled_checkbox.isChecked(),
            language=self.language_combo.currentData(),
            max_results=self.max_results_spin.value(),
            image_quality=self.quality_combo.currentData(),
            auto_download=self.auto_download_checkbox.isChecked(),
            convert_format=self.convert_format_checkbox.isChecked(),
            output_format=self.output_format_combo.currentData(),
            ffmpeg_quality=self.quality_slider.value(),
        )
