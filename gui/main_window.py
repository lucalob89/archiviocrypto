from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QProgressBar, QComboBox, QFrame, QMessageBox,
    QStackedWidget, QCheckBox, QSizePolicy
)

from core.encryption import encrypt_zip
from core.decryption import decrypt_zip


TEXT = {
    "it": {
        "tagline": "Gestione sicura degli archivi",
        "title": "Proteggi i tuoi archivi.",
        "subtitle": "Crittografia locale, semplice e completamente offline.",
        "encrypt": "Cripta ZIP", "decrypt": "Decripta",
        "input": "Archivio da elaborare",
        "drop": "Trascina qui il file oppure selezionalo dal computer",
        "browse": "Scegli file…", "password": "Password",
        "confirm": "Conferma password", "show": "Mostra password",
        "output": "File di destinazione", "output_hint": "Verrà scelto automaticamente",
        "run_encrypt": "CRITTOGRAFA ARCHIVIO",
        "run_decrypt": "DECRITTOGRAFA ARCHIVIO",
        "ready": "Pronto", "working": "Operazione in corso…",
        "done": "Operazione completata.", "error": "Operazione non riuscita",
        "cancel": "Annulla", "choose_zip": "Seleziona un archivio ZIP",
        "choose_enc": "Seleziona un file ArchivioCrypto",
        "zip_filter": "Archivi ZIP (*.zip)", "enc_filter": "ArchivioCrypto (*.acrypt)",
        "save_enc": "Salva archivio criptato", "save_zip": "Salva archivio ZIP",
        "all_files": "Tutti i file (*)",
        "need_file": "Seleziona prima un file.",
        "need_password": "Inserisci una password.",
        "password_mismatch": "Le password non coincidono.",
        "confirm_title": "Conferma operazione",
        "confirm_encrypt": "Il file originale non verrà modificato. Vuoi continuare?",
        "confirm_decrypt": "Il file criptato non verrà modificato. Vuoi continuare?",
        "success_title": "Completato",
        "success_text": "File creato correttamente:\n{}",
        "security": "AES-256-GCM  •  Elaborazione locale  •  Nessun cloud",
        "mode_encrypt": "Modalità: crittografia",
        "mode_decrypt": "Modalità: decrittografia",
        "lang": "Lingua", "theme": "Tema", "light": "Chiaro", "dark": "Scuro",
        "cancelled": "Operazione annullata.",
    },
    "en": {
        "tagline": "Secure archive manager",
        "title": "Protect your archives.",
        "subtitle": "Local encryption, simple and completely offline.",
        "encrypt": "Encrypt ZIP", "decrypt": "Decrypt",
        "input": "Archive to process",
        "drop": "Drop a file here or choose it from your computer",
        "browse": "Choose file…", "password": "Password",
        "confirm": "Confirm password", "show": "Show password",
        "output": "Output file", "output_hint": "Selected automatically",
        "run_encrypt": "ENCRYPT ARCHIVE",
        "run_decrypt": "DECRYPT ARCHIVE",
        "ready": "Ready", "working": "Working…",
        "done": "Operation completed.", "error": "Operation failed",
        "cancel": "Cancel", "choose_zip": "Choose a ZIP archive",
        "choose_enc": "Choose an ArchivioCrypto file",
        "zip_filter": "ZIP archives (*.zip)", "enc_filter": "ArchivioCrypto (*.acrypt)",
        "save_enc": "Save encrypted archive", "save_zip": "Save ZIP archive",
        "all_files": "All files (*)",
        "need_file": "Please select a file first.",
        "need_password": "Please enter a password.",
        "password_mismatch": "Passwords do not match.",
        "confirm_title": "Confirm operation",
        "confirm_encrypt": "The original file will not be changed. Continue?",
        "confirm_decrypt": "The encrypted file will not be changed. Continue?",
        "success_title": "Completed",
        "success_text": "File created successfully:\n{}",
        "security": "AES-256-GCM  •  Local processing  •  No cloud",
        "mode_encrypt": "Mode: encryption",
        "mode_decrypt": "Mode: decryption",
        "lang": "Language", "theme": "Theme", "light": "Light", "dark": "Dark",
        "cancelled": "Operation cancelled.",
    }
}

