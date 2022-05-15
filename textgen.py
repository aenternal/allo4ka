import markovify
from config import text

text_model = markovify.Text(text)

# print(text_model.make_sentence(tries=100))
