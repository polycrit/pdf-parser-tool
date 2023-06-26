import layoutparser as lp
import tabula
import numpy as np
import pdf2image
import os
import sys


def get_file_names(folder_path):
    file_names = []
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            file_names.append(file)
    return file_names


def parse_doc(dic, f):
    for k, v in dic.items():
        f.write(v)
        f.write("\n")


# Specify the folder path
folder_path = "data"

# Call the function to get the file names
file_names = get_file_names(folder_path)
print("Got data files...")

output_folder = "res_ai"

if output_folder not in os.listdir():
    os.makedirs(output_folder)

if not lp.is_detectron2_available():
    print("ERROR: Detectron2 is not available")
    exit(-1)
else:
    model = lp.Detectron2LayoutModel(
        "lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config",
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.65],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
    )

print("Loaded the Detectron2 PubLayNet model...")
# for name in file_names:
#     fname = os.path.join(folder_path, name)
#     doc = pdf2image.convert_from_path(fname)
#     p = 1
#     for page in doc:
#         img = np.asarray(page)  ## predict
#         detected = model.detect(img)  ## plot
#         image_name = "page_" + str(p) + ".jpg"
#         lp.draw_box(
#             img, detected, box_width=5, box_alpha=0.2, show_element_type=True
#         ).save(os.path.join(output_folder, image_name), "JPEG")
#         p += 1

tsrct = lp.TesseractAgent(languages=["deu", "eng"])
print("Loaded tesseract...")

for name in file_names:
    print("Beginning to process " + name + "...")
    fname = os.path.join(folder_path, name)
    doc = pdf2image.convert_from_path(fname)
    print("Converted " + name + " to images")
    res = open(os.path.join(output_folder, name + ".txt"), "a", encoding="utf-8")
    print("Create the output text file...")
    i = 1
    for page in doc:
        print("\tProcessing page " + str(i) + "/" + str(len(doc)))
        img = np.asarray(page)
        detected = model.detect(img)
        new_detected = detected.sort(key=lambda x: x.coordinates[1])
        detected = lp.Layout(
            [block.set(id=idx) for idx, block in enumerate(new_detected)]
        )
        dic_predicted = {}

        for block in [block for block in detected if block.type in ["Title", "Text"]]:
            ## segmentation
            segmented = block.pad(left=15, right=15, top=5, bottom=5).crop_image(img)
            ## extraction
            extracted = tsrct.detect(segmented)
            ## save
            dic_predicted[str(block.id) + "-" + block.type] = extracted.replace(
                "\n", " "
            ).strip()  # check

        parse_doc(dic_predicted, res)
        print("\t\tDone!")
        i += 1
