from . import core


def load_workbook(url, credentials):
    return core.Workbook(url, credentials)
