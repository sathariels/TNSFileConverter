import sys
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
import fitz
import os
import zipfile

# Import the pdfTOTnsConvertor class from the PDF to TNS conversion part
class PdfToTnsConverter:
    def __init__(self, pdfPath, tnsPath):
        # Initialize the converter with paths for the input PDF and output TNS file
        self.pdfPath = pdfPath
        self.tnsPath = tnsPath

    def extractText(self):
        # Open the PDF file
        doc = fitz.open(self.pdfPath)
        text = ""  # Initialize an empty string to hold the extracted text
        # Iterate through each page in the PDF
        for pageNum in range(doc.page_count):
            page = doc.load_page(pageNum)  # Load the current page
            text += page.get_text()  # Append the text from the current page to the text string
        return text  # Return the extracted text

    def createTnsFile(self, text):
        # Define the XML structure for a simple TI-Nspire document
        tnsContent = f"""<?xml version="1.0" encoding="utf-8"?>
        <document xmlns="https://www.ti.com/Nspire-XML/3.0/"> 
            <page>
                <text>{text}</text>
            </page>
        </document>"""
        # this is not right i will attempt to fix 
        # Create a temporary directory to hold the XML file
        temp_dir = "temp_tns"
        os.makedirs(temp_dir, exist_ok=True)  # Ensure the directory exists
        xml_path = os.path.join(temp_dir, "document.xml")  # Path for the XML file

        # Write the XML content to the file
        with open(xml_path, 'w', encoding='utf-8') as xmlFile:
            xmlFile.write(tnsContent)  # Write the XML content to the file

        # Create the ZIP file with the .tns extension
        with zipfile.ZipFile(self.tnsPath, 'w') as tnsFile:
            tnsFile.write(xml_path, 'document.xml')  # Add the XML file to the ZIP archive

        # Clean up the temporary directory
        os.remove(xml_path)  # Remove the XML file
        os.rmdir(temp_dir)  # Remove the temporary directory

    def convertToTns(self):
        # Extract text from the PDF
        text = self.extractText()
        # Create the TNS file with the extracted text
        self.createTnsFile(text)


class ConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Converter")
        self.setGeometry(400, 300, 500, 300)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)
        self.files = []
        self.createDragDropBox()
        self.createFileListBox()
        self.createConvertButton()

    def createDragDropBox(self):
        self.dragDropLabel = QLabel("Drag and Drop PDF Files Here", alignment=Qt.AlignCenter)
        self.dragDropLabel.setFont(QFont("Arial", 15))
        self.dragDropLabel.setStyleSheet("border: 2px dashed #aaa; padding: 10px;")
        self.dragDropLabel.setAcceptDrops(True)
        self.dragDropLabel.dragEnterEvent = self.dragEnterEvent
        self.dragDropLabel.dropEvent = self.dropEvent
        self.layout.addWidget(self.dragDropLabel, 2)

    def createFileListBox(self):
        self.fileNamesLabel = QLabel("Files:", alignment=Qt.AlignTop)
        self.fileNamesLabel.setFont(QFont("Arial", 15))
        self.fileNamesLabel.setStyleSheet("border: 1px solid #aaa; padding: 10px;")
        self.layout.addWidget(self.fileNamesLabel, 3)

    def createConvertButton(self):
        self.convertButton = QPushButton("Convert")
        self.convertButton.setFont(QFont("Arial", 15))
        self.convertButton.clicked.connect(self.convertFiles)
        self.layout.addWidget(self.convertButton, 1)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                filePath = str(url.toLocalFile())
                if filePath.lower().endswith('.pdf'):
                    self.files.append(filePath)
                else:
                    print("Unsupported file format:", filePath)
            self.updateFileNamesLabel()
            event.accept()
        else:
            event.ignore()

    def updateFileNamesLabel(self):
        fileNames = [filePath.split('/')[-1] for filePath in self.files]
        self.fileNamesLabel.setText("\n".join(fileNames))

    def convertFiles(self):
        for filePath in self.files:
            tnsPath = filePath + ".tns"  # Define the TNS file path based on the PDF file path
            convertor = PdfToTnsConverter(filePath, tnsPath)
            try:
                convertor.convertToTns()
                print("Conversion successful:", tnsPath)
            except Exception as e:
                print("Error occurred during conversion:")
                print(e)

def createGui():
    app = QApplication(sys.argv)
    gui = ConverterGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    createGui()
