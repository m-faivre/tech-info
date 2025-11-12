from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
import os

class PdfViewer(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.webView = QWebEngineView()
        self.webView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Nouvelle ligne
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        
        self.layout.addWidget(self.webView)

        self.load_file("reglement.pdf")

    def load_file(self, filename):
        if os.path.isfile(filename):
            self.webView.setUrl(QUrl.fromLocalFile(os.path.abspath(filename)))
        else:
            print(f"Le fichier {filename} n'existe pas.")
