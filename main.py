#!/usr/bin/env python3
"""主程序入口"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.config_manager import AppConfig
from utils.log_manager import get_logger
from utils.exceptions import ConfigException
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog


class FirstRunWizard:
    """首次运行配置向导"""
    
    @staticmethod
    def show_welcome_dialog() -> bool:
        """显示欢迎对话框"""
        msg = QMessageBox()
        msg.setWindowTitle("欢迎使用 ExcellentCaseExpert")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("欢迎使用 ExcellentCaseExpert - AI 测试用例生成系统！")
        msg.setInformativeText(
            "这是您第一次运行本程序。\n\n"
            "在开始使用之前，需要配置 AI 模型的 API Key。\n\n"
            "是否现在进行配置？"
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        return msg.exec() == QMessageBox.StandardButton.Yes
    
    @staticmethod
    def show_config_dialog(config: AppConfig) -> bool:
        """显示配置对话框"""
        dialog = SettingsDialog(config)
        dialog.setWindowTitle("首次运行配置")
        
        # 显示提示信息
        from PyQt6.QtWidgets import QLabel
        info_label = QLabel(
            "请配置 AI 模型的 API Key 以使用 AI 分析功能。\n"
            "您可以稍后在设置中修改这些配置。"
        )
        info_label.setStyleSheet("color: #666; padding: 10px;")
        dialog.layout().insertWidget(0, info_label)
        
        return dialog.exec() == SettingsDialog.DialogCode.Accepted
    
    @staticmethod
    def is_first_run() -> bool:
        """检查是否首次运行"""
        config_file = Path("config.yaml")
        
        # 如果配置文件不存在，则是首次运行
        if not config_file.exists():
            return True
        
        # 如果配置文件存在但 API Key 是默认值，也视为首次运行
        try:
            config = AppConfig.load_from_file()
            if config.ai_model.api_key == "your_api_key_here":
                return True
        except Exception:
            return True
        
        return False


def setup_application() -> QApplication:
    """设置应用程序"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("ExcellentCaseExpert")
    app.setApplicationDisplayName("ExcellentCaseExpert - AI 测试用例生成系统")
    app.setOrganizationName("ExcellentCase")
    app.setOrganizationDomain("excellentcase.com")
    
    return app


def load_and_validate_config() -> AppConfig:
    """加载和验证配置"""
    try:
        # 加载配置
        config = AppConfig.load_from_file()
        
        # 验证配置
        if not config.ocr.use_paddle_ocr and not config.ocr.use_tesseract:
            raise ConfigException("至少需要启用一个 OCR 引擎")
        
        return config
        
    except Exception as e:
        raise ConfigException(f"配置加载失败: {str(e)}")


def initialize_logger():
    """初始化日志系统"""
    logger = get_logger()
    
    # 清理过期日志（30 天前）
    try:
        logger.cleanup_old_logs(days=30)
    except Exception as e:
        logger.warning(f"清理过期日志失败: {e}")
    
    logger.info("=" * 60)
    logger.info("ExcellentCaseExpert 启动")
    logger.info("=" * 60)
    logger.log_operation("application_start")
    
    return logger


def handle_first_run(config: AppConfig) -> bool:
    """处理首次运行"""
    # 显示欢迎对话框
    if not FirstRunWizard.show_welcome_dialog():
        # 用户选择稍后配置
        reply = QMessageBox.question(
            None,
            "跳过配置",
            "跳过配置将导致 AI 分析功能无法使用。\n\n"
            "您可以稍后在设置中进行配置。\n\n"
            "是否继续启动程序？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    # 显示配置对话框
    if not FirstRunWizard.show_config_dialog(config):
        # 用户取消配置
        reply = QMessageBox.question(
            None,
            "取消配置",
            "取消配置将导致 AI 分析功能无法使用。\n\n"
            "是否继续启动程序？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    return True


def main():
    """主函数"""
    logger = None
    
    try:
        # 初始化日志系统
        logger = initialize_logger()
        
        # 设置应用程序
        app = setup_application()
        
        logger.info("应用程序初始化完成")
        
        # 加载和验证配置
        try:
            config = load_and_validate_config()
            logger.info("配置加载成功")
        except ConfigException as e:
            logger.log_error(e, {"operation": "load_config"})
            QMessageBox.critical(
                None,
                "配置错误",
                f"配置加载失败：{str(e)}\n\n"
                "程序将使用默认配置创建新的配置文件。"
            )
            # 创建默认配置
            config = AppConfig.create_default()
            config.save_to_file()
            logger.info("已创建默认配置文件")
        
        # 检查是否首次运行
        if FirstRunWizard.is_first_run():
            logger.info("检测到首次运行，启动配置向导")
            
            if not handle_first_run(config):
                logger.info("用户取消首次运行配置，程序退出")
                return 0
            
            # 重新加载配置
            config = AppConfig.load_from_file()
            logger.info("首次运行配置完成")
        
        # 创建主窗口
        logger.info("创建主窗口")
        main_window = MainWindow()
        
        # 显示主窗口
        main_window.show()
        logger.info("主窗口显示完成")
        
        # 运行应用程序
        exit_code = app.exec()
        
        logger.log_operation("application_exit", exit_code=exit_code)
        logger.info("=" * 60)
        logger.info("ExcellentCaseExpert 正常退出")
        logger.info("=" * 60)
        
        return exit_code
        
    except Exception as e:
        # 捕获所有未处理的异常
        if logger:
            logger.log_error(e, {"operation": "main"})
        
        # 显示错误对话框
        QMessageBox.critical(
            None,
            "严重错误",
            f"程序发生严重错误：{str(e)}\n\n"
            "详细信息请查看日志文件：logs/error.log\n\n"
            "程序将退出。"
        )
        
        if logger:
            logger.info("=" * 60)
            logger.info("ExcellentCaseExpert 异常退出")
            logger.info("=" * 60)
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
