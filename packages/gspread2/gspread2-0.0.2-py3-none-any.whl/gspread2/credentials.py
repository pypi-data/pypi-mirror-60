import json
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def authorize(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = json.load(f)
    elif isinstance(file_path, str):
        data = json.loads(file_path)
    elif isinstance(file_path, dict):
        pass
    else:
        raise AttributeError('Invalid input')
    creds = ServiceAccountCredentials.from_json_keyfile_dict(data, ['https://spreadsheets.google.com/feeds',
                                                                    'https://www.googleapis.com/auth/drive'])
    return gspread.authorize(creds)
