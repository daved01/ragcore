import argparse

from ragcore.shared.constants import AppConstants
from ragcore.app import RAGCore
from ragcore.models.app_model import QueryResponse


SEPARATOR_LINE = "--" * 64
LOGGER_LEVEL_DEBUG = "DEBUG"
LOGGER_LEVEL_WARN = "WARN"


def run_app(app) -> None:
    """Event loop for cli app."""

    while True:
        user_input = input(
            "\nEnter:\n(a/A) add new document\n(d/D) delete a document\n(l/L) list all titles\n(q/Q) exit\nor a question to run a search:\n"
        )
        if user_input.lower() == "q":
            print("Exiting ...")
            break
        if user_input.lower() == "a":
            path = input("Enter relative path to new document: ")
            app.add(path=path)
            print("Added documents!")
        elif user_input.lower() == "d":
            title = input("Enter title to remove from database: ")
            app.delete(title=title)
            print("Deleted documents!")
        elif user_input.lower() == "l":
            titles = app.get_titles()
            print(f"Following titles are in database: {titles.contents}")
        else:
            response: QueryResponse = app.query(query=user_input)
            if not response.content:
                continue
            print(f"\n{SEPARATOR_LINE}\n{response.content}\n{SEPARATOR_LINE}\n")


def entrypoint():
    arguments: dict[str, str] = _parse_args()
    cli_app = RAGCore(
        config=arguments.get(AppConstants.KEY_CONFIGURATION_PATH),
        log_level=(
            LOGGER_LEVEL_DEBUG
            if arguments.get(AppConstants.KEY_LOGGER_FLAG)
            else LOGGER_LEVEL_WARN
        ),
    )
    run_app(cli_app)


def _parse_args() -> dict[str, str]:
    parser = argparse.ArgumentParser(
        description=(
            "RAG Core is a library which helps you to create Retrieval-Augmented Generation applications. Create a `config.yaml` "
            "file to get started. For more information see: https://daved01.github.io/ragcore/"
        )
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
