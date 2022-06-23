import os
import re
import ffmpeg
from wand.image import Image
from wand.color import Color

def scenario_separate(base_filename, file):
    # Регулярка для поиска строки с названием файла
    pattern_filename = re.compile("={5} (.+?) ={5}")
    path = "data/tmp/" + base_filename
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    with open(file, "r", encoding="windows-1251") as f:
        file_arr = []
        file_count = int(0)
        filename = ""
        file_obj = None
        is_file_header = True

        for line in f:
            # Проверка наличия заголовка в файле
            match = pattern_filename.search(line)
            if match:
                if file_obj:
                    file_obj.close()

                file_count+=1
                print("+ Создание нового файла: " + str(match.group(1)) + str(file_count))
                file_arr.append(str(match.group(1)) + str(file_count))
                filename = path + "/" + str(match.group(1)) + str(file_count) + ".txt"
                file_obj = open(filename, "w", encoding="windows-1251")
                file_obj.write("<break time='3s'/>")
                is_file_header = True
                continue

            if not filename:
                continue

            if is_file_header:
                file_obj.write(line)
                is_file_header = False

            else:
                file_obj.write(line)

        if file_obj:
            file_obj.close()

    print("# Количество страниц для озвучки: " + str(file_count))
    return int(file_count)

def pres_separate(base_filename, file, resolution, dpi=300):
    all_pages = Image(filename=file, resolution=dpi)
    path = "data/tmp/" + base_filename
    for i, page in enumerate(all_pages.sequence):
        file_count = int(i+1)
        with Image(page) as img:
            img.format = "png"
            # img.transform(resize='2560x1820')
            if resolution == "16:9":
                img.resize(2560, 1440)
            elif resolution == "16:10":
                img.resize(2560, 1600)
            else:
                img.resize(2560, 1820)
            img.background_color = Color("white")
            # img.alpha_channel = "remove"

            image_filename = os.path.splitext(os.path.basename(file))[0]
            image_filename = "PAGE{}.png".format(i+1)
            image_filename = os.path.join(path, image_filename)

            img.save(filename=image_filename)

    print("# Количество страниц презентации: " + str(file_count))
    return file_count

def convert_paged_mp4(base_filename, file_count: int, videocard):
    if videocard == "AMD":
        vcodec = "h264_amf"
    elif videocard == "NVIDIA":
        vcodec = "h264_nvenc"
    else:
        vcodec = "libx264"
    for pagenum in range(1, file_count+1):
        image_file = ffmpeg.input("data/tmp/" + base_filename + "/PAGE" + str(pagenum) + ".png", r=1)
        audio_file = ffmpeg.input("data/tmp/" + base_filename + "/PAGE" + str(pagenum) + ".wav")
        (
            ffmpeg
            .output(image_file, audio_file, "data/tmp/" + base_filename + "/PAGE" + str(pagenum) + ".mp4", vcodec=vcodec, acodec="libmp3lame", audio_bitrate="320k")
            .run()
        )
    return print("+ Постраничное видео готово!")

def convert_mp4(base_filename, file_count: int, out_dir="data"):
    file_obj = open("data/tmp/" + base_filename + "/pages.txt", "w", encoding="windows-1251")
    for pagenum in range(1, file_count+1):
        file_obj.write("file 'PAGE" + str(pagenum) +".mp4'\n")
    file_obj.close()
    (
        ffmpeg
        .input("data/tmp/" + base_filename + "/pages.txt", f="concat")
        .output( out_dir + "/" + base_filename + ".mp4", vcodec="copy", acodec="copy")
        .run()
    )
    return print("+++ Видео готово! Найти его можете в папке: " + out_dir + "/" + base_filename + ".mp4")
