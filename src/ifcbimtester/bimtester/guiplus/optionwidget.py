import os
import shutil

from .bimtesterwrapper import BIMTesterWrapper
from .bimtesterwrapper import get_resource_path

from PySide2 import QtCore
from PySide2.QtCore import QDir, QFileInfo, QStandardPaths, Qt, QUrl, QSize
from PySide2.QtGui import QIcon, QKeySequence, QPixmap
from PySide2.QtWidgets import (
    QMenu,
    QMessageBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QToolButton,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QCheckBox,
)

DEFAULT_IFC_FILE_PATH = "IFC files from implementers"
DEFAULT_FEATURES_PATH = "Features"
DEFAULT_REPORTS_PATH = "Validation reports"

# Option widget
class OptionWidget(QWidget):
    """Provides a layout to manage the BIMTester options."""

    open_report = QtCore.Signal(QUrl)
    open_report_in_new_tab = QtCore.Signal(QUrl, float)
    set_default_zoom = QtCore.Signal(float)
    show_error = QtCore.Signal(str)

    def __init__(self, initial_path="", default_zoom=1):
        super(OptionWidget, self).__init__()
        self.default_zoom = default_zoom
        self.initial_ifcfile = ""
        self.initial_schemafile = ""
        self.initial_featurefile = ""
        self.initial_reportpath = ""

        # path
        _path_label = QLabel("Working Path:", self)
        self.path_text = QLineEdit()
        _path_browse_btn = QToolButton()
        _path_browse_btn.setText("...")
        _path_browse_btn.clicked.connect(self.select_path)

        # ifc file
        _ifcfile_label = QLabel("IFC file:", self)
        self.ifcfile_text = QLineEdit()
        self.set_ifcfile(self.initial_ifcfile)
        _ifcfile_browse_btn = QToolButton()
        _ifcfile_browse_btn.setText("...")
        _ifcfile_browse_btn.clicked.connect(self.select_ifcfile)

        # schema file
        _schemafile_label = QLabel("IFC Schema file:", self)
        self.schemafile_text = QLineEdit()
        self.set_schemafile(self.initial_schemafile)
        _schemafile_browse_btn = QToolButton()
        _schemafile_browse_btn.setText("...")
        _schemafile_browse_btn.clicked.connect(self.select_schemafile)

        # path browser and line edit
        _ffdir_str = "Feature file:"
        _featurefile_label = QLabel(_ffdir_str, self)
        self.featurefile_text = QLineEdit()
        self.set_featurefile(self.initial_featurefile)
        _featurefile_browse_btn = QToolButton()
        _featurefile_browse_btn.setText("...")
        _featurefile_browse_btn.clicked.connect(self.select_featurefile)

        # report path
        _reportpath_label = QLabel("Folder to write reports to:", self)
        self.reportpath_text = QLineEdit()
        self.set_reportpath(self.initial_reportpath)
        _reportpath_browse_btn = QToolButton()
        _reportpath_browse_btn.setText("...")
        _reportpath_browse_btn.clicked.connect(self.select_reportpath)

        # buttons
        self.cb_continue_failed = QCheckBox("Continue after failed step", self)
        self.cb_continue_failed.setChecked(True)

        pixmap = QPixmap(get_resource_path("guiplus/resources/run.png"))
        self.run_button = QPushButton("&Run")
        self.run_button.setIcon(QIcon(pixmap))
        self.run_button.setIconSize(pixmap.rect().size())

        self.run_button.setShortcut(QKeySequence("Alt+R"))
        self.run_button.clicked.connect(self.run_bimtester)

        _buttons = QHBoxLayout()
        _buttons.addStretch(1)
        _buttons.addWidget(self.cb_continue_failed)
        _buttons.addWidget(self.run_button)

        # Layout:
        layout = QGridLayout()

        layout.addWidget(_path_label, 0, 0)
        layout.addWidget(self.path_text, 0, 1)
        layout.addWidget(_path_browse_btn, 0, 2)

        layout.addWidget(_ifcfile_label, 2, 0)
        layout.addWidget(self.ifcfile_text, 2, 1)
        layout.addWidget(_ifcfile_browse_btn, 2, 2)

        layout.addWidget(_schemafile_label, 4, 0)
        layout.addWidget(self.schemafile_text, 4, 1)
        layout.addWidget(_schemafile_browse_btn, 4, 2)

        layout.addWidget(_featurefile_label, 6, 0)
        layout.addWidget(self.featurefile_text, 6, 1)
        layout.addWidget(_featurefile_browse_btn, 6, 2)

        layout.addWidget(_reportpath_label, 8, 0)
        layout.addWidget(self.reportpath_text, 8, 1)
        layout.addWidget(_reportpath_browse_btn, 8, 2)

        layout.addLayout(_buttons, 9, 0, 1, 2)
        # row stretches by 10 compared to the others, std is 0
        # first parameter is the row number
        # second is the stretch factor.
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # init
        if initial_path:
            self.set_path(initial_path)

    def run_bimtester(self):
        bimtester = BIMTesterWrapper()
        msg_error = ""
        if not self.get_path() and not self.get_ifcfile() and not self.get_featurefile() and not self.get_reportpath():
            msg_error = "Cannot run BIMTester without setting the options"
        elif not os.path.isfile(self.get_featurefile()) and not self.get_featurefile().endswith(".feature"):
            msg_error = "Cannot run BIMTester without a proper feature file"
        elif not os.path.isfile(self.get_ifcfile()) and not self.get_ifcfile().endswith(".ifc"):
            msg_error = "Cannot run BIMTester without a proper IFC file"

        if msg_error:
            self.show_error.emit(msg_error)
            return False

        report_file_urls = bimtester.run_bimtester(
            self.get_path(),
            self.get_ifcfile(),
            self.get_schemafile(),
            self.get_featurefile(),
            self.get_reportpath(),
            self.is_continue_after_failed_checked(),
        )
        if not report_file_urls:
            self.show_error.emit("No report could be found.")
            return False

        for report_file_url in report_file_urls:
            self.open_report_in_new_tab.emit(report_file_url, self.default_zoom)
            # self.set_default_zoom.emit(self.default_zoom)

        return True

    def select_path(self):
        path_dir = self.path_text.text()
        # hidden directories are only shown if the option is set
        path = QFileDialog.getExistingDirectory(
            self, caption="Choose directory ...", dir=path_dir, options=QFileDialog.HideNameFilterDetails
        )
        if path:
            self.set_path(path)

    def set_path(self, path):
        self.path_text.setText(path)
        if not self.get_ifcfile():
            self.set_ifcfile(os.path.join(path, DEFAULT_IFC_FILE_PATH))
        if not self.get_schemafile():
            self.set_schemafile(path)
        if not self.get_featurefile():
            self.set_featurefile(os.path.join(path, DEFAULT_FEATURES_PATH))
        if not self.get_reportpath():
            self.set_reportpath(os.path.join(path, DEFAULT_REPORTS_PATH))

    def get_path(self):
        return self.path_text.text()

    def select_ifcfile(self):
        ifcfile = QFileDialog.getOpenFileName(self, dir=self.get_ifcfile())[0]
        if ifcfile:
            self.set_ifcfile(ifcfile)

    def set_ifcfile(self, a_file):
        self.ifcfile_text.setText(a_file)

    def get_ifcfile(self):
        return self.ifcfile_text.text()

    def select_schemafile(self):
        schemafile = QFileDialog.getOpenFileName(self, dir=self.get_schemafile())[0]
        if schemafile:
            self.set_schemafile(schemafile)

    def set_schemafile(self, a_file):
        self.schemafile_text.setText(a_file)

    def get_schemafile(self):
        return self.schemafile_text.text()

    def select_featurefile(self):
        featurefile = QFileDialog.getOpenFileName(self, dir=self.get_featurefile())[0]
        if featurefile:
            self.set_featurefile(featurefile)

    def set_featurefile(self, file):
        self.featurefile_text.setText(file)

    def get_featurefile(self):
        return self.featurefile_text.text()

    def select_reportpath(self):
        reportpath_dir = self.reportpath_text.text()
        # hidden directories are only shown if the option is set
        path = QFileDialog.getExistingDirectory(
            self, caption="Choose directory ...", dir=reportpath_dir, options=QFileDialog.HideNameFilterDetails
        )
        if path:
            self.set_reportpath(path)

    def set_reportpath(self, a_path):
        self.reportpath_text.setText(a_path)

    def get_reportpath(self):
        return self.reportpath_text.text()

    def is_continue_after_failed_checked(self):
        return self.cb_continue_failed.isChecked()

    # Return a short title for a tab,
    # "Engisis | BIM Expert.." -> "Engisis"
    @staticmethod
    def short_title(t):
        i = t.find(" | ")
        if i == -1:
            i = t.find(" - ")
        return t[0:i] if i != -1 else t
