import os
import time
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import boto3
from botocore.exceptions import NoCredentialsError
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import utils

# accessing the key vault




subscription_key = "3daa44e536e84a0d9a8069d59421efc3"
endpoint = "https://fintrack-computer-vision.cognitiveservices.azure.com/"

logger = logging.getLogger(__name__)
logger.setLevel(10)
app = FastAPI()
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


@app.get("/")
def read_root():
    content = """
    <body>
    <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
        """
    return HTMLResponse(content=content)


@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    response = {}
    s = time.time()
    r = False
    for img in files:
        logger.info('Images Uploaded: ' + img.filename)
        temp_file = utils._save_file_to_server(img, path="", save_as=img.filename)
        r = uploadFileToAWS(temp_file)
    return r


async def ocrContent(tempFile):
    filePath = 'https://fintrack-images.s3.ap-south-1.amazonaws.com/'.join(tempFile)
    read_response = computervision_client.read(filePath,
                                               raw=True)
    # temp_file = utils._save_file_to_server(img, path="./", save_as=img.filename)
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]
    r = read_operation_location
    # Call the "GET" API and wait for it to retrieve the results
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                print(line.text)
                print(line.bounding_box)
    print()


def uploadFileToAWS(temp_file):

    try:
        KVUri = f"https://fintrack-key.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KVUri, credential=credential)
        ACCESS_KEY = client.get_secret('S3ACCESSKEY')
        SECRET_KEY = client.get_secret('S3SECRETKEY')
        bucket = 'fintrack-images'
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY.value,
                          aws_secret_access_key=SECRET_KEY.value)
        s3.upload_file(temp_file, bucket, temp_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        raise
    except NoCredentialsError:
        print("Credentials not available")
        raise
