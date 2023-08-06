from . import core


__version__ = '0.0.3'


def load_workbook(url, credentials):
    """Load a Google Sheet workbook.

        Args:
            url: Google Sheet URL (key will be supported in future release)
            credentials: Service Account JSON credentials created for the Google Sheet. Can be path, dict or JSON str.

        Returns:
            :class:`core.Workbook`
    """
    return core.Workbook(url, credentials)


def create_workbook(url, credentials):
    pass  # TODO
