# ui/config/templates.py - Note Type Template Configuration Widget

from dataclasses import replace

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...config.types import AppConfig, NoteTypeTemplate
from ...translator import _


class TemplateDialog(QDialog):
    """Dialog for editing a single note type template"""

    def __init__(self, template: NoteTypeTemplate | None = None, parent=None):
        super().__init__(parent or mw)
        self.template = template or NoteTypeTemplate("", "", "")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(_("编辑模板"))
        self.resize(400, 250)

        layout = QFormLayout()

        # Note type selector
        self.note_type_combo = QComboBox()
        layout.addRow(_("笔记类型:"), self.note_type_combo)

        # Search field
        self.search_field_combo = QComboBox()
        layout.addRow(_("搜索字段:"), self.search_field_combo)

        # Target field
        self.target_field_combo = QComboBox()
        layout.addRow(_("目标字段:"), self.target_field_combo)

        # Load note types and connect signal AFTER creating all widgets
        self.load_note_types()
        self.note_type_combo.currentIndexChanged.connect(self.on_note_type_changed)

        # Set current note type if editing
        if self.template.note_type_name:
            index = self.note_type_combo.findText(self.template.note_type_name)
            if index >= 0:
                self.note_type_combo.setCurrentIndex(index)

        # Enabled checkbox
        self.enabled_checkbox = QCheckBox(_("启用此模板"))
        self.enabled_checkbox.setChecked(self.template.enabled)
        layout.addRow(_("状态:"), self.enabled_checkbox)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        # Load fields for the selected note type
        self.load_fields()

    def load_note_types(self):
        """Load all note types from Anki"""
        if not mw or not mw.col:
            return

        note_types = mw.col.models.all()
        for note_type in note_types:
            self.note_type_combo.addItem(note_type["name"])

    def on_note_type_changed(self):
        """Handle note type selection change"""
        self.load_fields()

    def load_fields(self):
        """Load fields for the selected note type"""
        self.search_field_combo.clear()
        self.target_field_combo.clear()

        if not mw or not mw.col:
            return

        note_type_name = self.note_type_combo.currentText()
        if not note_type_name:
            return

        # Get note type by name
        note_type = mw.col.models.by_name(note_type_name)
        if not note_type:
            return

        # Load field names
        field_names = [field["name"] for field in note_type["flds"]]
        for field_name in field_names:
            self.search_field_combo.addItem(field_name)
            self.target_field_combo.addItem(field_name)

        # Set current fields if editing
        if self.template.search_field:
            index = self.search_field_combo.findText(self.template.search_field)
            if index >= 0:
                self.search_field_combo.setCurrentIndex(index)

        if self.template.target_field:
            index = self.target_field_combo.findText(self.template.target_field)
            if index >= 0:
                self.target_field_combo.setCurrentIndex(index)

    def get_template(self) -> NoteTypeTemplate:
        """Get the edited template"""
        return NoteTypeTemplate(
            note_type_name=self.note_type_combo.currentText(),
            search_field=self.search_field_combo.currentText(),
            target_field=self.target_field_combo.currentText(),
            enabled=self.enabled_checkbox.isChecked(),
        )


class TemplateSettings(QWidget):
    """Widget for managing note type templates"""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Enable templates checkbox
        self.use_templates_checkbox = QCheckBox(
            _("使用笔记类型特定配置（否则使用默认配置）")
        )
        self.use_templates_checkbox.setChecked(self.config.use_note_type_templates)
        self.use_templates_checkbox.toggled.connect(self.on_use_templates_toggled)
        layout.addWidget(self.use_templates_checkbox)

        # Template list group
        template_group = QGroupBox(_("笔记类型模板"))
        template_layout = QVBoxLayout()

        # Template list
        self.template_list = QListWidget()
        self.template_list.setAlternatingRowColors(True)
        self.load_templates()
        template_layout.addWidget(self.template_list)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton(_("添加模板"))
        self.add_button.clicked.connect(self.on_add_template)

        self.edit_button = QPushButton(_("编辑"))
        self.edit_button.clicked.connect(self.on_edit_template)

        self.delete_button = QPushButton(_("删除"))
        self.delete_button.clicked.connect(self.on_delete_template)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        template_layout.addLayout(button_layout)
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        # Info label
        info_label = QLabel(
            _(
                "提示: 为不同的笔记类型配置不同的字段映射。\n"
                "插件会自动根据当前笔记类型选择对应配置。"
            )
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { color: #666; font-size: 11px; }")
        layout.addWidget(info_label)

        # Update button states
        self.on_use_templates_toggled(self.config.use_note_type_templates)

        layout.addStretch()
        self.setLayout(layout)

    def load_templates(self):
        """Load templates into list widget"""
        self.template_list.clear()
        for template in self.config.note_type_templates:
            status = "✓" if template.enabled else "✗"
            item_text = (
                f"{status} {template.note_type_name}: "
                f"{template.search_field} → {template.target_field}"
            )
            item = QListWidgetItem(item_text)
            item.setData(1, template)  # Store template in item
            self.template_list.addItem(item)

    def on_use_templates_toggled(self, checked: bool):
        """Handle use templates checkbox toggle"""
        self.template_list.setEnabled(checked)
        self.add_button.setEnabled(checked)
        self.edit_button.setEnabled(checked)
        self.delete_button.setEnabled(checked)

    def on_add_template(self):
        """Add new template"""
        dialog = TemplateDialog(None, self)
        if dialog.exec():
            new_template = dialog.get_template()
            self.config.note_type_templates.append(new_template)
            self.load_templates()

    def on_edit_template(self):
        """Edit selected template"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return

        template = current_item.data(1)
        dialog = TemplateDialog(template, self)
        if dialog.exec():
            edited_template = dialog.get_template()

            # Update template in config
            index = self.config.note_type_templates.index(template)
            self.config.note_type_templates[index] = edited_template
            self.load_templates()

    def on_delete_template(self):
        """Delete selected template"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return

        template = current_item.data(1)
        self.config.note_type_templates.remove(template)
        self.load_templates()

    def get_config(self) -> AppConfig:
        """Get configuration from UI"""
        return replace(
            self.config,
            use_note_type_templates=self.use_templates_checkbox.isChecked(),
            # note_type_templates is already updated in-place
        )
