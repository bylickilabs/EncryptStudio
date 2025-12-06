import os
import sys
import base64
import sqlite3
from datetime import datetime

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QComboBox,
    QMessageBox,
    QStatusBar,
    QGroupBox,
    QFormLayout,
)

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


APP_NAME        = "Encrypt Studio"
APP_TITLE       = "Encrypt Studio - Secure Encryption Toolkit"
APP_VERSION     = "1.0.0"
APP_COMPANY     = "BYLICKILABS - Intelligence Systems & Communications"
APP_GITHUB_URL  = "https://github.com/bylickilabs/EncryptStudio"
DB_FILE         = "encrypt_studio.db"


class EasySQL:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_db(self):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    target TEXT,
                    status TEXT NOT NULL,
                    message TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def log_operation(self, action: str, target: str, status: str, message: str = ""):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO operations (action, target, status, message, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (action, target, status, message, datetime.utcnow().isoformat()),
            )
            conn.commit()
        finally:
            conn.close()


TRANSLATIONS = {
    "de": {
        "app_title": APP_TITLE,
        "label_language": "Sprache",
        "label_password": "Master-Passwort",
        "label_file": "Zieldatei",
        "btn_browse": "Durchsuchen...",
        "group_file_enc": "Datei-Verschlüsselung",
        "btn_encrypt_file": "Datei verschlüsseln",
        "btn_decrypt_file": "Datei entschlüsseln",
        "group_text_enc": "Text-Verschlüsselung",
        "label_plain_text": "Klartext",
        "label_cipher_text": "Verschlüsselter Text (Base64)",
        "btn_encrypt_text": "Text verschlüsseln",
        "btn_decrypt_text": "Text entschlüsseln",
        "status_ready": "Bereit.",
        "msg_no_password_title": "Fehlendes Passwort",
        "msg_no_password_text": "Bitte ein Master-Passwort eingeben.",
        "msg_no_file_title": "Keine Datei ausgewählt",
        "msg_no_file_text": "Bitte eine Datei auswählen.",
        "msg_encrypt_success_title": "Verschlüsselung erfolgreich",
        "msg_encrypt_success_text": "Die Datei wurde erfolgreich verschlüsselt.",
        "msg_decrypt_success_title": "Entschlüsselung erfolgreich",
        "msg_decrypt_success_text": "Die Datei wurde erfolgreich entschlüsselt.",
        "msg_encrypt_error_title": "Fehler bei der Verschlüsselung",
        "msg_decrypt_error_title": "Fehler bei der Entschlüsselung",
        "msg_text_encrypt_error_title": "Fehler bei der Textverschlüsselung",
        "msg_text_decrypt_error_title": "Fehler bei der Textentschlüsselung",
        "github_button": "GitHub",
        "info_button": "Info",
        "info_title": "Über diese Anwendung",
        "info_text": (
            f"{APP_NAME}\n\n"
            f"Version: {APP_VERSION}\n"
            f"Unternehmen: {APP_COMPANY}\n\n"
            "Encrypt Studio ist ein lokales Verschlüsselungs-Toolkit für Dateien "
            "und Texte. Alle Operationen erfolgen lokal – es werden keine Daten "
            "an externe Server übertragen.\n\n"
            "Features:\n"
            "- AES-256-GCM Verschlüsselung\n"
            "- Passwortbasierte Schlüsselableitung (PBKDF2)\n"
            "- EasySQL-Logging in einer lokalen SQLite-Datenbank\n"
        ),
        "file_dialog_title": "Datei auswählen",
        "status_encrypting": "Verschlüssele Datei...",
        "status_decrypting": "Entschlüssele Datei...",
        "status_done": "Fertig.",
    },
    "en": {
        "app_title": APP_TITLE,
        "label_language": "Language",
        "label_password": "Master password",
        "label_file": "Target file",
        "btn_browse": "Browse...",
        "group_file_enc": "File Encryption",
        "btn_encrypt_file": "Encrypt file",
        "btn_decrypt_file": "Decrypt file",
        "group_text_enc": "Text Encryption",
        "label_plain_text": "Plain text",
        "label_cipher_text": "Encrypted text (Base64)",
        "btn_encrypt_text": "Encrypt text",
        "btn_decrypt_text": "Decrypt text",
        "status_ready": "Ready.",
        "msg_no_password_title": "Missing password",
        "msg_no_password_text": "Please enter a master password.",
        "msg_no_file_title": "No file selected",
        "msg_no_file_text": "Please select a file.",
        "msg_encrypt_success_title": "Encryption successful",
        "msg_encrypt_success_text": "The file was encrypted successfully.",
        "msg_decrypt_success_title": "Decryption successful",
        "msg_decrypt_success_text": "The file was decrypted successfully.",
        "msg_encrypt_error_title": "Encryption error",
        "msg_decrypt_error_title": "Decryption error",
        "msg_text_encrypt_error_title": "Text encryption error",
        "msg_text_decrypt_error_title": "Text decryption error",
        "github_button": "GitHub",
        "info_button": "Info",
        "info_title": "About this application",
        "info_text": (
            f"{APP_NAME}\n\n"
            f"Version: {APP_VERSION}\n"
            f"Company: {APP_COMPANY}\n\n"
            "Encrypt Studio is a local encryption toolkit for files and text. "
            "All operations are performed locally – no data is transmitted to "
            "external servers.\n\n"
            "Features:\n"
            "- AES-256-GCM encryption\n"
            "- Password-based key derivation (PBKDF2)\n"
            "- EasySQL logging in a local SQLite database\n"
        ),
        "file_dialog_title": "Choose file",
        "status_encrypting": "Encrypting file...",
        "status_decrypting": "Decrypting file...",
        "status_done": "Done.",
    },
}


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """PBKDF2-HMAC-SHA256 → 32-Byte-Key."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
        backend=default_backend(),
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(password: str, data: bytes) -> bytes:
    """
    AES-256-GCM Containerformat:
    magic(4) + salt(16) + nonce(12) + ciphertext+tag
    """
    magic = b"ES01"
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key_from_password(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return magic + salt + nonce + ciphertext


def decrypt_bytes(password: str, container: bytes) -> bytes:
    if len(container) < 4 + 16 + 12:
        raise ValueError("Invalid encrypted data container.")

    magic = container[:4]
    if magic != b"ES01":
        raise ValueError("Invalid magic header.")

    salt = container[4:4+16]
    nonce = container[4+16:4+16+12]
    ciphertext = container[4+16+12:]

    key = derive_key_from_password(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


class EncryptStudioWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_lang = "de"
        self.db = EasySQL(DB_FILE)

        self.setWindowTitle(APP_TITLE)
        self.resize(900, 600)

        self._init_ui()
        self._apply_translations()


    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        self.label_title = QLabel(APP_NAME)
        self.label_title.setStyleSheet("font-size: 22px; font-weight: 600;")
        header_layout.addWidget(self.label_title, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        self.combo_language = QComboBox()
        self.combo_language.addItem("Deutsch", "de")
        self.combo_language.addItem("English", "en")
        self.combo_language.currentIndexChanged.connect(self.on_language_changed)

        header_layout.addWidget(self.combo_language, alignment=Qt.AlignRight)

        self.btn_github = QPushButton()
        self.btn_github.setCursor(Qt.PointingHandCursor)
        self.btn_github.clicked.connect(self.on_github_clicked)

        self.btn_info = QPushButton()
        self.btn_info.setCursor(Qt.PointingHandCursor)
        self.btn_info.clicked.connect(self.on_info_clicked)

        header_layout.addWidget(self.btn_github)
        header_layout.addWidget(self.btn_info)

        main_layout.addLayout(header_layout)

        pw_layout = QHBoxLayout()
        self.label_password = QLabel()
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.Password)
        pw_layout.addWidget(self.label_password)
        pw_layout.addWidget(self.edit_password)
        main_layout.addLayout(pw_layout)

        file_group = QGroupBox()
        self.file_group = file_group
        file_layout = QVBoxLayout(file_group)

        file_form = QFormLayout()
        self.label_file = QLabel()
        self.edit_file = QLineEdit()
        self.btn_browse = QPushButton()
        self.btn_browse.clicked.connect(self.on_browse_file)

        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.edit_file)
        file_path_layout.addWidget(self.btn_browse)

        file_form.addRow(self.label_file, file_path_layout)
        file_layout.addLayout(file_form)

        btn_file_layout = QHBoxLayout()
        self.btn_encrypt_file = QPushButton()
        self.btn_decrypt_file = QPushButton()
        self.btn_encrypt_file.clicked.connect(self.on_encrypt_file)
        self.btn_decrypt_file.clicked.connect(self.on_decrypt_file)
        btn_file_layout.addWidget(self.btn_encrypt_file)
        btn_file_layout.addWidget(self.btn_decrypt_file)
        file_layout.addLayout(btn_file_layout)

        main_layout.addWidget(file_group)

        text_group = QGroupBox()
        self.text_group = text_group
        text_layout = QVBoxLayout(text_group)

        self.label_plain_text = QLabel()
        self.text_plain = QTextEdit()
        self.text_plain.setPlaceholderText("")

        self.label_cipher_text = QLabel()
        self.text_cipher = QTextEdit()
        self.text_cipher.setPlaceholderText("")

        text_layout.addWidget(self.label_plain_text)
        text_layout.addWidget(self.text_plain)
        text_layout.addWidget(self.label_cipher_text)
        text_layout.addWidget(self.text_cipher)

        text_btn_layout = QHBoxLayout()
        self.btn_encrypt_text = QPushButton()
        self.btn_decrypt_text = QPushButton()
        self.btn_encrypt_text.clicked.connect(self.on_encrypt_text)
        self.btn_decrypt_text.clicked.connect(self.on_decrypt_text)
        text_btn_layout.addWidget(self.btn_encrypt_text)
        text_btn_layout.addWidget(self.btn_decrypt_text)
        text_layout.addLayout(text_btn_layout)

        main_layout.addWidget(text_group, stretch=1)

        status = QStatusBar()
        self.setStatusBar(status)
        self.status_label = QLabel()
        status.addWidget(self.status_label)
        self.status_label.setText("")


    def _apply_translations(self):
        t = TRANSLATIONS[self.current_lang]

        self.setWindowTitle(t["app_title"])
        self.label_password.setText(t["label_password"] + ":")
        self.label_file.setText(t["label_file"] + ":")

        self.file_group.setTitle(t["group_file_enc"])
        self.btn_browse.setText(t["btn_browse"])
        self.btn_encrypt_file.setText(t["btn_encrypt_file"])
        self.btn_decrypt_file.setText(t["btn_decrypt_file"])

        self.text_group.setTitle(t["group_text_enc"])
        self.label_plain_text.setText(t["label_plain_text"] + ":")
        self.label_cipher_text.setText(t["label_cipher_text"] + ":")

        self.btn_encrypt_text.setText(t["btn_encrypt_text"])
        self.btn_decrypt_text.setText(t["btn_decrypt_text"])

        self.btn_github.setText(t["github_button"])
        self.btn_info.setText(t["info_button"])

        self.status_label.setText(t["status_ready"])
        self.label_title.setText(APP_NAME)


    def on_language_changed(self, index: int):
        lang = self.combo_language.itemData(index)
        if lang in TRANSLATIONS:
            self.current_lang = lang
            self._apply_translations()

    def on_github_clicked(self):
        QDesktopServices.openUrl(QUrl(APP_GITHUB_URL))

    def on_info_clicked(self):
        t = TRANSLATIONS[self.current_lang]
        QMessageBox.information(self, t["info_title"], t["info_text"])

    def on_browse_file(self):
        t = TRANSLATIONS[self.current_lang]
        file_path, _ = QFileDialog.getOpenFileName(
            self, t["file_dialog_title"], "", "All Files (*.*)"
        )
        if file_path:
            self.edit_file.setText(file_path)


    def on_encrypt_file(self):
        t = TRANSLATIONS[self.current_lang]
        password = self.edit_password.text()
        if not password:
            QMessageBox.warning(self, t["msg_no_password_title"], t["msg_no_password_text"])
            return

        file_path = self.edit_file.text()
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.warning(self, t["msg_no_file_title"], t["msg_no_file_text"])
            return

        try:
            self.status_label.setText(t["status_encrypting"])
            QApplication.processEvents()

            with open(file_path, "rb") as f:
                data = f.read()

            container = encrypt_bytes(password, data)
            out_path = file_path + ".esec"
            with open(out_path, "wb") as f:
                f.write(container)

            self.db.log_operation("encrypt_file", file_path, "success", "File encrypted.")
            QMessageBox.information(
                self, t["msg_encrypt_success_title"], t["msg_encrypt_success_text"]
            )
            self.status_label.setText(t["status_done"])
        except Exception as e:
            self.db.log_operation("encrypt_file", file_path, "error", str(e))
            QMessageBox.critical(
                self, t["msg_encrypt_error_title"], str(e)
            )
            self.status_label.setText(t["status_ready"])

    def on_decrypt_file(self):
        t = TRANSLATIONS[self.current_lang]
        password = self.edit_password.text()
        if not password:
            QMessageBox.warning(self, t["msg_no_password_title"], t["msg_no_password_text"])
            return

        file_path = self.edit_file.text()
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.warning(self, t["msg_no_file_title"], t["msg_no_file_text"])
            return

        try:
            self.status_label.setText(t["status_decrypting"])
            QApplication.processEvents()

            with open(file_path, "rb") as f:
                container = f.read()

            plain = decrypt_bytes(password, container)

            if file_path.endswith(".esec"):
                out_path = file_path[:-5]
            else:
                out_path = file_path + ".dec"

            with open(out_path, "wb") as f:
                f.write(plain)

            self.db.log_operation("decrypt_file", file_path, "success", "File decrypted.")
            QMessageBox.information(
                self, t["msg_decrypt_success_title"], t["msg_decrypt_success_text"]
            )
            self.status_label.setText(t["status_done"])
        except Exception as e:
            self.db.log_operation("decrypt_file", file_path, "error", str(e))
            QMessageBox.critical(
                self, t["msg_decrypt_error_title"], str(e)
            )
            self.status_label.setText(t["status_ready"])


    def on_encrypt_text(self):
        t = TRANSLATIONS[self.current_lang]
        password = self.edit_password.text()
        if not password:
            QMessageBox.warning(self, t["msg_no_password_title"], t["msg_no_password_text"])
            return

        plain_text = self.text_plain.toPlainText()
        if not plain_text:
            return

        try:
            data = plain_text.encode("utf-8")
            container = encrypt_bytes(password, data)
            b64 = base64.b64encode(container).decode("ascii")
            self.text_cipher.setPlainText(b64)
            self.db.log_operation("encrypt_text", "-", "success", "Text encrypted.")
        except Exception as e:
            self.db.log_operation("encrypt_text", "-", "error", str(e))
            QMessageBox.critical(
                self, t["msg_text_encrypt_error_title"], str(e)
            )

    def on_decrypt_text(self):
        t = TRANSLATIONS[self.current_lang]
        password = self.edit_password.text()
        if not password:
            QMessageBox.warning(self, t["msg_no_password_title"], t["msg_no_password_text"])
            return

        cipher_b64 = self.text_cipher.toPlainText()
        if not cipher_b64:
            return

        try:
            container = base64.b64decode(cipher_b64)
            plain = decrypt_bytes(password, container)
            self.text_plain.setPlainText(plain.decode("utf-8", errors="replace"))
            self.db.log_operation("decrypt_text", "-", "success", "Text decrypted.")
        except Exception as e:
            self.db.log_operation("decrypt_text", "-", "error", str(e))
            QMessageBox.critical(
                self, t["msg_text_decrypt_error_title"], str(e)
            )


def main():
    app = QApplication(sys.argv)
    window = EncryptStudioWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()