import sys
import argparse

from bimtester.guiplus import optionwidget
from bimtester.guiplus import browsertabwidget
from bimtester.guiplus import findtoolbar
from bimtester.guiplus import webengineview

from PySide2 import QtCore
from PySide2.QtCore import Qt, QUrl
from PySide2.QtGui import QKeySequence, QIcon
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QDockWidget,
    QLabel,
    QLineEdit,
    QMainWindow,
    QToolBar,
    QMessageBox,
    QTabWidget,
)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

from bimtester.guiplus.optionwidget import OptionWidget
from bimtester.guiplus.browsertabwidget import BrowserTabWidget
from bimtester.guiplus.findtoolbar import FindToolBar
from bimtester.guiplus.webengineview import WebEngineView

from bimtester.guiplus.bimtesterwrapper import get_resource_path

# from hanging_threads import start_monitoring
# start_monitoring(seconds_frozen=10, test_interval=100)

main_windows = []


def create_main_window(initial_path="", default_zoom=1):
    """Creates a MainWindow using 75% of the available screen resolution."""
    main_win = MainWindow(initial_path, default_zoom)
    main_windows.append(main_win)
    available_geometry = app.desktop().availableGeometry(main_win)
    main_win.resize(available_geometry.width() * 2 / 3, available_geometry.height() * 2 / 3)
    main_win.show()
    return main_win


def create_main_window_with_browser(initial_path="", default_zoom=1):
    """Creates a MainWindow with a BrowserTabWidget."""
    main_win = create_main_window(initial_path, default_zoom)
    # main_win.add_browser_tab()
    return main_win


class MainWindow(QMainWindow):
    """Provides the parent window that includes the BookmarkWidget,
    BrowserTabWidget, and a DownloadWidget, to offer the complete
    web browsing experience."""

    def __init__(self, initial_path="", default_zoom=1):
        super(MainWindow, self).__init__()

        self.icon = QIcon(get_resource_path("resources/icons/bimtester.ico"))

        self.setWindowTitle("BIMTester GUI+")
        self.setWindowIcon(self.icon)

        self._tab_widget = BrowserTabWidget(create_main_window_with_browser)

        self.setCentralWidget(self._tab_widget)

        self._option_dock = QDockWidget()
        self._option_dock.setWindowTitle("Options")
        self._option_widget = OptionWidget(initial_path, default_zoom)
        self._option_widget.open_report.connect(self.load_url)
        self._option_widget.open_report_in_new_tab.connect(self.load_url_in_new_tab)
        self._option_widget.set_default_zoom.connect(self.set_default_zoom)
        self._option_widget.show_error.connect(self.show_error)
        self._option_dock.setWidget(self._option_widget)
        self.addDockWidget(Qt.TopDockWidgetArea, self._option_dock)

        self._find_tool_bar = None

        self._actions = {}
        self._create_menu()

        self._zoom_label = QLabel()
        self.statusBar().addPermanentWidget(self._zoom_label)
        self._update_zoom_label()

        # if tab is not added from start, adding the first tab freezes the application sometimes
        self.load_url_in_new_tab(QUrl.fromLocalFile(get_resource_path("guiplus/resources/welcome.html")), default_zoom)

    def _create_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        exit_action = QAction(
            QIcon.fromTheme("application-exit"), "E&xit", self, shortcut="Ctrl+Q", triggered=qApp.quit
        )
        file_menu.addAction(exit_action)

        window_menu = self.menuBar().addMenu("&Window")

        find_action = QAction("Find", self, shortcut=QKeySequence(QKeySequence.Find), triggered=self._show_find)
        window_menu.addAction(find_action)
        window_menu.addSeparator()

        window_menu.addAction(self._option_dock.toggleViewAction())
        window_menu.addSeparator()

        zoom_in_action = QAction(
            QIcon.fromTheme("zoom-in"),
            "Zoom In",
            self,
            shortcut=QKeySequence(QKeySequence.ZoomIn),
            triggered=self._zoom_in,
        )
        window_menu.addAction(zoom_in_action)
        zoom_out_action = QAction(
            QIcon.fromTheme("zoom-out"),
            "Zoom Out",
            self,
            shortcut=QKeySequence(QKeySequence.ZoomOut),
            triggered=self._zoom_out,
        )
        window_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction(
            QIcon.fromTheme("zoom-original"), "Reset Zoom", self, shortcut="Ctrl+0", triggered=self._reset_zoom
        )
        window_menu.addAction(reset_zoom_action)

        about_menu = self.menuBar().addMenu("&About")
        about_action = QAction(
            "About BIMTester GUI+", self, shortcut=QKeySequence(QKeySequence.HelpContents), triggered=self.show_about
        )
        about_menu.addAction(about_action)

    def add_browser_tab(self):
        return self._tab_widget.add_browser_tab()

    def _close_current_tab(self):
        self._tab_widget.close_current_tab()

    def close_event(self, event):
        main_windows.remove(self)
        event.accept()

    def load_url_string(self, url_s):
        url = QUrl.fromUserInput(url_s)
        if url.isValid():
            self.load_url(url)

    def load_url(self, url):
        self._tab_widget.load(url)

    def load_url_in_new_tab(self, url, zoom=1):
        web_engine_view = self.add_browser_tab()
        web_engine_view.load(url)
        if zoom != 1 and zoom <= WebEngineView.maximum_zoom_factor():
            web_engine_view.setZoomFactor(zoom)
            self._update_zoom_label()

    def set_default_zoom(self, zoom):
        if zoom <= WebEngineView.maximum_zoom_factor():
            self._tab_widget.set_zoom_factor(zoom)
            self._update_zoom_label()

    def _zoom_in(self):
        new_zoom = self._tab_widget.zoom_factor() * 1.5
        if new_zoom <= WebEngineView.maximum_zoom_factor():
            self._tab_widget.set_zoom_factor(new_zoom)
            self._update_zoom_label()

    def _zoom_out(self):
        new_zoom = self._tab_widget.zoom_factor() / 1.5
        if new_zoom >= WebEngineView.minimum_zoom_factor():
            self._tab_widget.set_zoom_factor(new_zoom)
            self._update_zoom_label()

    def _reset_zoom(self):
        self._tab_widget.set_zoom_factor(1)
        self._update_zoom_label()

    def _update_zoom_label(self):
        percent = int(self._tab_widget.zoom_factor() * 100)
        self._zoom_label.setText("{}%".format(percent))

    def _show_find(self):
        if self._find_tool_bar is None:
            self._find_tool_bar = FindToolBar()
            self._find_tool_bar.find.connect(self._tab_widget.find)
            self.addToolBar(Qt.BottomToolBarArea, self._find_tool_bar)
        else:
            self._find_tool_bar.show()
        self._find_tool_bar.focus_find()

    def show_error(self, msg_error):
        msg = QMessageBox()
        msg.setWindowIcon(self.icon)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(msg_error)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def show_about(self):
        msg = QMessageBox()
        msg.setWindowIcon(self.icon)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About BIMTester GUI+")
        msg.setText("Contribution by Engisis for buildingSMART")
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec()


if __name__ == "__main__":

    if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    parser = argparse.ArgumentParser(description="Runs GUI for IFC test")
    parser.add_argument("-p", "--path", type=str, help=("Specify a path to a working directory"), default="")
    parser.add_argument("-z", "--zoom", type=float, help=("Specify a zoom factor when opening a tab"), default=1)
    args = vars(parser.parse_args())

    # start
    app = QApplication(sys.argv)
    main_win = create_main_window_with_browser(args["path"], args["zoom"])
    sys.exit(app.exec_())
