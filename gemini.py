import google.genai as genai
from google.genai import types
import csv
import os
import json
import time
import setting

# Initialize client
client = genai.Client(api_key=setting.GeminiKey)

system_prompt = (
    "Analyze the provided data carefully. "
    "You are allowed to perform calculations such as counting, averaging, and comparisons "
    "based strictly on the information present in the data. "
    "Do not use any external knowledge. "
    "If the data is completely missing required information, then say: No relevant data found."
)


# read txt file
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# read csv file
def read_csv(file_path):
    content = ""
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for key, value in row.items():
                content += f"{key}: {value}\n"
            content += "\n"
    return content


# read json file
def read_json(file_path):
    content = ""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

        # If JSON is a list (most common case)
        if isinstance(data, list):
            for row in data:
                for key, value in row.items():
                    content += f"{key}: {value}\n"
                content += "\n"

        # If JSON is a dictionary
        elif isinstance(data, dict):
            for key, value in data.items():
                content += f"{key}: {value}\n"

    return content


def file_summary(file_path: str, que: str):
    try:
        file_content = ""
        if file_path.endswith(".txt"):
            file_content = read_txt(file_path)

        elif file_path.endswith(".csv"):
            file_content = read_csv(file_path)

        elif file_path.endswith(".json"):
            file_content = read_json(file_path)
        if not file_content:
            return f"Content not found in file: {os.path.basename(file_path)}"
        prompt = f"From the given file content answer the question: {que}\n\nfile content:\n\n{file_content}"

        response = client.models.generate_content(
            model=setting.GeminiModel, contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=1000, temperature=0.2,
                                               system_instruction=system_prompt))
        answer = response.text.strip()
        return answer
    except Exception as ex:
        print(f"Could not get summary from filepath: {file_path}, ex:\n {ex}")
        return f"Content not generate summary from file: {os.path.basename(file_path)}"


#  Read each file separately
def query_llm(question):
    try:
        data_folder = setting.DataFolderPath
        combined_res = ""
        for file in os.listdir(data_folder):
            file_path = os.path.join(data_folder, file)
            file_sum = file_summary(file_path, question)
            time.sleep(20)
            combined_res += f"Response from file: {os.path.basename(file_path)}\n\nResponse: {file_sum}\n\n"

        prompt = f"""
        Answer the question by analyzing responses across multiple files. 
        Combine relevant information from different files into a single, clear answer. 
        You may calculate totals, averages, or summaries if required.
    
        Question:
        {question}
    
        Combined Response:
        {combined_res}
        """

        response = client.models.generate_content(
            model=setting.GeminiModel,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=1500, temperature=0.2,
                                               system_instruction=system_prompt))

        return response.text
    except Exception as ex:
        print(f"Could not  query_llm for question: {question}, ex:\n {ex}")
        return False
