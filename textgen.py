import markovify
from config import text


def gen():
    text_model = markovify.Text(text)
    return text_model.make_sentence(tries=100)

# print(text_model.make_sentence(tries=100))
