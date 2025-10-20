"""
应用程序样式表

提供现代化的UI样式，支持亮色和暗色主题。
"""

# 亮色主题样式
LIGHT_THEME = """
/* 全局样式 */
QWidget {
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

/* 主窗口 */
QMainWindow {
    background-color: #f5f5f5;
}

/* 工具栏 */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    spacing: 8px;
    padding: 8px;
}

QToolBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 8px 16px;
    margin: 2px;
    color: #333333;
    font-size: 13px;
}

QToolBar QToolButton:hover {
    background-color: #f0f0f0;
    border: 1px solid #d0d0d0;
}

QToolBar QToolButton:pressed {
    background-color: #e0e0e0;
}

QToolBar QToolButton:disabled {
    color: #999999;
    background-color: transparent;
}

QToolBar::separator {
    background-color: #e0e0e0;
    width: 1px;
    margin: 8px 4px;
}

/* 状态栏 */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e0e0e0;
    padding: 4px;
}

QStatusBar QLabel {
    padding: 2px 8px;
    color: #666666;
}

/* 进度条 */
QProgressBar {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: #f0f0f0;
    text-align: center;
    height: 20px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 #4CAF50, stop:1 #66BB6A);
    border-radius: 3px;
}

/* 分割器 */
QSplitter::handle {
    background-color: #e0e0e0;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #2196F3;
}

/* 文本编辑器 */
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
}

QTextEdit:focus {
    border: 1px solid #2196F3;
}

/* 列表 */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}

QListWidget:focus {
    border: 1px solid #2196F3;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px;
}

QListWidget::item:hover {
    background-color: #f5f5f5;
}

QListWidget::item:selected {
    background-color: #E3F2FD;
    color: #1976D2;
}

QListWidget::item:alternate {
    background-color: #fafafa;
}

/* 表格 */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    gridline-color: #e0e0e0;
    outline: none;
}

QTableWidget:focus {
    border: 1px solid #2196F3;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:hover {
    background-color: #f5f5f5;
}

QTableWidget::item:selected {
    background-color: #E3F2FD;
    color: #1976D2;
}

QTableWidget::item:alternate {
    background-color: #fafafa;
}

QHeaderView::section {
    background-color: #f5f5f5;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #2196F3;
    border-right: 1px solid #e0e0e0;
    font-weight: bold;
    color: #333333;
}

QHeaderView::section:hover {
    background-color: #eeeeee;
}

/* 按钮 */
QPushButton {
    background-color: #2196F3;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #BDBDBD;
    color: #757575;
}

/* 次要按钮 */
QPushButton[class="secondary"] {
    background-color: #ffffff;
    color: #2196F3;
    border: 1px solid #2196F3;
}

QPushButton[class="secondary"]:hover {
    background-color: #E3F2FD;
}

/* 危险按钮 */
QPushButton[class="danger"] {
    background-color: #f44336;
}

QPushButton[class="danger"]:hover {
    background-color: #d32f2f;
}

/* 输入框 */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #2196F3;
}

QLineEdit:disabled {
    background-color: #f5f5f5;
    color: #999999;
}

/* 下拉框 */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
}

QComboBox:focus {
    border: 1px solid #2196F3;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #666666;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    selection-background-color: #E3F2FD;
    selection-color: #1976D2;
    outline: none;
}

/* 数字输入框 */
QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 8px 12px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #2196F3;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background-color: #f5f5f5;
    border: 1px solid #d0d0d0;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
    color: #666666;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #2196F3;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #eeeeee;
}

/* 对话框 */
QDialog {
    background-color: #f5f5f5;
}

/* 消息框 */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #333333;
    padding: 10px;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 工具提示 */
QToolTip {
    background-color: #333333;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

/* 标题标签 */
QLabel[class="title"] {
    font-size: 16px;
    font-weight: bold;
    color: #1976D2;
    padding: 8px;
}

QLabel[class="subtitle"] {
    font-size: 14px;
    font-weight: bold;
    color: #333333;
    padding: 5px;
}

QLabel[class="info"] {
    color: #666666;
    padding: 2px 5px;
}
"""

