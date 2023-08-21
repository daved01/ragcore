import pytest


class BaseTest:
    @pytest.fixture
    def mock_logger(self, mocker):
        mock_logger = mocker.patch("logging.getLogger")
        mock_logger_instance = mock_logger.return_value
        mock_logger_instance.info = mocker.MagicMock()
        return mock_logger_instance
