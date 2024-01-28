import argparse
from typing import Optional

from ragcore.shared.constants import AppConstants
from ragcore.app.app import RAGCore


SEPARATOR_LINE = "--" * 64
LOGGER_LEVEL_DEBUG = "DEBUG"
LOGGER_LEVEL_WARN = "WARN"


def run_app(app) -> None:
    """Event loop for cli app."""

    while True:
        user_input = input(
            "\nEnter:\n(n/N) add new document\n(d/D) delete a document\n(q/Q) exit\nor a question to run a search:\n"
        )
        if user_input.lower() == "q":
            print("Exiting ...")
            break
        if user_input.lower() == "n":
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


def entrypoint():
    arguments: dict[str, str] = _parse_args()
    cli_app = RAGCore(
        config_path=arguments.get(AppConstants.KEY_CONFIGURATION_PATH),
        log_level=LOGGER_LEVEL_DEBUG
        if arguments.get(AppConstants.KEY_LOGGER_FLAG)
        else LOGGER_LEVEL_WARN,
    )
    run_app(cli_app)


def _parse_args() -> dict[str, str]:
    parser = argparse.ArgumentParser(
        description="RAG Core Kit is a library which helps you to create Retrieval Augmentations applications."
    )
    parser.add_argument("--config", type=str, help="Path to the config file")
    parser.add_argument("-v", action="store_true", help="Verbose logger")
    args = parser.parse_args()
    return {
        AppConstants.KEY_CONFIGURATION_PATH: args.config,
        AppConstants.KEY_LOGGER_FLAG: args.v,
    }


if __name__ == "__main__":
    entrypoint()