LIGHT_QSS = """
QMainWindow, QWidget#root { background: #F4F7FB; color: #172033; }
QFrame#header { background: #142B50; border-radius: 16px; }
QLabel#brand { color: white; font-size: 21px; font-weight: 700; }
QLabel#tagline, QLabel#heroSub { color: #C8D5E8; }
QLabel#hero { color: white; font-size: 25px; font-weight: 700; }
QFrame#panel { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }
QLabel#section { font-weight: 650; color: #25334A; }
QLineEdit { background: #FFFFFF; border: 1px solid #D6DFEA; border-radius: 8px; padding: 11px; color: #172033; }
QLineEdit:focus { border: 1px solid #3978D8; }
QPushButton { border: 0; border-radius: 8px; padding: 10px 15px; background: #E8EEF7; color: #20334F; font-weight: 600; }
QPushButton:hover { background: #DCE7F5; }
QPushButton#primary { background: #2463C5; color: white; padding: 14px; }
QPushButton#primary:hover { background: #1C54AA; }
QPushButton#selectedMode { background: #DCEAFF; color: #174A99; border: 1px solid #B8D2FA; }
QComboBox { background: white; border: 1px solid #D6DFEA; border-radius: 7px; padding: 7px; min-width: 95px; }
QProgressBar { border: 0; background: #E8EEF5; border-radius: 5px; height: 9px; text-align: center; }
QProgressBar::chunk { background: #2871D3; border-radius: 5px; }
QCheckBox { color: #53647B; }
QLabel#muted { color: #64748B; }
"""

DARK_QSS = """
QMainWindow, QWidget#root { background: #101827; color: #E7EDF7; }
QFrame#header { background: #172D50; border-radius: 16px; }
QLabel#brand { color: white; font-size: 21px; font-weight: 700; }
QLabel#tagline, QLabel#heroSub { color: #C0CEE2; }
QLabel#hero { color: white; font-size: 25px; font-weight: 700; }
QFrame#panel { background: #192538; border: 1px solid #2B3B52; border-radius: 14px; }
QLabel#section { font-weight: 650; color: #E3EBF7; }
QLineEdit { background: #111D2E; border: 1px solid #34465F; border-radius: 8px; padding: 11px; color: #F1F5F9; }
QLineEdit:focus { border: 1px solid #5C9AF0; }
QPushButton { border: 0; border-radius: 8px; padding: 10px 15px; background: #2A3A51; color: #E5EDF8; font-weight: 600; }
QPushButton:hover { background: #354A66; }
QPushButton#primary { background: #2869C5; color: white; padding: 14px; }
QPushButton#primary:hover { background: #347BD9; }
QPushButton#selectedMode { background: #213F68; color: #BBD7FF; border: 1px solid #3C6599; }
QComboBox { background: #192538; border: 1px solid #34465F; border-radius: 7px; padding: 7px; min-width: 95px; color: #E7EDF7; }
QComboBox QAbstractItemView { background: #192538; color: #E7EDF7; selection-background-color: #2869C5; }
QProgressBar { border: 0; background: #2B3B50; border-radius: 5px; height: 9px; text-align: center; }
QProgressBar::chunk { background: #4D91ED; border-radius: 5px; }
QCheckBox { color: #BAC7D8; }
QLabel#muted { color: #9BAAC0; }
"""

