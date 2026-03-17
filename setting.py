import json

with open("config.json", "r") as f:
    config = json.load(f)

GeminiKey = config['GeminiKey']
GeminiModel = config['GeminiModel']
DataFolderPath = config['DataFolderPath']
