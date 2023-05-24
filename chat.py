import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
import tensorflow as tf
import random
import json

# Önceden eğitilmiş modeli yükle
model = tf.keras.models.load_model("chatbot_model.h5")

# İntentleri yükle
with open('intents.json') as file:
    intents = json.load(file)

# Kelimeleri lemmatize etmek için bir nesne oluştur
lemmatizer = WordNetLemmatizer()

# Modelin tahmin edebileceği sınıfları ve sözlüğü yükle
classes = intents['classes']
words = intents['words']

# Chat bot cevapları veren bir fonksiyon yazalım
def chatbot_response(msg):
    # Girdiyi ön işleyelim
    msg = msg.lower()
    words = nltk.word_tokenize(msg)
    words = [lemmatizer.lemmatize(word) for word in words]

    # Girdiye karşılık gelen bag of words dizisini oluşturalım
    bag_of_words = [0] * len(words)
    for w in words:
        for i, word in enumerate(words):
            if word == w:
                bag_of_words[i] = 1

    # Tahminlerimizi yapalım
    results = model.predict(np.array([bag_of_words]))[0]
    # En yüksek tahmini bulalım
    highest_index = np.argmax(results)
    # Sınıf etiketi bulalım
    tag = classes[highest_index]

    # Eğer tahminimiz belirli bir eşik değerinin altındaysa, 
    # kullanıcının mesajına bir karşılık veremiyoruz demektir
    if results[highest_index] < 0.5:
        return "Üzgünüm, sizi anlamadım. Lütfen tekrar deneyin."

    # Tag'e göre en uygun cevabı seçelim
    for intent in intents['intents']:
        if intent['tag'] == tag:
            response = random.choice(intent['responses'])
            break

    return response

# Kullanıcıyla sohbet etmek için bir döngü başlatalım
while True:
    msg = input("Siz: ")
    if msg.lower() == "quit":
        break

    response = chatbot_response(msg)
    print("Chat Bot: ", response)
