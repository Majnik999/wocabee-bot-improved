## Disclaimer

**This project is for educational purposes only. I am not responsible for any consequences resulting from the use of this tool, including but not limited to account suspension or angry teachers.**

# WocaBot - Multi-purpose Bot for Wocabee

WocaBot is an automated tool designed to help you manage and complete tasks on the Wocabee platform. It uses Selenium to interact with the web interface and can automate practice sessions, vocabulary learning, and points gathering.

## Features

- **Practice Mode**: Automatically completes practice sessions to gain points.
- **Points Gathering**: Target a specific number of points (e.g., +1000).
- **Save & Quit Automation**: Ensures progress is saved and exits practice sessions properly.
- **Headless Mode**: Run the bot in the background without a browser window.
- **Account Management**: Save and use multiple accounts easily.
- **Vocabulary Learning**: Automatically handles new words and builds a local dictionary (`dict.json`).

## Installation

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- Google Chrome installed

### Setup

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Install the required dependencies:

```bash
pip install selenium webdriver-manager colorama
```

## Usage

The bot is controlled via command-line arguments. The main entry point is `main.py`.

### Basic Commands

- **List classes**:
  ```bash
  python main.py --classes
  ```
- **List packages in a class**:
  ```bash
  python main.py --class <class_index>/<class_name> --get-packages
  ```
- **Start practice to gain points**:
  ```bash
  python main.py --class <class_index>/<class_name> --package <package_index>/<package_name> --practice --points 500
  ```
- **Complete a specific package**:
  ```bash
  python main.py --class <class_index>/<class_name> --package <package_index>/<package_name> --do-package
  ```
- **Run in headless mode (no window)**:
  ```bash
  python main.py --class <class_index>/<class_name> --package <package_index>/<package_name> --practice --points 500 --hide
  ```
- **Use a specific saved account**:
  ```bash
  python main.py --class <class_index>/<class_name> --package <package_index>/<package_name> --account <account_index> (saved after first login) --practice --points 500
  ```

### All Command-Line Arguments

| Argument | Description |
| :--- | :--- |
| `--practice` | Start practice mode to gather points. |
| `--points <N>` | Target points to reach (e.g., `500` or `1000`). |
| `--class <ID>` | Specify the class index (starting from 0). |
| `--package <ID>` | Specify the package index or name. |
| `--do-package` | Start completing the specified package. |
| `--get-classes` | List all available classes. |
| `--get-packages` | List all packages in the selected class. |
| `--leaderboard` | Show the current class leaderboard. |
| `--hide` | Run the browser in headless mode. |
| `--account <ID>` | Use a saved account from `credentials.json` or login with a new one. |
| `--auto` | Run in automatic mode. |

## Configuration

- **`credentials.json`**: Stores your login information. If it doesn't exist, the bot will ask for your credentials on the first run.
- **`dict.json`**: A local database of translated words. The bot populates this as it learns.

## Important Notes

- **Safety**: Do not use the bot excessively to avoid detection or account issues.
