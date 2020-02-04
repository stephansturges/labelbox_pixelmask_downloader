import argparse
import os
import json
import urllib3
import cv2
import numpy as np


if __name__ == "__main__":
    # Parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile", default="./labelbox.json", help="JSON file form labelbox", required=False
    )
    parser.add_argument(
        "--outputfolder", default="./", help="location where the labels will be output as images", required=False
    )
    parser.add_argument(
        "--binarize", default=False, help="Binarize your masks with opencv", required=False
    )
    parser.add_argument(
        "--jpg", default=False, help="Convert your images to JPG (from png default)", required=False
    )
    flags = parser.parse_args()

input_json_file = flags.inputfile
output_folder = flags.outputfolder
binarize = flags.binarize
convert_to_jpg = flags.jpg

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

http = urllib3.PoolManager()

chunk_size = 64000

def is_json_key_present(json, key):
    try:
        _ = json[key]
    except KeyError:
        return False
    return True

with open(input_json_file) as json_file:
    data = json.load(json_file)
    for object in data:
        try:
            x = object["Label"]["objects"][0]["instanceURI"]
            y = object["External ID"]
            z = object["Dataset Name"]
        except KeyError:
            pass
        else:
            print(object)
            print(object["Label"]["objects"][0]["instanceURI"])
            print(object["External ID"])
            print(object["Dataset Name"])

            if not os.path.exists(os.path.join(output_folder, object["Dataset Name"])):
                os.mkdir(os.path.join(output_folder, object["Dataset Name"]))

            path = os.path.join(output_folder, object["Dataset Name"], object["External ID"][:-4]+".png")
            r = http.request('GET', object["Label"]["objects"][0]["instanceURI"], preload_content=False)
            print(r.status)
            with open(path, 'wb') as out:
                while True:
                    data = r.read(chunk_size)
                    if not data:
                        break
                    out.write(data)
            if binarize:
                img = cv2.imread(path,0)
                ret,thresh1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
                if convert_to_jpg:
                    jpg_binarized_path = path[:-4]+".jpg"
                    with open(jpg_binarized_path, 'wb') as out:
                        try:
                            data = ret
                            cv2.imwrite(jpg_binarized_path, thresh1)
                        except:
                            pass
                else:
                    with open(path, 'wb') as out:
                        try:
                            data = ret
                            cv2.imwrite(path, thresh1)
                        except:
                            pass