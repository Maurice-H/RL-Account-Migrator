# RL-Account-Migrator

[![GitHub Release](https://img.shields.io/github/v/release/Maurice-H/RL-Account-Migrator)](https://github.com/Maurice-H/RL-Account-Migrator/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Issues](https://img.shields.io/github/issues/Maurice-H/RL-Account-Migrator)](https://github.com/Maurice-H/RL-Account-Migrator/issues)

## 📖 Overview

**RL-Account-Migrator** is a powerful tool designed to seamlessly migrate your Rocket League account settings and configurations between Steam and Epic Games accounts. 

### ✨ Features

- 💾 **Save Config Data** - Backup your Rocket League settings from Steam or Epic
- 🔄 **Transfer Settings** - Easily move your configuration between different accounts
- ⏭️ **Skip Intro** - Bypass the intro sequence and tutorial match on new accounts
- 🎮 **Preserve Settings** - Keep all your personal preferences including:
  - Keybindings
  - Camera settings
  - Video settings
  - Audio preferences
  - And more!

Perfect for players who want to maintain consistent settings across multiple launchers without the hassle of manual configuration.

---

## 🚀 Quick Start

### For Users

1. Download the latest release from the [Releases page](https://github.com/Maurice-H/RL-Account-Migrator/releases)
2. Run the executable
3. Follow the on-screen instructions to backup or migrate your settings

### For Developers

If you want to build or modify the project:

1. **Clone the repository**
   ```bash
   git clone https://github.com/Maurice-H/RL-Account-Migrator.git
   cd RL-Account-Migrator
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   pip install poetry
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```
   This will create a virtual environment (if it doesn't exist) and install all required dependencies.

4. **Run the application**
   ```bash
   poetry run python src/main.py
   ```
   Or activate the virtual environment manually:
   ```bash
   # Windows
   .venv\Scripts\activate
   python src/main.py
   
   # Linux/macOS
   source .venv/bin/activate
   python src/main.py
   ```

5. **Build executable**
   ```bash
   poetry run pyinstaller RLAccountMigrator.spec
   ```
   The compiled executable will be available in the `dist/` folder.

#### Requirements
- Python 3.12 or 3.13
- Poetry for dependency management
- Dependencies are managed via `pyproject.toml`:
  - PySide6 (GUI framework)
  - psutil (Process utilities)
  - PyInstaller (for building executables)

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can get involved:

### 🐛 Report Bugs or Request Features

Open an [Issue](https://github.com/Maurice-H/RL-Account-Migrator/issues) with a clear description of:
- The problem you're experiencing
- Steps to reproduce (for bugs)
- Your suggested enhancement (for features)

### 💻 Submit Pull Requests

1. Fork the repository
2. Create a new branch for your feature/fix
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes with clear, descriptive commit messages
4. Submit a Pull Request against the `main` branch

### 💬 Join Discussions

Participate in [GitHub Discussions](https://github.com/Maurice-H/RL-Account-Migrator/discussions) to:
- Share ideas
- Get help with the tool
- Connect with other users

### 📧 Direct Contact

Reach out via Discord: **maizu_u**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Support

If you find this tool helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🔀 Contributing code

---

**Note:** For more detailed contribution guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md)
