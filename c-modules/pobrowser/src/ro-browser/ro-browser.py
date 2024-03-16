import os
import subprocess


def open_pdf_with_browser(folder_path, browser_command):
    files = os.listdir(folder_path)
    filesPDF = [file for file in files if file.endswith(".pdf")]
    filesPDF.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path,x)), reverse=True)
    contador = 0
    for filePDF in filesPDF:
        contador += 1
        pathComplete = os.path.abspath(os.path.join(folder_path, filePDF))
        # print(pathComplete)
        subprocess.run(f"{browser_command} --new-tab {pathComplete}", shell=True)
        # print(contador)

def open_pdf_with_firefox(folder_path):
    open_pdf_with_browser(folder_path, "start firefox")

def open_pdf_with_chrome(folder_path):
    open_pdf_with_browser(folder_path, "start chrome") 