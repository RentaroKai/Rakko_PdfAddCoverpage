import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
    QVBoxLayout, QHBoxLayout, QProgressBar, QListWidget, QMessageBox, QListWidgetItem,
    QInputDialog  # この行を追加
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize
from utils.pdf_utils import PDFHandler
from utils.image_utils import ImageHandler
from utils.set_manager import SetManager

class PDFCoverAdder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDFカバー追加ツール")
        self.setGeometry(100, 100, 800, 600)
        
        self.pdf_path = ""
        self.front_cover_path = ""
        self.back_cover_path = ""
        
        self.set_manager = SetManager()
        
        # デバッグ用の出力を追加
        print(f"設定ファイルのパス: {self.set_manager.config_path}")
        
        self.init_ui()
        self.populate_set_list()  # セットリストを初期化
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # ファイル選択セクション
        file_selection_layout = QHBoxLayout()
        
        # 元のPDFファイル
        self.pdf_label = QLabel("元のPDFファイル:")
        self.pdf_input = QLineEdit()
        self.pdf_browse = QPushButton("選択")
        self.pdf_browse.clicked.connect(self.browse_pdf)
        file_selection_layout.addWidget(self.pdf_label)
        file_selection_layout.addWidget(self.pdf_input)
        file_selection_layout.addWidget(self.pdf_browse)
        
        # 表紙JPGファイル
        self.front_label = QLabel("表紙JPGファイル:")
        self.front_input = QLineEdit()
        self.front_browse = QPushButton("選択")
        self.front_browse.clicked.connect(self.browse_front_cover)
        file_selection_layout.addWidget(self.front_label)
        file_selection_layout.addWidget(self.front_input)
        file_selection_layout.addWidget(self.front_browse)
        
        # 裏表紙JPGファイル
        self.back_label = QLabel("裏表紙JPGファイル:")
        self.back_input = QLineEdit()
        self.back_browse = QPushButton("選択")
        self.back_browse.clicked.connect(self.browse_back_cover)
        file_selection_layout.addWidget(self.back_label)
        file_selection_layout.addWidget(self.back_input)
        file_selection_layout.addWidget(self.back_browse)
        
        layout.addLayout(file_selection_layout)
        
        # プレビューセクション
        preview_layout = QHBoxLayout()
        
        self.front_preview = QLabel("表紙プレビュー")
        self.front_preview.setFixedSize(200, 200)
        self.front_preview.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.front_preview)
        
        self.back_preview = QLabel("裏表紙プレビュー")
        self.back_preview.setFixedSize(200, 200)
        self.back_preview.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.back_preview)
        
        layout.addLayout(preview_layout)
        
        # 実行ボタンと進捗バー
        run_layout = QHBoxLayout()
        self.run_button = QPushButton("実行")
        self.run_button.clicked.connect(self.run_process)
        self.progress_bar = QProgressBar()
        run_layout.addWidget(self.run_button)
        run_layout.addWidget(self.progress_bar)
        layout.addLayout(run_layout)
        
        # 結果メッセージ
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)
        
        # セット管理セクション
        set_layout = QHBoxLayout()
        
        self.set_save_button = QPushButton("セット保存")
        self.set_save_button.clicked.connect(self.save_set)
        set_layout.addWidget(self.set_save_button)
        
        self.set_load_button = QPushButton("セット読み込み")
        self.set_load_button.clicked.connect(self.load_set)
        set_layout.addWidget(self.set_load_button)
        
        layout.addLayout(set_layout)
        
        # セットリスト表示
        self.set_list = QListWidget()
        self.set_list.itemClicked.connect(self.load_set_item)
        layout.addWidget(self.set_list)
        
        self.set_manager.load_sets()
        self.populate_set_list()
        
        self.setLayout(layout)
    
    def browse_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "PDFファイルを選択", "", "PDF Files (*.pdf)")
        if file_path:
            self.pdf_path = file_path
            self.pdf_input.setText(file_path)
    
    def browse_front_cover(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "表紙JPGファイルを選択", "", "JPEG Files (*.jpg *.jpeg)")
        if file_path:
            self.front_cover_path = file_path
            self.front_input.setText(file_path)
            self.display_image(file_path, self.front_preview)
    
    def browse_back_cover(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "裏表紙JPGファイルを選択", "", "JPEG Files (*.jpg *.jpeg)")
        if file_path:
            self.back_cover_path = file_path
            self.back_input.setText(file_path)
            self.display_image(file_path, self.back_preview)
    
    def display_image(self, path, label):
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
    
    def run_process(self):
        if not self.pdf_path or not self.front_cover_path or not self.back_cover_path:
            QMessageBox.warning(self, "エラー", "すべてのファイルを選択してください。")
            return
        
        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.result_label.setText("")
        
        try:
            pdf_handler = PDFHandler(self.pdf_path)
            image_handler = ImageHandler()
            
            max_width, max_height = pdf_handler.get_max_page_size()
            self.progress_bar.setValue(20)
            
            resized_front = image_handler.resize_image(self.front_cover_path, max_width, max_height)
            resized_back = image_handler.resize_image(self.back_cover_path, max_width, max_height)
            self.progress_bar.setValue(40)
            
            pdf_handler.add_covers(resized_front, resized_back)
            self.progress_bar.setValue(70)
            
            save_path, _ = QFileDialog.getSaveFileName(self, "保存先を選択", "", "PDF Files (*.pdf)")
            if save_path:
                pdf_handler.save(save_path)
                self.progress_bar.setValue(100)
                self.result_label.setText("PDFにカバーを追加しました。")
            else:
                self.result_label.setText("保存がキャンセルされました。")
        except Exception as e:
            QMessageBox.critical(self, "エラー", str(e))
        finally:
            self.run_button.setEnabled(True)
            self.progress_bar.setValue(0)
    
    def save_set(self):
        set_name, ok = QInputDialog.getText(self, "セット名を入力", "セット名:")
        if ok and set_name:
            set_data = {
                "pdf_path": self.pdf_path,
                "front_cover_path": self.front_cover_path,
                "back_cover_path": self.back_cover_path
            }
            self.set_manager.save_set(set_name, set_data)
            print(f"Saving set: {set_name}")  # デバッグ用出力
            print(f"Set data: {set_data}")  # デバッグ用出力
            self.populate_set_list()
            QMessageBox.information(self, "成功", f"セット '{set_name}' が保存されました。")
    
    def load_set(self):
        self.populate_set_list()
    
    def populate_set_list(self):
        self.set_list.clear()
        for set_name in self.set_manager.sets.keys():
            item = QListWidgetItem(set_name)
            self.set_list.addItem(item)
    
    def load_set_item(self, item):
        set_data = self.set_manager.sets.get(item.text(), {})
        self.pdf_path = set_data.get("pdf_path", "")
        self.front_cover_path = set_data.get("front_cover_path", "")
        self.back_cover_path = set_data.get("back_cover_path", "")
        
        self.pdf_input.setText(self.pdf_path)
        self.front_input.setText(self.front_cover_path)
        self.back_input.setText(self.back_cover_path)
        
        if self.front_cover_path:
            self.display_image(self.front_cover_path, self.front_preview)
        if self.back_cover_path:
            self.display_image(self.back_cover_path, self.back_preview)

def main():
    app = QApplication(sys.argv)
    window = PDFCoverAdder()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()