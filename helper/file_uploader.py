# 引入MinIO包。
from minio import Minio
from minio.error import (S3Error)
# from minio.error import (ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists)


class MinioClient():
    def __init__(self, endpoint, access_key=None,
                 secret_key=None,
                 session_token=None,
                 secure=True,
                 region=None,
                 http_client=None,
                 credentials=None) -> None:
        self.client=Minio(endpoint=endpoint, access_key=access_key, secret_key= secret_key, secure= secure)
    
    def upload(self, bucket_name, object_name, file_path,
                    content_type="application/octet-stream",
                    metadata=None, sse=None, progress=None,
                    part_size=0, num_parallel_uploads=3,
                    tags=None, retention=None, legal_hold=False):
        # try:
        #     self.client.make_bucket(bucket_name= bucket_name, location="us-east-1")
        # except S3Error as err:
        #     # print(err.code)
        #     if err.code == "BucketAlreadyExists":
        #         print("test succ")
        #     if err.code == "BucketAlreadyOwnedByYou":
        #         print("succ BucketAlreadyOwnedByYou")
        try:
            result=self.client.fput_object(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
            print("result:", result.bucket_name)
        except S3Error as err:
            print(err.code)
        
        return result.location
    
    def download(self, bucket_name, object_name, file_path):
        self.client.fget_object(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
