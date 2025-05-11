from chatbot_model import ChatbotAssistant

bot = ChatbotAssistant("intents.json")
bot.load_intents()
bot.train(epochs=100)
bot.save()
