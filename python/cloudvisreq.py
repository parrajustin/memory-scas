from base64 import b64encode
from os import makedirs, listdir
from os.path import join, basename
from sys import argv
import json
import requests
import pickle

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
RESULTS_DIR = 'jsons'
makedirs(RESULTS_DIR, exist_ok=True)

def make_image_data_list(image_filenames):
    """
    image_filenames is a list of filename strings
    Returns a list of dicts formatted as the Vision API
        needs them to be
    """
    img_requests = []
    for imgname in image_filenames:
        with open(imgname, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            img_requests.append({
                    'image': {'content': ctxt},
                    'features': [{
                        'type': 'TEXT_DETECTION',
                        'maxResults': 1
                    }]
            })
    return img_requests

def make_image_data(image_filenames):
    """Returns the image data lists as bytes"""
    imgdict = make_image_data_list(image_filenames)
    return json.dumps({"requests": imgdict }).encode()


def request_ocr(api_key, image_filenames):
    response = requests.post(ENDPOINT_URL,
                             data=make_image_data(image_filenames),
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if __name__ == '__main__':
    api_key, *image_filenames = argv[1:]

    # Specify the directory path (use "." for the current directory)
    directory_path = "./scan1_crop"

    # Get a list of all files and directories in the specified directory
    filenames = listdir(directory_path)

    # Print each filename
    endFileNames = []
    for filename in filenames:
        if not filename.endswith("_back.png"):
            continue
        endFileNames.append(f"./scan1_crop/{filename}")
    print(endFileNames)

    result = list(chunk_list(endFileNames, 5))
    print(result)

    # if not api_key or not endFileNames:
    #     print("""
    #         Please supply an api key, then one or more image filenames
    #         $ python cloudvisreq.py api_key image1.jpg image2.png""")
    # else:
    #     for group in result:
    #         # print(group)
    #         response = request_ocr(api_key, group)
    #         if response.status_code != 200 or response.json().get('error'):
    #             print(response.text)
    #         else:
    #             # Pickling the object
    #             with open("data.pkl", "wb") as file:  # "wb" mode opens the file in binary write mode
    #                 pickle.dump(response.json()['responses'], file)
    #             for idx, resp in enumerate(response.json()['responses']):
    #                 # save to JSON file
    #                 imgname = group[idx]
    #                 jpath = join(RESULTS_DIR, basename(imgname) + '.json')
    #                 with open(jpath, 'w') as f:
    #                     datatxt = json.dumps(resp, indent=2)
    #                     print("Wrote", len(datatxt), "bytes to", jpath)
    #                     f.write(datatxt)

    #                 # print the plaintext to screen for convenience
    #                 print("---------------------------------------------")
    #                 t = resp['textAnnotations'][0]
    #                 print("    Bounding Polygon:")
    #                 print(t['boundingPoly'])
    #                 print("    Text:")
    #                 print(t['description'])