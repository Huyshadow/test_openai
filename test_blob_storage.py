from azure.storage.blob import BlobServiceClient

conn_str = "your-connection-string"
container_name = "raw-data"
blob_service = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service.get_container_client(container_name)

with open("data.csv", "rb") as data:
    container_client.upload_blob("daily_data/data.csv", data, overwrite=True)
