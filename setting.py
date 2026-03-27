import json
import os

with open("config.json", "r") as f:
    config = json.load(f)

GeminiKey = config['GeminiKey']
GeminiModel = config['GeminiModel']
DataFolderPath = config['DataFolderPath']


chat_db_file_path = os.path.join(os.getcwd(), "DB", "chat.json")
user_db_file_path = os.path.join(os.getcwd(), "DB", "user.json")
