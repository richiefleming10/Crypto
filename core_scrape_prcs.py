from openAI_engine import chat_with_gpt
import os 
import time 
import datetime 
from bs4 import BeautifulSoup
import requests
import pyperclip

def reddit_summary(url): 
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    reddit_text = pyperclip.copy(text)
    reddit_information = chat_with_gpt("")





if __name__ == "__main__":
    pass 
