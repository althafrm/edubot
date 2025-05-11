import os
import json
import nltk
import random
import torch
import numpy as np
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from nltk.tokenize import TreebankWordTokenizer

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

class ChatbotModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(ChatbotModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        return self.fc3(x)

class ChatbotAssistant:
    def __init__(self, intents_path):
        self.intents_path = intents_path
        self.vocab = []
        self.tags = []
        self.documents = []
        self.responses = {}
        self.model = None
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.tokenizer = TreebankWordTokenizer()

    def tokenize(self, sentence):
        return [self.lemmatizer.lemmatize(w.lower()) for w in self.tokenizer.tokenize(sentence)]

    def bag_of_words(self, tokenized_sentence):
        return [1 if word in tokenized_sentence else 0 for word in self.vocab]

    def load_intents(self):
        with open(self.intents_path, 'r') as f:
            data = json.load(f)
        for intent in data['intents']:
            tag = intent['tag']
            self.tags.append(tag)
            self.responses[tag] = intent['responses']
            for pattern in intent['patterns']:
                tokens = self.tokenize(pattern)
                self.vocab.extend(tokens)
                self.documents.append((tokens, tag))
        self.vocab = sorted(set(self.vocab))

    def prepare_data(self):
        X, y = [], []
        for tokens, tag in self.documents:
            X.append(self.bag_of_words(tokens))
            y.append(self.tags.index(tag))
        return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)

    def train(self, epochs=100, lr=0.001, batch_size=8):
        X, y = self.prepare_data()
        loader = DataLoader(TensorDataset(X, y), batch_size=batch_size, shuffle=True)
        self.model = ChatbotModel(len(self.vocab), len(self.tags))
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        loss_fn = nn.CrossEntropyLoss()

        for epoch in range(epochs):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                out = self.model(batch_x)
                loss = loss_fn(out, batch_y)
                loss.backward()
                optimizer.step()
            print(f"Epoch {epoch+1}/{epochs}")

    def save(self, model_path="chatbot_model.pth", meta_path="chatbot_meta.json"):
        torch.save(self.model.state_dict(), model_path)
        with open(meta_path, "w") as f:
            json.dump({
                "tags": self.tags,
                "vocab": self.vocab,
                "responses": self.responses
            }, f)

    def load(self, model_path="chatbot_model.pth", meta_path="chatbot_meta.json"):
        with open(meta_path) as f:
            meta = json.load(f)
        self.tags = meta["tags"]
        self.vocab = meta["vocab"]
        self.responses = meta["responses"]
        self.model = ChatbotModel(len(self.vocab), len(self.tags))
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def get_response(self, message):
        tokens = self.tokenize(message)
        bow = torch.tensor([self.bag_of_words(tokens)], dtype=torch.float32)
        with torch.no_grad():
            output = self.model(bow)
            probs = torch.softmax(output, dim=1)
            conf, idx = torch.max(probs, dim=1)
            if conf.item() < 0.7:
                return "I'm not sure I understand. Could you rephrase?"
            tag = self.tags[idx.item()]
            return random.choice(self.responses[tag])
