import os
import time
import shutil
import PySimpleGUI as sg
from Utility.converting import *
from Utility.silero import *

def main():
    available_languages = ["Украинский", "Русский"]
    available_threads = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    available_codecs = ["Другая", "AMD", "NVIDIA"]
    sg.theme("Default1")
    layout = [
        [sg.Text("Язык: "), sg.Combo(available_languages, key="input_lang", default_value="Русский"), sg.Text("Кол-во потоков: "), sg.Combo(available_threads, key="input_thread", default_value="2"), sg.Text("Видеокарта: "), sg.Combo(available_codecs, key="input_codec", default_value="Другая")],
        [sg.Text("Файл сценария (.txt): ")],
        [sg.InputText(key="file_scenario"), sg.FileBrowse("Выбрать", file_types=(("Текстовый", "*.txt"),))],
        [sg.Text("Файл презентации (.pdf): ")],
        [sg.InputText(key="file_pres"), sg.FileBrowse("Выбрать", file_types=(("PDF", "*.pdf"),))],
        [sg.Text("Директория куда сохранить готовый файл: ")],
        [sg.InputText(key="dir_out"), sg.FolderBrowse("Выбрать")],
        [sg.Output(size=(88, 20))],
        [sg.Submit("Перевести"), sg.Exit("Закрыть")],
        [sg.ProgressBar(100, orientation="h", border_width=2, key="progbar"), sg.Text("", key="status")]
    ]
    window = sg.Window("TTS для презентаций", layout)
    while True:
        event, values = window.read()
        # print(event, values)
        if event == sg.WIN_CLOSED or event == "Закрыть":
            break
        # if event == "Обновить":
        #     models = download_models()
        #     available_languages = list(models.tts_models.keys())
        #     window["input_lang"].update(values=available_languages)
        #     print(f"Доступные языки {available_languages}")
        #     for lang in available_languages:
        #         model_id = list(models.tts_models.get(lang).keys())
        #         print(f"Доступные model_id для языка {lang}: {model_id}")
        elif event == "Перевести":
            window["progbar"].update_bar(0)
            window["status"].update("")
            if os.path.isfile(values["file_scenario"]) and os.path.isfile(values["file_pres"]) and os.path.isdir(values["dir_out"]) and values["input_lang"] != "" and values["input_codec"] != "" and type(values["input_thread"]) == int:
                scenario_name, scenario_extension = os.path.splitext(values["file_scenario"])
                pres_name, pres_extension = os.path.splitext(values["file_pres"])
                if scenario_extension == ".txt" and pres_extension == ".pdf":
                    if values["input_lang"] == "Украинский":
                        lang = "ua"
                    elif values["input_lang"] == "Русский":
                        lang = "ru"
                    else:
                        print("Указан язык, который не поддерживается")
                    base_filename = lang + "_" + time.strftime("%Y%m%d_%H%M%S")
                    scenario_pages = scenario_separate(base_filename, values["file_scenario"])
                    window["progbar"].update_bar(10)
                    pres_pages = pres_separate(base_filename, values["file_pres"])
                    if scenario_pages != pres_pages:
                        clean_tmp(base_filename)
                        print("Ошибка! Количество страниц текста и количество страниц в презентации не совпадают, проверьте на ошибки исходные файлы")
                    else:
                        window["progbar"].update_bar(30)
                        window["status"].update("Обработка аудио")
                        tts_silero(lang, base_filename, scenario_pages, int(values["input_thread"]))
                        window["progbar"].update_bar(60)
                        window["status"].update("Обработка видео")
                        convert_paged_mp4(base_filename, scenario_pages, values["input_codec"])
                        window["progbar"].update_bar(80)
                        window["status"].update("Объединение видео")
                        convert_mp4(base_filename, scenario_pages, values["dir_out"])
                        window["progbar"].update_bar(100)
                        window["status"].update("Готово!")
                        clean_tmp(base_filename)
                else:
                    print("Расширения выбранных файлов не соответствуют требованиям. Должны быть .txt и .pdf")
            else:
                print("Не найден один из выбранных файлов, проверьте правильность выбранного пути")
    window.close()

def clean_tmp(base_filename):
    try:
        shutil.rmtree("data/tmp/" + base_filename)
    except OSError as e:
        print("Ошибка! Очистка временной папки: %s - %s." % (e.filename, e.strerror))

main()