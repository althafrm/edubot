import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TreebankWordTokenizer
from chatbot_model import ChatbotAssistant

lemmatizer = WordNetLemmatizer()
tokenizer = TreebankWordTokenizer()

ml_bot = ChatbotAssistant("intents.json")
ml_bot.load()

def normalize_input(user_input):
    user_input = user_input.lower()
    user_input = re.sub(r"[^\w\s]", "", user_input)
    words = tokenizer.tokenize(user_input)
    return " ".join([lemmatizer.lemmatize(w) for w in words])

def get_answer(user_input):
    norm = normalize_input(user_input)
    return ml_bot.get_response(norm)
