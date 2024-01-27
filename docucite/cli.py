import argparse
from typing import Optional

from docucite.shared.constants import AppConstants
from docucite.app.app import DocuCiteApp


SEPARATOR_LINE = "--" * 64


def run_app(app) -> None:
    """Event loop for cli app."""

    while True:
        user_input = input(
            "\nEnter:\n(n/N) add new document\n(d/D) delete a document\n(q/Q) exit\nor a question to run a search:\n"
        )
        if user_input.lower() == "q":
            print("Exiting ...")
            break
        elif user_input.lower() == "n":
            path = input("Enter relative path to new document: ")
            app.add(path=path)

        elif user_input.lower() == "d":
            title = input("Enter title to remove from database: ")
            app.delete(title=title)
        else:
            response: Optional[str] = app.query(query=user_input)
            if not response:
                continue
            print(f"\n{SEPARATOR_LINE}\n{response}\n{SEPARATOR_LINE}\n")


def _parse_args() -> dict[str, str]:
    parser = argparse.ArgumentParser(description="Docucite")
    parser.add_argument("--config", type=str, help="Path to the config file")
    args = parser.parse_args()
    return {AppConstants.KEY_CONFIGURATION_PATH: args.config}


if __name__ == "__main__":
    arguments: dict[str, str] = _parse_args()
    app = DocuCiteApp(config_path=arguments.get(AppConstants.KEY_CONFIGURATION_PATH))
    run_app(app)
