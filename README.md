# Discord Bot

![Ojos Project logo header](./res/vlogo.png)

This Discord bot is for the Ojos Project to organize ourselves.

## Developer Guide

### Dependencies

This project uses `pipenv` to manage our dependencies. Please install and it and
the `Pipfile` dependencies by using:

```shell
pip install pipenv
pipenv install

# activates dev environment
pipenv shell
```

Whenever you're finished with programming, run `exit` to deactivate the dev
environment subprocess.

### Discord Token

Then, get a Discord token from the
[developer portal](https://discord.com/developers). With that token, run this
command:

```shell
echo 'DISCORD_TOKEN="<DISCORD TOKEN FROM WEBSITE>"' >> .env
```

### Starting the bot

You can start the bot by running:

```shell
pipenv run start
```

### Running Tests

We use `pytest` and `coverage` to test this module. To properly test it, use:

```shell
coverage run -m pytest; coverage xml
```

This creates two files: `.coverage` and `coverage.xml`. Use the
[Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters)
extension to see if the tests ran, and the coverage it's covered. Read more with
the Coverage Gutters documentation.
