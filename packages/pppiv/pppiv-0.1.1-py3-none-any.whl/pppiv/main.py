import json
from pathlib import Path

import click
from poetry.factory import Factory
from poetry.utils.env import EnvManager

TARGET_COMMANDS = {
    "python.pythonPath": "python",
    "python.jediPath": "jedi",
    "python.dataScience.ptvsdDistPath": "ptvsd",
    "python.formatting.blackPath": "black",
    "python.formatting.autopep8Path": "autopep8",
    "python.formatting.yapfPath": "yapf",
    "python.linting.banditPath": "bandit",
    "python.linting.flake8Path": "flake8",
    "python.linting.mypyPath": "mypy",
    "python.linting.prospectorPath": "prospector",
    "python.linting.pycodestylePath": "pycodestyle",
    "python.linting.pylamaPath": "pylama",
    "python.linting.pydocstylePath": "pycodestyle",
    "python.linting.pylintPath": "pylint",
    "python.sortImports.path": "isort",
    "python.testing.nosetestPath": "nosetest",
}


@click.command()
def main() -> None:
    poetry = Factory().create_poetry(Path.cwd())
    env_manager = EnvManager(poetry)

    settings = {}
    settings[f"python.pythonPath"] = env_manager.get().python
    for key, command in TARGET_COMMANDS.items():
        command_path = env_manager.get().path / "bin" / command
        if command_path.exists():
            settings[key] = str(command_path)
    settings_json_str = json.dumps(settings, indent=4)

    dot_vscode_path = poetry.file.path.parent / ".vscode"
    dot_vscode_path.mkdir(exist_ok=True)

    setting_json_path = dot_vscode_path / "settings.json"
    setting_json_path.write_text(settings_json_str)

    click.echo(settings_json_str)
