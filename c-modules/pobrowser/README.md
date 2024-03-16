# ro-browser

This package is used to print several files over the browser, for example firefox and chrome using folderpath where are the files and the name of command for example if i wan to print with firefox


```shell
    open_pdf_with_firefox(folderpath)
```

that function call another function that is 
```shell
    open_pdf_with_browser(folder_path, "start firefox")
```
and the detail of this function is
```shell
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
```