class Worker(QThread):
    progress = Signal(int)
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, operation, source, destination, password):
        super().__init__()
        self.operation = operation
        self.source = source
        self.destination = destination
        self.password = password
        self._cancel_requested = False

    def cancel(self):
        self._cancel_requested = True

    def is_cancelled(self):
        return self._cancel_requested

    def run(self):
        try:
            fn = encrypt_zip if self.operation == "encrypt" else decrypt_zip
            result = fn(
                self.source, self.destination, self.password,
                progress=self.progress.emit,
                cancelled=self.is_cancelled
            )
            self.succeeded.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class DropLineEdit(QLineEdit):
    file_dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.file_dropped.emit(urls[0].toLocalFile())
            event.acceptProposedAction()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "it"
        self.dark = False
        self.mode = "encrypt"
        self.worker = None
        self.setWindowTitle("ArchivioCrypto")
        self.setMinimumSize(650, 720)
        self.resize(760, 820)
        self.build_ui()
        self.retranslate()
        self.apply_theme()

    def tr(self, key):
        return TEXT[self.language][key]

    def build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(28, 24, 28, 22)
        outer.setSpacing(16)

        # Header / hero
        header = QFrame()
        header.setObjectName("header")
        h = QVBoxLayout(header)
        h.setContentsMargins(24, 20, 24, 22)
        top = QHBoxLayout()
        logo = QLabel("⬡")
        logo.setStyleSheet("color:#67D8E8;font-size:30px;font-weight:700;")
        brand_col = QVBoxLayout()
        self.brand = QLabel("ArchivioCrypto")
        self.brand.setObjectName("brand")
        self.tagline = QLabel()
        self.tagline.setObjectName("tagline")
        brand_col.addWidget(self.brand)
        brand_col.addWidget(self.tagline)
        top.addWidget(logo)
        top.addLayout(brand_col)
        top.addStretch()
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Italiano", "it")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        self.theme_combo = QComboBox()
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        top.addWidget(self.lang_combo)
        top.addWidget(self.theme_combo)
        h.addLayout(top)
        self.hero = QLabel()
        self.hero.setObjectName("hero")
        self.hero_sub = QLabel()
        self.hero_sub.setObjectName("heroSub")
        h.addSpacing(16)
        h.addWidget(self.hero)
        h.addWidget(self.hero_sub)
        outer.addWidget(header)

        # Main panel
        panel = QFrame()
        panel.setObjectName("panel")
        p = QVBoxLayout(panel)
        p.setContentsMargins(22, 20, 22, 20)
        p.setSpacing(13)

        mode_row = QHBoxLayout()
        self.encrypt_btn = QPushButton()
        self.decrypt_btn = QPushButton()
        self.encrypt_btn.clicked.connect(lambda: self.set_mode("encrypt"))
        self.decrypt_btn.clicked.connect(lambda: self.set_mode("decrypt"))
        mode_row.addWidget(self.encrypt_btn)
        mode_row.addWidget(self.decrypt_btn)
        p.addLayout(mode_row)

        self.mode_label = QLabel()
        self.mode_label.setObjectName("muted")
        p.addWidget(self.mode_label)

        self.file_label = QLabel()
        self.file_label.setObjectName("section")
        p.addWidget(self.file_label)
        file_row = QHBoxLayout()
        self.file_edit = DropLineEdit()
        self.file_edit.setReadOnly(True)
        self.file_edit.file_dropped.connect(self.set_file)
        self.browse_btn = QPushButton()
        self.browse_btn.clicked.connect(self.browse_file)
        file_row.addWidget(self.file_edit, 1)
        file_row.addWidget(self.browse_btn)
        p.addLayout(file_row)
        self.drop_hint = QLabel()
        self.drop_hint.setObjectName("muted")
        p.addWidget(self.drop_hint)

        self.password_label = QLabel()
        self.password_label.setObjectName("section")
        p.addWidget(self.password_label)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(42)
        p.addWidget(self.password_edit)

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setMinimumHeight(42)
        p.addWidget(self.confirm_edit)

        self.show_password = QCheckBox()
        self.show_password.toggled.connect(self.toggle_password)
        p.addWidget(self.show_password)

        self.output_label = QLabel()
        self.output_label.setObjectName("section")
        p.addWidget(self.output_label)
        out_row = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("")
        self.output_browse = QPushButton("…")
        self.output_browse.clicked.connect(self.browse_output)
        out_row.addWidget(self.output_edit, 1)
        out_row.addWidget(self.output_browse)
        p.addLayout(out_row)

        self.run_btn = QPushButton()
        self.run_btn.setObjectName("primary")
        self.run_btn.setMinimumHeight(48)
        self.run_btn.clicked.connect(self.start_operation)
        p.addSpacing(4)
        p.addWidget(self.run_btn)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        p.addWidget(self.progress)
        self.status = QLabel()
        self.status.setObjectName("muted")
        p.addWidget(self.status)
        outer.addWidget(panel)

        footer = QHBoxLayout()
        self.security = QLabel()
        self.security.setObjectName("muted")
        footer.addWidget(self.security)
        footer.addStretch()
        outer.addLayout(footer)
        outer.addStretch()

    def retranslate(self):
        t = TEXT[self.language]
        self.tagline.setText(t["tagline"])
        self.hero.setText(t["title"])
        self.hero_sub.setText(t["subtitle"])
        self.encrypt_btn.setText(t["encrypt"])
        self.decrypt_btn.setText(t["decrypt"])
        self.file_label.setText(t["input"])
        self.drop_hint.setText(t["drop"])
        self.browse_btn.setText(t["browse"])
        self.password_label.setText(t["password"])
        self.confirm_edit.setPlaceholderText(t["confirm"])
        self.show_password.setText(t["show"])
        self.output_label.setText(t["output"])
        self.output_edit.setPlaceholderText(t["output_hint"])
        self.run_btn.setText(t["run_encrypt"] if self.mode == "encrypt" else t["run_decrypt"])
        self.status.setText(t["ready"])
        self.security.setText(t["security"])
        self.theme_combo.blockSignals(True)
        current = self.theme_combo.currentData()
        self.theme_combo.clear()
        self.theme_combo.addItem(t["light"], "light")
        self.theme_combo.addItem(t["dark"], "dark")
        self.theme_combo.setCurrentIndex(1 if self.dark else 0)
        self.theme_combo.blockSignals(False)
        self.update_mode_ui()

    def change_language(self, index):
        self.language = self.lang_combo.itemData(index)
        self.retranslate()

    def change_theme(self, index):
        self.dark = self.theme_combo.itemData(index) == "dark"
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(DARK_QSS if self.dark else LIGHT_QSS)

    def set_mode(self, mode):
        self.mode = mode
        self.file_edit.clear()
        self.output_edit.clear()
        self.password_edit.clear()
        self.confirm_edit.clear()
        self.progress.setValue(0)
        self.retranslate()

    def update_mode_ui(self):
        self.encrypt_btn.setObjectName("selectedMode" if self.mode == "encrypt" else "")
        self.decrypt_btn.setObjectName("selectedMode" if self.mode == "decrypt" else "")
        # Re-polish buttons so the selected state updates.
        for button in (self.encrypt_btn, self.decrypt_btn):
            button.style().unpolish(button)
            button.style().polish(button)
        self.mode_label.setText(self.tr("mode_encrypt" if self.mode == "encrypt" else "mode_decrypt"))
        self.confirm_edit.setVisible(self.mode == "encrypt")
        self.run_btn.setText(self.tr("run_encrypt" if self.mode == "encrypt" else "run_decrypt"))
        self.file_edit.setPlaceholderText("*.zip" if self.mode == "encrypt" else "*.acrypt")

    def browse_file(self):
        if self.mode == "encrypt":
            path, _ = QFileDialog.getOpenFileName(
                self, self.tr("choose_zip"), "", self.tr("zip_filter")
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, self.tr("choose_enc"), "", self.tr("enc_filter")
            )
        if path:
            self.set_file(path)

    def set_file(self, path):
        if not path:
            return
        self.file_edit.setText(path)
        source = Path(path)
        suffix = ".acrypt" if self.mode == "encrypt" else ".zip"
        self.output_edit.setText(str(source.with_name(source.stem + suffix)))

    def browse_output(self):
        source = self.file_edit.text().strip()
        if not source:
            QMessageBox.warning(self, "ArchivioCrypto", self.tr("need_file"))
            return
        if self.mode == "encrypt":
            path, _ = QFileDialog.getSaveFileName(
                self, self.tr("save_enc"), self.output_edit.text(),
                self.tr("enc_filter")
            )
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, self.tr("save_zip"), self.output_edit.text(),
                self.tr("zip_filter")
            )
        if path:
            self.output_edit.setText(path)

    def toggle_password(self, checked):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.password_edit.setEchoMode(mode)
        self.confirm_edit.setEchoMode(mode)

    def start_operation(self):
        source = self.file_edit.text().strip()
        password = self.password_edit.text()
        destination = self.output_edit.text().strip()

        if not source:
            QMessageBox.warning(self, "ArchivioCrypto", self.tr("need_file"))
            return
        if not password:
            QMessageBox.warning(self, "ArchivioCrypto", self.tr("need_password"))
            return
        if self.mode == "encrypt" and password != self.confirm_edit.text():
            QMessageBox.warning(self, "ArchivioCrypto", self.tr("password_mismatch"))
            return
        if not destination:
            self.set_file(source)
            destination = self.output_edit.text().strip()

        prompt = self.tr("confirm_encrypt" if self.mode == "encrypt" else "confirm_decrypt")
        answer = QMessageBox.question(
            self, self.tr("confirm_title"), prompt,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return

        self.set_busy(True)
        self.progress.setValue(0)
        self.status.setText(self.tr("working"))
        self.worker = Worker(self.mode, source, destination, password)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.succeeded.connect(self.operation_succeeded)
        self.worker.failed.connect(self.operation_failed)
        self.worker.start()

    def set_busy(self, busy):
        for widget in (
            self.encrypt_btn, self.decrypt_btn, self.browse_btn,
            self.output_browse, self.run_btn, self.lang_combo,
            self.theme_combo, self.password_edit, self.confirm_edit
        ):
            widget.setEnabled(not busy)
        self.file_edit.setEnabled(not busy)
        self.output_edit.setEnabled(not busy)
        self.show_password.setEnabled(not busy)
        if busy:
            self.run_btn.setText(self.tr("working"))
        else:
            self.update_mode_ui()

    def operation_succeeded(self, result):
        self.set_busy(False)
        self.password_edit.clear()
        self.confirm_edit.clear()
        self.status.setText(self.tr("done"))
        QMessageBox.information(
            self, self.tr("success_title"),
            self.tr("success_text").format(result)
        )

    def operation_failed(self, message):
        self.set_busy(False)
        self.password_edit.clear()
        self.confirm_edit.clear()
        self.status.setText(self.tr("error"))
        QMessageBox.critical(self, self.tr("error"), message)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(
                self, "ArchivioCrypto",
                "Wait for the current operation to finish before closing."
            )
            event.ignore()
        else:
            event.accept()
