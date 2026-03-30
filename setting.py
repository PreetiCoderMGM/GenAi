import json
import os

with open("config.json", "r") as f:
    config = json.load(f)

GeminiKey = config['GeminiKey']
GeminiModel = config['GeminiModel']
DataFolderPath = config['DataFolderPath']


chat_db_file_path = os.path.join(os.getcwd(), "DB", "chat.json")
user_db_file_path = os.path.join(os.getcwd(), "DB", "user.json")
files_db_file_path = os.path.join(os.getcwd(), "DB", "files.json")
if not os.path.isfile(files_db_file_path):
    open(files_db_file_path, "w").close()
