> ### Encrypt Studio v1.0.0  
  - **BYLICKILABS – Intelligence Systems & Communications**  

| <img width="1280" height="640" alt="Encrypt" src="https://github.com/user-attachments/assets/2423efd4-851a-4937-9a77-0c16c338d281" /> |
|---|

---

## 🔐 About Encrypt Studio  
> Encrypt Studio is a fully local encryption toolkit designed to securely process files and text.  
  - Version **1.0.0** provides a modern feature set, strong security architecture, and an intuitive user experience.
    - All operations run **offline**, without cloud connections or external data transmission.

---

## 🚀 Key Features

### ✔ File Encryption  
- AES‑256‑GCM encryption  
- Automatic `.esec` secure container  
- Password‑based key derivation (PBKDF2)

### ✔ Text Encryption  
- Plain text → Base64 encrypted text  
- Secure decryption using password

### ✔ Language Selection (EN/DE)  
- Live switching between English and German  
- Fully translated interface

### ✔ EasySQL Logging  
- Local SQLite event logging  
- Logs: action, target, status, timestamp  
- No data transmitted externally

### ✔ GitHub Integration  
- Button directly opens the repository

### ✔ Info Dialog  
- Version information  
- Company details  
- Security architecture (AES‑GCM, PBKDF2)

---

## 🛡 Security & Architecture

### 🔑 Key-Derivation (PBKDF2)
- SHA‑256  
- 200,000 iterations  
- 32‑byte key

### 🔰 Container Format (.esec)  
Includes:  
- Magic header  
- Salt  
- Nonce  
- Ciphertext + authentication tag  

### 🔒 Data Handling  
- Fully local  
- No cloud services  
- No telemetry  

---

## 🗂 Technology Stack  
- **Python 3.10+**  
- **PySide6** (UI)  
- **cryptography** (AES‑GCM)  
- **SQLite (EasySQL)**  

---

## 📌 Installation

### Requirements  
```
pip install -r requirements.txt
```

### Start
```
python app.py
```

---

## © BYLICKILABS – Intelligence Systems & Communications  
All rights reserved.
[LICENSE](LICENSE)
