import base64
import os
import re
import sys
from os import makedirs, listdir
from os.path import join, basename
import json
import pickle

from googleapiclient import discovery
from googleapiclient import errors
# import nltk
# from nltk.stem.snowball import EnglishStemmer
from oauth2client.client import GoogleCredentials
# import redis

DISCOVERY_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'  # noqa
BATCH_SIZE = 10
RESULTS_DIR = 'scan2_jsons'
makedirs(RESULTS_DIR, exist_ok=True)

class VisionApi:
    """Construct and use the Google Vision API service."""

    def __init__(self):
        self.credentials = GoogleCredentials.get_application_default()
        self.service = discovery.build(
            'vision', 'v1', credentials=self.credentials,
            discoveryServiceUrl=DISCOVERY_URL)

    def detect_text(self, input_filenames, num_retries=3, max_results=6):
        """Uses the Vision API to detect text in the given file.
        """
        images = {}
        for filename in input_filenames:
            with open(filename, 'rb') as image_file:
                images[filename] = image_file.read()

        batch_request = []
        for filename in images:
            batch_request.append({
                'image': {
                    'content': base64.b64encode(
                            images[filename]).decode('UTF-8')
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': max_results,
                }]
            })
        request = self.service.images().annotate(
            body={'requests': batch_request})

        try:
            responses = request.execute(num_retries=num_retries)
            if 'responses' not in responses:
                return {}
            text_response = {}
            for filename, response in zip(images, responses['responses']):
                if 'error' in response:
                    print("API Error for %s: %s" % (
                            filename,
                            response['error']['message']
                            if 'message' in response['error']
                            else ''))
                    continue
                if 'textAnnotations' in response:
                    text_response[filename] = response['textAnnotations']
                else:
                    text_response[filename] = []
            return text_response
        except errors.HttpError as e:
            print("Http Error for %s: %s" % (filename, e))
        except KeyError as e2:
            print("Key error: %s" % e2)

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if __name__ == '__main__':
    # Specify the directory path (use "." for the current directory)
    directory_path = "./scan2_crop"

    # Get a list of all files and directories in the specified directory
    filenames = listdir(directory_path)

    # Print each filename
    endFileNames = []
    for filename in filenames:
        if not filename.endswith("_back.png"):
            continue
        endFileNames.append(f"./scan2_crop/{filename}")
    print(endFileNames)

    result = list(chunk_list(endFileNames, 5))
    print(result)

    result = list(chunk_list(endFileNames, 5))
    vision = VisionApi()

    all_data = {}
    for group in result:
        text = vision.detect_text(group)
        for imgname in group:
            resp = text[imgname]
            all_data[imgname] = resp
            jpath = join(RESULTS_DIR, basename(imgname) + '.json')
            with open(jpath, 'w') as f:
                datatxt = json.dumps(resp, indent=2)
                print("Wrote", len(datatxt), "bytes to", jpath)
                f.write(datatxt)
    # Pickling the object
    with open("scan2.pkl", "wb") as file:  # "wb" mode opens the file in binary write mode
        pickle.dump(all_data, file)
    # print(all_data)
    # print(text["text.png"])
