import time
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import logging
import boto3
import utils
from mangum import Mangum

logger = logging.getLogger(__name__)
logger.setLevel(10)
app = FastAPI()


@app.get("/")
def read_root():
    content = """
    <body>
    <form action="/uploadfile/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
        """
    return HTMLResponse(content=content)


@app.post("/uploadfile/")
async def analyse_file(files: List[UploadFile] = File(...)):
    logger.info("started")
    response = {}
    s = time.time()
    r = False
    text = ""
    for img in files:
        logger.info('Images Uploaded: ' + img.filename)
        temp_file = utils._save_file_to_server(img, path="", save_as=img.filename)
        byte_data = utils._get_image_bytes(temp_file)
        # Amazon Textract client
        textract = boto3.client('textract')
        # Amazon Comprehend client
        comprehend = boto3.client('comprehend')

        # Call Amazon Textract
        response = textract.detect_document_text(Document={'Bytes': byte_data})
        # Print detected text
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                print('\033[94m' + item["Text"] + '\033[0m')
                text = text + item["Text"]
        # Detect sentiment
        sentiment = comprehend.detect_sentiment(LanguageCode="en", Text=text)
        print("\nSentiment\n========\n{}".format(sentiment.get('Sentiment')))

        # Detect entities
        entities = comprehend.detect_entities(LanguageCode="en", Text=text)
        print("\nEntities\n========")
        for entity in entities["Entities"]:
            print("{}\t=>\t{}".format(entity["Type"], entity["Text"]))

        return response


# async def ocrContent(tempFile):
#     filePath = 'https://fintrack-images.s3.ap-south-1.amazonaws.com/'.join(tempFile)
#     read_response = computervision_client.read(filePath,
#                                                raw=True)
#     # temp_file = utils._save_file_to_server(img, path="./", save_as=img.filename)
#     # Get the operation location (URL with an ID at the end) from the response
#     read_operation_location = read_response.headers["Operation-Location"]
#     # Grab the ID from the URL
#     operation_id = read_operation_location.split("/")[-1]
#     r = read_operation_location
#     # Call the "GET" API and wait for it to retrieve the results
#     while True:
#         read_result = computervision_client.get_read_result(operation_id)
#         if read_result.status not in ['notStarted', 'running']:
#             break
#         time.sleep(1)
#
#     # Print the detected text, line by line
#     if read_result.status == OperationStatusCodes.succeeded:
#         for text_result in read_result.analyze_result.read_results:
#             for line in text_result.lines:
#                 print(line.text)
#                 print(line.bounding_box)
#     print()

# def uploadFileToAWS(temp_file):
#
#     try:
#         KVUri = f"https://fintrack-key.vault.azure.net"
#         app_credentials = ClientSecretCredential(tenant_id, client_id, client_secret)
#         client = SecretClient(vault_url=KVUri, credential=app_credentials)
#         ACCESS_KEY = client.get_secret('S3ACCESSKEY')
#         SECRET_KEY = client.get_secret('S3SECRETKEY')
#         bucket = 'fintrack-images'
#         s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY.value,
#                           aws_secret_access_key=SECRET_KEY.value)
#         s3.upload_file(temp_file, bucket, temp_file)
#         print("Upload Successful")
#         return True
#     except FileNotFoundError:
#         print("The file was not found")
#         raise
#     except NoCredentialsError:
#         print("Credentials not available")
#         raise
handler = Mangum(app=app)
