# Phish-Kit

**Python-Based Phishing Simulation Framework for Authorized Security Testing**

Phish-Kit is a cybersecurity project intended for phishing simulation, security awareness training, and controlled penetration-testing labs.

## Features

- Command-line interface
- Configurable application settings
- Template selection
- Modular Python architecture
- Automated setup through `setup.sh`
- Dedicated output directory

## Technology Stack

- Python 3
- Flask
- Colorama
- Requests
- Pyngrok
- Cloudflare Python package

See `requirements.txt` for the declared Python dependencies.

## Project Structure

```text
phish-kit/
├── modules/
├── output/
├── templates/
├── config.json
├── phishkit.py
├── requirements.txt
├── setup.sh
└── README.md
```

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/geo-hotzz/phish-kit.git
```

### Step 2: Navigate to the Project Directory

```bash
cd phish-kit
```

### Step 3: Make the Setup Script Executable

```bash
chmod +x setup.sh
```

### Step 4: Run the Setup Script

```bash
./setup.sh
```

Alternatively, run it through Bash:

```bash
bash setup.sh
```

Review the script before execution to understand the commands it performs and whether it requires elevated privileges.

### Step 5: Verify Python Dependencies

If the setup script does not install the dependencies, run:

```bash
python3 -m pip install -r requirements.txt
```

For a cleaner installation, use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Step 6: Review the Configuration

Inspect the application configuration:

```bash
cat config.json
```

Verify the configured port and other settings before launching the application.

## Usage

### View Available Arguments

```bash
python3 phishkit.py --help
```

The application defines the following command-line options:

| Argument | Purpose |
|---|---|
| `-c`, `--config` | Specify a configuration file |
| `-t`, `--template` | Select a template |
| `-p`, `--port` | Set the server port |

### Start the Application

```bash
python3 phishkit.py
```

Use the options supported by the application when configuring an authorized test environment.

## Configuration

The `config.json` file stores application settings.

Before running the project:

- Verify the configured server port.
- Review the template configuration.
- Understand where generated output is stored.
- Never commit credentials, API keys, or other secrets.

## Troubleshooting

### Setup Script Permission Error

```bash
chmod +x setup.sh
./setup.sh
```

### Check Python Installation

```bash
python3 --version
python3 -m pip --version
```

### Dependency Installation Issues

```bash
python3 -m pip install -r requirements.txt
```

If installation fails, review the error output and resolve dependency conflicts before proceeding.

## Security and Legal Disclaimer

Phish-Kit is intended for authorized cybersecurity testing, educational demonstrations, and controlled lab environments.

- Obtain explicit authorization before testing any system or user.
- Use test accounts and systems you control.
- Do not collect real credentials or session tokens.
- Avoid exposing the application to the public internet without an appropriate security review.
- Follow applicable laws and responsible disclosure practices.

The user is responsible for ensuring that all use of this project is authorized and lawful.

## Contributing

Contributions that improve documentation, code quality, security, and educational value are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Test your changes in an isolated environment.
4. Submit a pull request with a clear description.

## Repository

GitHub: https://github.com/geo-hotzz/phish-kit
