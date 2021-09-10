import time
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
import ocr
import utils

logger = logging.getLogger(__name__)
logger.setLevel(10)
app = FastAPI()
logger.addHandler(AzureLogHandler(connection_string='InstrumentationKey=1c37da42-ac0f-4f4a-b5a5-c47c5eedbe52'))

@app.get("/")
def read_root():
    content = """
    <body>
    <form action="/files/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
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
    for img in files:
        logger.info('Images Uploaded: '+img.filename)
        temp_file = utils._save_file_to_server(img, path="./", save_as=img.filename)
        text = await ocr.read_image(temp_file)
        response[img.filename] = text
    response["Time Taken"] = round((time.time() - s), 2)

    return response
