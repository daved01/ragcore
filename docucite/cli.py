import argparse
from docucite.constants import AppConstants
from docucite.app.app import DocuCiteApp


def _parse_args() -> dict[str, str]:
    parser = argparse.ArgumentParser(description="Docucite")
    parser.add_argument("--config", type=str, help="Path to the config file")
    args = parser.parse_args()
    return {AppConstants.KEY_CONFIGURATION_PATH: args.config}


if __name__ == "__main__":
    arguments: dict[str, str] = _parse_args()
    app = DocuCiteApp(config_path=arguments.get(AppConstants.KEY_CONFIGURATION_PATH))
    app.run()
