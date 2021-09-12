import time

from fastapi import APIRouter
from typing import List
from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse
import boto3

from . import utils

router = APIRouter()


@router.get("/amazon/ocr")
def read_root():
    content = """
    <body>
    <form action="/v1/amazon/ocr/uploadfile/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
        """
    return HTMLResponse(content=content)


@router.post("/amazon/ocr/uploadfile/")
async def analyse_file(files: List[UploadFile] = File(...)):
    response = {}
    s = time.time()
    r = False
    text = ""
    for img in files:
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