# 暗色主题样式
DARK_THEME = """
/* 全局样式 */
QWidget {
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", Arial, sans-serif;
    font-size: 13px;
    color: #e0e0e0;
}

/* 主窗口 */
QMainWindow {
    background-color: #1e1e1e;
}

/* 工具栏 */
QToolBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3d3d3d;
    spacing: 8px;
    padding: 8px;
}

QToolBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 8px 16px;
    margin: 2px;
    color: #e0e0e0;
    font-size: 13px;
}

QToolBar QToolButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
}

QToolBar QToolButton:pressed {
    background-color: #4d4d4d;
}

QToolBar QToolButton:disabled {
    color: #666666;
    background-color: transparent;
}

QToolBar::separator {
    background-color: #3d3d3d;
    width: 1px;
    margin: 8px 4px;
}

/* 状态栏 */
QStatusBar {
    background-color: #2d2d2d;
    border-top: 1px solid #3d3d3d;
    padding: 4px;
}

QStatusBar QLabel {
    padding: 2px 8px;
    color: #b0b0b0;
}

/* 进度条 */
QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    background-color: #2d2d2d;
    text-align: center;
    height: 20px;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 #4CAF50, stop:1 #66BB6A);
    border-radius: 3px;
}

/* 分割器 */
QSplitter::handle {
    background-color: #3d3d3d;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #2196F3;
}

/* 文本编辑器 */
QTextEdit {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px;
    color: #e0e0e0;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
}

QTextEdit:focus {
    border: 1px solid #2196F3;
}

/* 列表 */
QListWidget {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    color: #e0e0e0;
}

QListWidget:focus {
    border: 1px solid #2196F3;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px;
}

QListWidget::item:hover {
    background-color: #3d3d3d;
}

QListWidget::item:selected {
    background-color: #1565C0;
    color: #ffffff;
}

QListWidget::item:alternate {
    background-color: #252525;
}

/* 表格 */
QTableWidget {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    gridline-color: #3d3d3d;
    outline: none;
    color: #e0e0e0;
}

QTableWidget:focus {
    border: 1px solid #2196F3;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:hover {
    background-color: #3d3d3d;
}

QTableWidget::item:selected {
    background-color: #1565C0;
    color: #ffffff;
}

QTableWidget::item:alternate {
    background-color: #252525;
}

QHeaderView::section {
    background-color: #3d3d3d;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #2196F3;
    border-right: 1px solid #4d4d4d;
    font-weight: bold;
    color: #e0e0e0;
}

QHeaderView::section:hover {
    background-color: #4d4d4d;
}

/* 按钮 */
QPushButton {
    background-color: #2196F3;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1976D2;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #4d4d4d;
    color: #666666;
}

/* 次要按钮 */
QPushButton[class="secondary"] {
    background-color: transparent;
    color: #2196F3;
    border: 1px solid #2196F3;
}

QPushButton[class="secondary"]:hover {
    background-color: #1565C0;
    color: #ffffff;
}

/* 危险按钮 */
QPushButton[class="danger"] {
    background-color: #f44336;
}

QPushButton[class="danger"]:hover {
    background-color: #d32f2f;
}

/* 输入框 */
QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e0e0e0;
    selection-background-color: #2196F3;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #2196F3;
}

QLineEdit:disabled {
    background-color: #252525;
    color: #666666;
}

/* 下拉框 */
QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
    color: #e0e0e0;
}

QComboBox:focus {
    border: 1px solid #2196F3;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #b0b0b0;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    selection-background-color: #1565C0;
    selection-color: #ffffff;
    outline: none;
    color: #e0e0e0;
}

/* 数字输入框 */
QSpinBox, QDoubleSpinBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e0e0e0;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #2196F3;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    background-color: #2d2d2d;
    top: -1px;
}

QTabBar::tab {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
    color: #b0b0b0;
}

QTabBar::tab:selected {
    background-color: #2d2d2d;
    color: #2196F3;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #4d4d4d;
}

/* 对话框 */
QDialog {
    background-color: #1e1e1e;
}

/* 消息框 */
QMessageBox {
    background-color: #2d2d2d;
}

QMessageBox QLabel {
    color: #e0e0e0;
    padding: 10px;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #5d5d5d;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7d7d7d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #5d5d5d;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #7d7d7d;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 工具提示 */
QToolTip {
    background-color: #4d4d4d;
    color: #ffffff;
    border: 1px solid #5d5d5d;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

/* 标题标签 */
QLabel[class="title"] {
    font-size: 16px;
    font-weight: bold;
    color: #2196F3;
    padding: 8px;
}

QLabel[class="subtitle"] {
    font-size: 14px;
    font-weight: bold;
    color: #e0e0e0;
    padding: 5px;
}

QLabel[class="info"] {
    color: #b0b0b0;
    padding: 2px 5px;
}
"""


def get_theme_stylesheet(theme: str = "light") -> str:
    """获取主题样式表
    
    Args:
        theme: 主题名称 ("light", "dark", "auto")
        
    Returns:
        样式表字符串
    """
    if theme == "dark":
        return DARK_THEME
    elif theme == "auto":
        # 自动检测系统主题（简化版，实际可以通过系统API检测）
        import platform
        if platform.system() == "Darwin":  # macOS
            try:
                import subprocess
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True,
                    text=True
                )
                if "Dark" in result.stdout:
                    return DARK_THEME
            except:
                pass
        return LIGHT_THEME
    else:
        return LIGHT_THEME
