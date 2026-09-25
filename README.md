# My Repository

This repository contains three main modules: **Data Pipeline**, **Analytics**, and **Support Assistant**. Each module is designed to handle specific tasks and can be executed independently. Below are the details for setting up and running each module, as well as some design decisions made during the development of this project.

## Project Structure

```
my-repository
├── README.md
├── data_pipeline
│   ├── README.md
│   ├── src
│   ├── tests
│   └── requirements.txt
├── analytics
│   ├── README.md
│   ├── src
│   ├── tests
│   └── requirements.txt
├── support_assistant
│   ├── README.md
│   ├── src
│   ├── tests
│   └── requirements.txt
└── .gitignore
```

## Setup Instructions

1. **Clone the Repository**
   ```
  git clone https://github.com/vivekreddy1994/capstone_project.git
  cd capstone_project
   ```

2. **Install Dependencies**
   Each module has its own `requirements.txt` file. Navigate to each module's directory and install the required packages using pip:
   ```
  python -m pip install --upgrade pip
  python -m pip install pandas pytest
   cd data_pipeline
  python -m pip install -r requirements.txt
   cd ../analytics
  python -m pip install -r requirements.txt
   cd ../support_assistant
  python -m pip install -r requirements.txt
   ```
  `pandas` is used by the data and analytics pipelines, and `pytest` runs the repository test suite. SQLite is included with Python and does not need a pip package.

3. **Verify Git and Python Tools**
  Run these commands from the repository root:
  ```powershell
  git --version
  python --version
  python -m pytest --version
  ```
  If `git` is not recognized on Windows, install Git for Windows, reopen VS Code, and run the commands again.

4. **Run Tests**
  ```powershell
  python -m pytest data_pipeline/tests support_assistant/tests analytics/tests
  ```

5. **Demonstrate the Required Branch Workflow**
  These commands create a feature branch, make two commits, and merge it back into `main`:
  ```powershell
  git switch main
  git pull --ff-only origin main
  git switch -c feature/capstone-validation
  git add README.md
  git commit -m "Document capstone setup and validation"
  git add .
  git commit -m "Complete capstone implementation updates"
  git switch main
  git merge --no-ff feature/capstone-validation -m "Merge capstone validation feature"
  git push origin main
  git log --graph --oneline --decorate --all
  ```

## Module Execution Guidelines

### Data Pipeline
- From the repository root, run the scraper, cleaner, and SQLite loader using:
  ```
  python -m data_pipeline.main
  ```
  The default run writes `books.db` and uses Books to Scrape as its free public source.

### Analytics
- From the repository root, run the analytics ingestion path using:
  ```
  python -m analytics.src.main
  ```
  The pipeline writes cleaned output to `processed_books.csv`.

### Support Assistant
- From the repository root, start the policy support CLI using:
  ```
  python -m support_assistant.src.assistant
  ```

## Design Decisions

- **Modular Structure**: Each module is separated into its own directory to promote clean organization and maintainability.
- **Testing**: Each module includes a `tests` directory with unit tests to ensure functionality and reliability.
- **Configuration Management**: Configuration settings are centralized in `config.py` files within the respective modules to simplify adjustments and environment management.
- **Documentation**: Each module contains its own `README.md` file to provide specific instructions and details relevant to that module.

The modules are linked by one data lifecycle: the data pipeline produces a relational source for analysts, the analytics module cleans and profiles structured records, and the support assistant exposes deterministic policy responses behind a small service boundary. Each module keeps its own `requirements.txt`; SQLite is provided by Python and is not installed from pip.

This project aims to provide a comprehensive solution for data processing, analytics, and user support, with a focus on modularity and ease of use.