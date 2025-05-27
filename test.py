from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Укажите путь к вашему JSON-файлу с ключами
SERVICE_ACCOUNT_FILE = 'swift-shore-451020-s8-deacce47d549.json'

# ID вашей таблицы (из URL)
SAMPLE_SPREADSHEET_ID = '13IwxghlX08DIKfZFesYAtI-ceFNdScvAPxMMN-O5itk'

# Авторизация
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', credentials=creds)

# Данные для записи
values = [
    ['Hello world']
]
body = {
    'values': values
}

# Запись в таблицу
result = service.spreadsheets().values().update(
    spreadsheetId=SAMPLE_SPREADSHEET_ID,
    range='A1',
    valueInputOption='RAW',
    body=body
).execute()

print(f"{result.get('updatedCells')} cells updated.")