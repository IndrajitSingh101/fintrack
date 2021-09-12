from fastapi import FastAPI
from mangum import Mangum
from v1.routers import router

app = FastAPI(title='ocr', description='ocr tech')
app.include_router(router, prefix="/v1")


@app.get("/")
def read_root():
    return {"Hello Medium Reader": "from FastAPI & API Gateway"}


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
