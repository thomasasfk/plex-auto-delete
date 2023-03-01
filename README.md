# plex-auto-delete  [![Python Test and Lint](https://github.com/thomasasfk/plex-auto-delete/actions/workflows/pytest-and-lint.yml/badge.svg)](https://github.com/thomasasfk/plex-auto-delete/actions/workflows/pytest-and-lint.yml)

Ah, the joys of managing a Plex server! It's like herding cats, but instead of cats, it's a bunch of lazy humans who can't be bothered to clean up after themselves.

Introducing "plex-auto-delete" (because apparently hitting the shift key to capitalize letters is too much effort for some people). This magical piece of software will take care of the dirty work for you, because let's face it, we can't rely on our users to do it themselves.

Say goodbye to the days of begging and pleading with people to clean up their files. With "plex-auto-delete", you won't even have to lift a finger! And hey, who needs free space on their server, am I right? Let's just keep hoarding all of our old, unused files like they're precious treasures.

But seriously, folks, let's give a round of applause to all the lazy users out there who just can't seem to hit the delete button. You're the reason why we had to create this project in the first place. Thanks for nothing!


## Installation

To run this project, you will need to have Python 3.9.2 installed on your system. If you do not have Python 3.9.2 installed, please follow the instructions to install it from the Python website.

It is recommended that you use a virtual environment to manage the project's dependencies. To create a virtual environment, run the following command:

```bash
python -m venv myenv
```

Replace myenv with the name you want to give your virtual environment.

Once your virtual environment is created, activate it using the following command:

```bash
source myenv/bin/activate
```

Once your virtual environment is activated, install the project's dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Running

Set the following environment variables:

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
0 0 * * * cd  ~/path/to/plex-auto-delete && .venv/bin/python main.py
````

## Installing pre-commit hooks
This project uses pre-commit hooks to ensure that the code meets certain standards before committing it. To install the pre-commit hooks, activate your virtual environment and run the following command:

```bash
pre-commit install
```

This will install the pre-commit hooks and set them up to run automatically before each commit. If any issues are found, pre-commit will prevent the commit from going through until the issues are resolved.
