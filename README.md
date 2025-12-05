# 🔍 Pathfinder - SFTP Remote File Finder

A modern GUI application for searching files on remote SFTP servers using Python and Tkinter.

## ✨ Features

- 🌐 **SFTP Connection**: Connect to remote servers via SSH/SFTP
- 🔎 **Dual Search Modes**:
  - **Filename Search**: Find files by name using `find` command
  - **Content Search**: Search file contents using `grep` command
- 💾 **Profile Management**: Save and load connection profiles for quick access
- 🌍 **Bilingual Support**: English and Traditional Chinese (繁體中文)
- 🎨 **Modern UI**: Windows 11 inspired interface with Tkinter
- 🔐 **Secure**: Base64 encoded password storage (local configuration only)

## 📋 Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## 🚀 Installation

1. **Clone or download the project**
    ```bash
    cd c:\Users\ykswo\Downloads\Test\Pathfinder
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application**
    ```bash
    python Pathfinder.py
    ```

## 📦 Dependencies

- **paramiko** (≥4.0.0) - SSH/SFTP client library
- **tkinter** - GUI framework (included with Python)

## 🎯 Usage

### Connection Setup
1. Enter the remote host IP address
2. Specify SSH port (default: 22)
3. Enter username and password
4. (Optional) Check "Save Connection Info" to store credentials locally

### Search Options
1. **Start Path**: Remote directory to search in (default: `.`)
2. **Keyword**: Filename or content to search for
3. **Mode Selection**:
   - **Filename**: Search for files matching the keyword
   - **Content**: Search within file contents (slower)

### Quick Connect
- Use the "Select Profile" dropdown to quickly load previously saved connections
- Click "Delete Profile" to remove saved credentials

## 🔧 File Structure

```plaintext
Pathfinder/
│
├───icons/                   # Application icons
│       ├── icon.png
│       └── ...
│
├───locales/                 # Translation files
│       ├── en_US.po
│       ├── zh_TW.po
│       └── ...
│
├───src/                     # Source files
│       ├── __init__.py
│       ├── main.py
│       ├── sftp_client.py
│       ├── file_search.py
│       ├── profile_manager.py
│       └── ...
│
├───tests/                   # Unit tests
│       ├── __init__.py
│       ├── test_sftp_client.py
│       ├── test_file_search.py
│       ├── test_profile_manager.py
│       └── ...
│
├───requirements.txt         # Python dependencies
├───README.md                # Project documentation
└───LICENSE                  # License information
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for a powerful, user-friendly SFTP client
- Built with passion and dedication to open-source software

## 📫 Contact

- **Author**: Your Name
- **Email**: yourname@example.com
- **GitHub**: [yourgithub](https://github.com/yourgithub)
