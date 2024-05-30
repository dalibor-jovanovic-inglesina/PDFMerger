import sys
import os
import time
from PyPDF2 import PdfMerger
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QHBoxLayout, QLabel, QMessageBox, QDialog, QStyleFactory
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QThread, pyqtSignal

class MergeThread(QThread):
    started = pyqtSignal()
    finished = pyqtSignal(str)

    def __init__(self, pdf_folder_path, final_path, parent=None):
        super().__init__(parent)
        self.pdf_folder_path = pdf_folder_path
        self.final_path = final_path

    def run(self):
        self.started.emit()
        merger = PdfMerger()
        pdf_files = [f for f in os.listdir(self.pdf_folder_path) if f.lower().endswith('.pdf')]

        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_folder_path, pdf_file)
            merger.append(pdf_path)

        merger.write(self.final_path)
        merger.close()
        self.finished.emit(self.final_path)

class RenameFileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Rename File')
        self.setGeometry(300, 300, 300, 100)

        self.new_file_name = QLineEdit(self)
        self.new_file_name.setPlaceholderText('New File Name')

        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.accept)

        hbox = QHBoxLayout()
        hbox.addWidget(self.new_file_name)
        hbox.addWidget(self.ok_button)

        self.setLayout(hbox)

    def get_new_file_name(self):
        return self.new_file_name.text()

class PDFMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Merger')
        self.setGeometry(200, 200, 400, 200)

        self.pdf_folder_path = ''
        self.output_folder_path = ''

        self.choose_folder_button = QPushButton('Browse...', self)
        self.choose_folder_button.clicked.connect(self.choose_folder)

        self.final_file_path_label = QLabel('Files Folder:', self)
        self.final_file_path = QLineEdit(self)
        self.final_file_path.setReadOnly(True)

        self.final_file_name_label = QLabel('Final Pdf Name:', self)
        self.final_file_name = QLineEdit(self)
        self.final_file_name.setPlaceholderText('Insert the pdf file name')

        self.choose_output_folder_button = QPushButton('Select the destination folder (Optional)', self)
        self.choose_output_folder_button.clicked.connect(self.choose_output_folder)

        self.merge_button = QPushButton('Start Merging', self)
        self.merge_button.clicked.connect(self.merge_pdfs)

        vbox = QVBoxLayout()
        vbox.addWidget(self.choose_folder_button)
        vbox.addWidget(self.final_file_path_label)
        vbox.addWidget(self.final_file_path)
        vbox.addWidget(self.final_file_name_label)
        vbox.addWidget(self.final_file_name)
        vbox.addWidget(self.choose_output_folder_button)
        vbox.addWidget(self.merge_button)

        self.setLayout(vbox)

        self.merge_thread = None

    def choose_folder(self):
        self.pdf_folder_path = QFileDialog.getExistingDirectory(self, 'Select PDFs Folder')
        if self.pdf_folder_path:
            self.final_file_path.setText(self.pdf_folder_path)

    def choose_output_folder(self):
        self.output_folder_path = QFileDialog.getExistingDirectory(self, 'Select The Destionation Folder')
        #if self.output_folder_path:
            #self.show_notification('Selected destionation folder: ' + self.output_folder_path)

    def show_notification(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Notification')
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.addButton(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def merge_pdfs(self):
        if not self.pdf_folder_path:
            self.show_notification('Choose a folder containing the pdfs to merge.')
            return

        file_name = self.final_file_name.text()
        if not file_name:
            self.show_notification('Insert the merged pdf file name.')
            return

        if not self.output_folder_path:  # Use the selected folder if a destination folder isn't selected
            self.output_folder_path = self.pdf_folder_path

        final_path = os.path.join(self.output_folder_path, file_name + '.pdf')

        if os.path.exists(final_path):
            result = self.check_existing_file(final_path)
            if result == 'rename':
                new_name = self.rename_file()
                if new_name:
                    self.final_file_name.setText(new_name)
                    final_path = os.path.join(self.output_folder_path, new_name + '.pdf')
                else:
                    return
            elif result == 'cancel':
                return
            elif result == 'replace':
                os.remove(final_path)
                time.sleep(10)
            else:
                return

        self.merge_thread = MergeThread(self.pdf_folder_path, final_path)
        self.merge_thread.started.connect(self.on_merge_started)
        self.merge_thread.finished.connect(self.on_merge_finished)
        self.merge_thread.start()

    def on_merge_started(self):
        self.merge_button.setText('Merging...')

    def on_merge_finished(self, final_path):
        self.show_notification('Merge Completed. The file was saved in:\n' + final_path)
        self.merge_button.setText('Start Merging')

    def rename_file(self):
            dialog = RenameFileDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_name = dialog.get_new_file_name()
                if new_name:
                    self.final_file_name.setText(new_name)

    def check_existing_file(self, path):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle('File already exist')
        msg.setText('A file with the same name already exist.\nDo you want to rename or replace the existing file?')
        msg.addButton('Rename', QMessageBox.ButtonRole.AcceptRole)
        msg.addButton('Replace', QMessageBox.ButtonRole.AcceptRole)
        msg.addButton('Cancel', QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        if msg.clickedButton().text() == 'Rename':
            return 'rename'
        elif msg.clickedButton().text() == 'Replace':
            confirm_replace = self.confirm_replace_file(path)
            if confirm_replace == 'yes':
                return 'replace'
            else:
                return self.check_existing_file(path)
        else:
            return 'cancel'

    def confirm_replace_file(self, path):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle('Confirm Replace')
        msg.setText('Are you sure you want to replace the existing file?')
        msg.addButton('Yes', QMessageBox.ButtonRole.AcceptRole)
        msg.addButton('No', QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        if msg.clickedButton().text() == 'yes':
            return 'yes'
        else:
            return 'no'

def set_theme():
    app.setStyle(QStyleFactory.create('Fusion'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    set_theme()

    pdf_merger_app = PDFMergerApp()
    pdf_merger_app.show()

    sys.exit(app.exec())
