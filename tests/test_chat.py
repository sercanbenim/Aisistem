import json
import importlib
import sys
import types
from unittest import mock


def test_chatbot_response_basic():
    fake_intents = {
        "classes": ["greeting"],
        "words": ["hi"],
        "intents": [
            {"tag": "greeting", "responses": ["hello", "hi there"]}
        ],
    }

    class FakeModel:
        def predict(self, x):
            return [[1.0]]

    fake_tf = types.ModuleType("tensorflow")
    fake_keras = types.ModuleType("tensorflow.keras")
    fake_models = types.ModuleType("tensorflow.keras.models")
    fake_models.load_model = lambda path: FakeModel()
    fake_keras.models = fake_models
    fake_tf.keras = fake_keras
    modules = {
        "tensorflow": fake_tf,
        "tensorflow.keras": fake_keras,
        "tensorflow.keras.models": fake_models,
    }

    fake_nltk = types.ModuleType("nltk")
    fake_nltk.word_tokenize = lambda text: text.split()
    fake_stem = types.ModuleType("nltk.stem")
    class FakeLemmatizer:
        def lemmatize(self, word):
            return word
    fake_stem.WordNetLemmatizer = lambda: FakeLemmatizer()
    modules.update({"nltk": fake_nltk, "nltk.stem": fake_stem})

    fake_np = types.ModuleType("numpy")
    fake_np.array = lambda x: x
    fake_np.argmax = lambda x: 0
    modules["numpy"] = fake_np

    with mock.patch.dict(sys.modules, modules):
        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(fake_intents))):
            import chat
            importlib.reload(chat)
            assert chat.chatbot_response("hi") in fake_intents["intents"][0]["responses"]

