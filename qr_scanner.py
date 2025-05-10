import sys
import io
from PIL import Image, ImageGrab
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QVBoxLayout, QWidget, QMessageBox, QTextEdit, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QClipboard
from pyzbar.pyzbar import decode
import cv2
import numpy as np

class QRScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 存储初始窗口大小和位置
        self.initial_width = 300
        self.initial_height = 80
        self.initUI()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('二维码扫描器')
        self.setGeometry(100, 100, self.initial_width, self.initial_height)  # 使用更紧凑的初始窗口大小
        
        # 设置窗口始终在最前端
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        
        # 创建截屏按钮
        self.scan_button = QPushButton('截屏并扫描二维码', self)
        self.scan_button.clicked.connect(self.capture_and_scan)
        self.layout.addWidget(self.scan_button)
        
        # 创建清除结果按钮
        self.clear_button = QPushButton('清除结果', self)
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.hide()  # 初始隐藏清除按钮
        self.layout.addWidget(self.clear_button)
        
        # 创建结果显示区域
        self.result_container = QWidget()
        result_layout = QVBoxLayout(self.result_container)
        
        # 创建可复制的文本编辑框
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setAlignment(Qt.AlignCenter)
        self.result_text.setLineWrapMode(QTextEdit.WidgetWidth)
        self.result_text.setFixedHeight(60)  # 设置固定高度
        result_layout.addWidget(self.result_text)
        
        # 创建复制按钮的水平布局
        button_layout = QHBoxLayout()
        
        # 创建复制按钮
        self.copy_button = QPushButton('复制结果', self)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        # 添加水平布局到结果容器
        result_layout.addLayout(button_layout)
        
        # 初始隐藏结果区域
        self.result_container.hide()
        self.layout.addWidget(self.result_container)
        
        # 创建显示截图的标签
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.hide()  # 初始隐藏图像标签
        self.layout.addWidget(self.image_label)
        
        # 显示窗口
        self.show()
        
    def copy_to_clipboard(self):
        """将扫描结果复制到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_text.toPlainText())
        QMessageBox.information(self, "复制成功", "扫描结果已复制到剪贴板")

    def clear_results(self):
        """清除扫描结果并隐藏结果区域"""
        # 记录当前窗口位置
        current_x = self.x()
        current_y = self.y()
        
        # 清除内容并隐藏控件
        self.result_text.clear()
        self.result_container.hide()
        self.image_label.setPixmap(QPixmap())
        self.image_label.hide()
        self.clear_button.hide()
        
        # 设置隐藏控件的固定高度为0，强制布局收缩
        self.result_text.setFixedHeight(0)
        self.image_label.setFixedHeight(0)
        
        # 更新布局
        self.layout.update()
        
        # 设置窗口的最小和最大大小，强制窗口大小
        self.setMinimumSize(self.initial_width, self.initial_height)
        self.setMaximumSize(self.initial_width, self.initial_height)
        
        # 先调整大小
        self.resize(self.initial_width, self.initial_height)
        
        # 然后显式设置位置
        self.move(current_x, current_y)
        
        # 处理完成后，重置最小和最大大小限制，并保持位置
        QTimer.singleShot(100, lambda: self.reset_size_constraints(current_x, current_y))
        
    def reset_size_constraints(self, x=None, y=None):
        """重置窗口大小限制，允许窗口在下次显示结果时增大"""
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)  # Qt默认的最大尺寸
        
        # 重置控件的固定高度
        self.result_text.setFixedHeight(16777215)
        self.image_label.setFixedHeight(16777215)
        
        # 如果提供了位置参数，确保窗口位置不变
        if x is not None and y is not None:
            self.move(x, y)
    
    def capture_and_scan(self):
        """截屏并扫描二维码"""
        # 隐藏窗口以避免截取到自己
        self.hide()
        
        # 使用定时器延迟截屏，给用户时间切换到包含二维码的窗口
        QTimer.singleShot(1000, self.perform_capture)
    
    def perform_capture(self):
        """执行截屏和扫描操作"""
        try:
            # 截取全屏
            screenshot = ImageGrab.grab()
            
            # 将PIL图像转换为OpenCV格式
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # 解析二维码
            decoded_objects = decode(screenshot)
            
            # 重新显示窗口
            self.show()
            
            if decoded_objects:
                # 找到二维码
                qr_data = decoded_objects[0].data.decode('utf-8')
                self.result_text.setPlainText(f"扫描结果: {qr_data}")
                
                # 在截图上标记二维码位置
                for obj in decoded_objects:
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(np.array([point for point in points]))
                        points = hull
                    else:
                        points = np.array([point for point in points])
                    
                    # 绘制二维码边界
                    cv2.polylines(screenshot_cv, [points], True, (0, 255, 0), 3)
                    
                    # 在二维码上方显示数据
                    x = obj.rect.left
                    y = obj.rect.top - 10
                    cv2.putText(screenshot_cv, qr_data[:20], (x, y), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # 将OpenCV图像转换回QImage以显示
                height, width, channel = screenshot_cv.shape
                bytes_per_line = 3 * width
                q_img = QImage(cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2RGB).data, 
                              width, height, bytes_per_line, QImage.Format_RGB888)
                
                # 调整图像大小以适应窗口
                pixmap = QPixmap.fromImage(q_img)
                scaled_pixmap = pixmap.scaled(self.initial_width - 20, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                
                # 重置控件的固定高度限制
                self.result_text.setFixedHeight(16777215)
                self.image_label.setFixedHeight(16777215)
                
                # 显示结果区域和按钮
                self.result_container.show()
                self.image_label.show()
                self.clear_button.show()
                
                # 重置控件高度限制
                self.result_text.setFixedHeight(60)
                self.image_label.setFixedHeight(16777215)
                
                # 记录当前窗口位置
                current_x = self.x()
                current_y = self.y()
                
                # 重置窗口大小限制
                self.setMinimumSize(0, 0)
                self.setMaximumSize(16777215, 16777215)
                
                # 先调整窗口大小
                result_height = 350  # 有结果时的窗口高度
                self.resize(self.initial_width, result_height)
                
                # 然后显式设置位置
                self.move(current_x, current_y)
            else:
                # 未找到二维码
                self.result_text.setPlainText("未检测到二维码")
                
                # 显示原始截图
                height, width, channel = screenshot_cv.shape
                bytes_per_line = 3 * width
                q_img = QImage(cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2RGB).data, 
                              width, height, bytes_per_line, QImage.Format_RGB888)
                
                # 调整图像大小以适应窗口
                pixmap = QPixmap.fromImage(q_img)
                scaled_pixmap = pixmap.scaled(self.initial_width - 20, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                
                # 重置控件的固定高度限制
                self.result_text.setFixedHeight(16777215)
                self.image_label.setFixedHeight(16777215)
                
                # 显示结果区域和按钮
                self.result_container.show()
                self.image_label.show()
                self.clear_button.show()
                
                # 重置控件高度限制
                self.result_text.setFixedHeight(60)
                self.image_label.setFixedHeight(16777215)
                
                # 记录当前窗口位置
                current_x = self.x()
                current_y = self.y()
                
                # 重置窗口大小限制
                self.setMinimumSize(0, 0)
                self.setMaximumSize(16777215, 16777215)
                
                # 先调整窗口大小
                result_height = 350  # 有结果时的窗口高度
                self.resize(self.initial_width, result_height)
                
                # 然后显式设置位置
                self.move(current_x, current_y)
        except Exception as e:
            # 重新显示窗口并显示错误信息
            self.show()
            QMessageBox.critical(self, "错误", f"截屏或扫描过程中出错: {str(e)}")
            
            # 确保结果区域和清除按钮不显示
            self.clear_results()

def main():
    app = QApplication(sys.argv)
    ex = QRScannerApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()