# plex-auto-delete  [![Python Lint](https://github.com/thomasasfk/plex-auto-delete/actions/workflows/pytest-and-lint.yml/badge.svg?branch=main)](https://github.com/thomasasfk/plex-auto-delete/actions/workflows/pytest-and-lint.yml)

## Installation

To run this project, you will need to have Python 3.9.2 installed on your system. If you do not have Python 3.9.2 installed, please follow the instructions to install it from the Python website.

It is recommended that you use a virtual environment to manage the project's dependencies. To create a virtual environment, run the following command:

```bash
python -m venv .venv
```

Replace myenv with the name you want to give your virtual environment.

Once your virtual environment is created, activate it using the following command:

```bash
source .venv/bin/activate
```

Once your virtual environment is activated, install the project's dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Running

Copy the `.env` file & fill in the variables:

```bash
cp .env.example .env
```

```bash
DAYS_SINCE_TOUCHED=
PLEX_URL=
PLEX_TOKEN=
RU_TORRENT_RPC_URL=
```

You can run the script using the following command:

```bash
python main.py
```

Or run on a cronjob:
```bash
0 0 * * * cd  ~/path/to/plex-auto-delete && .venv/bin/python main.py >> log.txt 2>&1
````

## Installing pre-commit hooks
This project uses pre-commit hooks to ensure that the code meets certain standards before committing it. To install the pre-commit hooks, activate your virtual environment and run the following command:

```bash
pre-commit install
```

This will install the pre-commit hooks and set them up to run automatically before each commit. If any issues are found, pre-commit will prevent the commit from going through until the issues are resolved.
