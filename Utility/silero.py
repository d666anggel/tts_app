import torch
from omegaconf import OmegaConf
from razdel import sentenize



def download_models():
    torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
                                'data/latest_silero_models.yml',
                                progress=False)
    return OmegaConf.load('data/latest_silero_models.yml')

def audioparse(model, text, speaker, sample_rate=48000):
    result = []
    lines = text.splitlines()
    for i in lines:
        if 0 < len(i) <= 1000:
            print("Длина строки: " + str(len(i)))
            temp_text = "<speak><p>" + str(i) + "</p></speak>"
            result.append(model.apply_tts(ssml_text=temp_text,
                                speaker=speaker,
                                sample_rate=sample_rate))
        elif len(i) > 1000:
            print("Длина строки: " + str(len(i)))
            for sentence in list(sentenize(i)):
                result.append(model.apply_tts(ssml_text="<speak>" + str(sentence.text) + "</speak>",
                                              speaker=speaker,
                                              sample_rate=sample_rate))
        else:
            print("Ошибка! Длины строки неопределена!")
    return result

def tts_silero(language, base_filename, file_count: int, threads_count: int):
    if language == "ua":
        model_id = "v3_ua"
        speaker = "mykyta"
    else:
        model_id = "v3_1_ru"
        speaker = "xenia"
    sample_rate = 48000
    device = torch.device("cpu")
    torch.set_num_threads(threads_count)
    model, example_text = torch.hub.load(repo_or_dir="snakers4/silero-models",
                                     model="silero_tts",
                                     language=language,
                                     speaker=model_id)
    model.to(device)
    for pagenum in range(1, file_count+1):
        audio = torch.empty
        file = "data/tmp/" + base_filename + "/PAGE" + str(pagenum) + ".txt"
        with open(file, "r", encoding="windows-1251") as f:
            page_text = f.read()
        audio = torch.cat(audioparse(model, page_text, speaker, sample_rate))
        model.write_wave(path="data/tmp/" + base_filename + "/PAGE" + str(pagenum) + ".wav",
                        audio=(audio * 32767).numpy().astype("int16"),
                        sample_rate=sample_rate)
        print("+ Записано новое аудио для страницы: " + str(pagenum))
    return print("++ Записаны аудио для всех страниц")
