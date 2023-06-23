import layoutparser as lp
import cv2
import numpy as np
import pdf2image
import os
import io
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image


def get_file_names(folder_path):
    file_names = []
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            file_names.append(file)
    return file_names


# Specify the folder path
folder_path = "data/"

# Call the function to get the file names
file_names = get_file_names(folder_path)

output_folder = "res_ai"

if output_folder not in os.listdir():
    os.makedirs(output_folder)

if not lp.is_detectron2_available():
    print("ERROR: Detectron2 is not available")
    exit(-1)
else:
    model = lp.Detectron2LayoutModel(
        "lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config",
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
    )


for name in file_names:
    fname = os.path.join(folder_path, name)
    doc = pdf2image.convert_from_path(fname)
    p = 1
    for page in doc:
        img = np.asarray(page)  ## predict
        detected = model.detect(img)  ## plot
        image_name = "page_" + str(p) + ".jpg"
        lp.draw_box(
            img, detected, box_width=5, box_alpha=0.2, show_element_type=True
        ).save(os.path.join(output_folder, image_name), "JPEG")
        p += 1
