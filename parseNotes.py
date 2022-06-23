import os
import glob
import xml.etree.ElementTree as ET

num_files = len(glob.glob("notesSlides/*.xml"))
filename = "notesSlides/Theme1(" + str(num_files) + " pages).txt"
file_obj = open(filename, "w", encoding="windows-1251")
for i in range(1,num_files):
    tree = ET.parse('./notesSlides/notesSlide' + str(i) +'.xml')
    root = tree.getroot()
    file_obj.write('===== PAGE =====' + '\n')
    #/p:notes/p:cSld/p:spTree/p:sp/p:txBody/a:p/a:r/a:t
    for sub in root.findall("./{http://schemas.openxmlformats.org/presentationml/2006/main}cSld/{http://schemas.openxmlformats.org/presentationml/2006/main}spTree/{http://schemas.openxmlformats.org/presentationml/2006/main}sp/{http://schemas.openxmlformats.org/presentationml/2006/main}txBody/"):
        for text in sub.findall('./{http://schemas.openxmlformats.org/drawingml/2006/main}r'):
            if str(text.find('{http://schemas.openxmlformats.org/drawingml/2006/main}t').text) != 'Элькон':
                file_obj.write(text.find('{http://schemas.openxmlformats.org/drawingml/2006/main}t').text + '\n')
file_obj.close()