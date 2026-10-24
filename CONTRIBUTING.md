# Contributing to BookVault

Thank you for your interest in contributing to **BookVault**! We welcome contributions from developers of all skill levels. Whether you're fixing a bug, adding new features, improving documentation, or styling templates, your help is appreciated.

---

## 🛠️ Code of Conduct

Please be respectful and constructive in all discussions, pull requests, and issues. We aim to foster an open, welcoming, and productive environment.

---

## 🚀 How to Contribute

### 1. Fork & Clone
1. Fork the repository on GitHub: [https://github.com/AshrajSingh/BookVault](https://github.com/AshrajSingh/BookVault)
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/BookVault.git
   cd BookVault
   ```

### 2. Set Up Development Environment
1. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows (Command Prompt / PowerShell):
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Navigate to the project directory and run migrations:
   ```bash
   cd bookVault
   python manage.py migrate
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

### 3. Create a Feature Branch
Always create a branch for your specific work:
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/issue-description
```

### 4. Making Changes
- Follow standard Python PEP 8 conventions.
- Maintain existing Django design patterns and naming conventions.
- If you add or alter models, create and commit corresponding migrations:
  ```bash
  python manage.py makemigrations
  ```
- Keep CSS clean and scoped to respective templates.

### 5. Submit a Pull Request
1. Commit your changes with descriptive messages:
   ```bash
   git add .
   git commit -m "feat: add search filter to student dashboard"
   ```
2. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Open a Pull Request on the main repository describing:
   - What changed
   - Motivation and context
   - Steps to test the change
   - Any screenshots (if UI changes were made)

---

## 🐛 Reporting Bugs & Suggesting Features

If you encounter bugs or have ideas for new features, please open an issue on GitHub:
- **[Bug Report](https://github.com/AshrajSingh/BookVault/issues/new?template=bug_report.md)**: Include detailed steps to reproduce, expected vs actual behavior, and error tracebacks.
- **[Feature Request](https://github.com/AshrajSingh/BookVault/issues/new?template=feature_request.md)**: Describe the problem your feature solves and proposed implementation ideas.

---

Thank you for helping make **BookVault** better! 📚✨
