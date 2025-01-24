import sys
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QListWidget, QLabel,
                            QComboBox, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class ImageConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('LIVP/HEIC 转换工具')
        self.setFixedSize(600, 400)
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        main_widget.setLayout(layout)
        
        # 文件上传区域
        self.upload_area = QLabel("拖放文件到这里或点击上传", self)
        self.upload_area.setAlignment(Qt.AlignCenter)
        self.upload_area.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 2px dashed #6C5CE7;
                padding: 40px;
                color: #333;
                font-size: 14px;
            }
            QLabel:hover {
                background-color: #e0e0e0;
            }
        """)
        self.upload_area.setAcceptDrops(True)
        layout.addWidget(self.upload_area)
        
        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 8px;
                color: #333;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 4px;
            }
        """)
        layout.addWidget(self.file_list)
        
        # 底部控制区域
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # 格式选择
        self.format_combo = QComboBox()
        self.format_combo.addItems(['JPG', 'PNG'])
        self.format_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #ddd;
                padding: 4px;
                color: #333;
                font-size: 12px;
            }
        """)
        bottom_layout.addWidget(self.format_combo)
        
        # 转换按钮
        self.convert_btn = QPushButton('开始转换')
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5C4CD7;
            }
            QPushButton:pressed {
                background-color: #4C3CC7;
            }
        """)
        bottom_layout.addWidget(self.convert_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 2px;
                height: 4px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #6C5CE7;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        layout.addLayout(bottom_layout)
        
        # 连接信号
        self.upload_area.mousePressEvent = self.upload_files
        self.convert_btn.clicked.connect(self.start_conversion)
        
    def upload_files(self, event):
        from PyQt5.QtWidgets import QFileDialog
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择LIVP/HEIC文件",
            "",
            "Image Files (*.livp *.heic)"
        )
        if files:
            self.add_files(files)
        
    def start_conversion(self):
        from PIL import Image
        import pillow_heif
        import os
        import zipfile
        from pathlib import Path
        import tempfile
        
        if self.file_list.count() == 0:
            return
            
        output_format = self.format_combo.currentText().lower()
        total_files = self.file_list.count()
        
        for i in range(total_files):
            input_file = self.file_list.item(i).text()
            output_file = self.get_output_path(input_file, output_format)
            
            try:
                # 如果是LIVP文件，先解压
                if input_file.lower().endswith('.livp'):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        with zipfile.ZipFile(input_file, 'r') as zip_ref:
                            zip_ref.extractall(tmpdir)
                            
                        # 查找解压后的HEIC文件
                        heic_files = [f for f in os.listdir(tmpdir) 
                                    if f.lower().endswith('.heic')]
                        if not heic_files:
                            raise ValueError("LIVP文件中未找到HEIC文件")
                            
                        # 处理第一个HEIC文件
                        heic_path = os.path.join(tmpdir, heic_files[0])
                        heif_file = pillow_heif.open_heif(heic_path)
                else:
                    # 直接处理HEIC文件
                    heif_file = pillow_heif.open_heif(input_file)
                    
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                )
                
                # 保存为指定格式，将JPG转换为JPEG
                save_format = 'JPEG' if output_format == 'jpg' else output_format.upper()
                image.save(output_file, format=save_format)
                
                # 更新进度
                self.progress_bar.setValue(int((i+1)/total_files * 100))
                
            except Exception as e:
                print(f"转换失败: {input_file}, 错误: {str(e)}")
                
        self.progress_bar.setValue(100)
        
    def get_output_path(self, input_path, output_format):
        """生成输出文件路径"""
        path = Path(input_path)
        return str(path.with_suffix(f".{output_format}"))
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.add_files(files)
        
    def add_files(self, files):
        for file in files:
            if file.lower().endswith(('.livp', '.heic')):
                self.file_list.addItem(file)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageConverterApp()
    window.show()
    sys.exit(app.exec_())
