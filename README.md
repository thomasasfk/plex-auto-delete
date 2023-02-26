# plex-auto-delete

[![Python Test and Lint](https://github.com/thomasasfk/plex-auto-delete/actions/workflows/pytest-and-lint.yml/badge.svg)](https://github.com/thomasasfk/plex-auto-delete/actions/workflows/pytest-and-lint.yml)

## Installation

To run this project, you will need to have Python 3.9.2 installed on your system. If you do not have Python 3.9.2 installed, please follow the instructions to install it from the Python website.

It is recommended that you use a virtual environment to manage the project's dependencies. To create a virtual environment, run the following command:

```bash
python -m venv myenv
```

Replace myenv with the name you want to give your virtual environment. Once your virtual environment is created, activate it using the following command depending on your operating system:

### On Windows

```bash
source myenv/bin/activate
```

### On Unix or Linux

```bash
source myenv/bin/activate
```

Once your virtual environment is activated, install the project's dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Running

You can run the script using the following command:

```bash
python main.py --url <PLEX_URL> --token <PLEX_TOKEN> --days <DAYS_TO_KEEP>
```

## Tests

To run tests for the project, simply run:

```bash
pytest
```

## Installing pre-commit hooks
This project uses pre-commit hooks to ensure that the code meets certain standards before committing it. To install the pre-commit hooks, activate your virtual environment and run the following command:

```bash
pre-commit install
```

This will install the pre-commit hooks and set them up to run automatically before each commit. If any issues are found, pre-commit will prevent the commit from going through until the issues are resolved.
