import sys, pathlib, fitz
import os


def get_file_names(folder_path):
    file_names = []
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            file_names.append(file)
    return file_names


# Specify the folder path
folder_path = "data"

# Call the function to get the file names
file_names = get_file_names(folder_path)

if not os.path.exists("res"):
    os.makedirs("res")

# Print the file names
for name in file_names:
    fname = folder_path + "/" + name
    with fitz.open(fname) as doc:  # open document
        text = chr(12).join([page.get_text() for page in doc])
    # write as a binary file to support non-ASCII characters
    pathlib.Path("res/" + name + ".txt").write_bytes(text.encode())

# import openpyxl

# wb = openpyxl.load_workbook("data/Regulations.xlsx")
# ws = wb["Regulations"]
# # This will fail if there is no hyperlink to target
# print(ws.cell(row=2, column=8).hyperlink.target)
