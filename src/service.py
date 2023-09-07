import torch
import os
import markovify


def wavgen(text: str, speaker: str = 'baya'):
    device = torch.device('cpu')
    torch.set_num_threads(2)
    local_file = 'model.pt'

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(url='https://models.silero.ai/models/tts/ru/ru_v3.pt',
                                       dst=local_file)

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    text.lower()
    sample_rate = 44100

    model.save_wav(text=text, speaker=speaker, sample_rate=sample_rate)


async def gen_text(text: str):
    text_model = markovify.Text(text)
    return text_model.make_sentence(tries=100)
