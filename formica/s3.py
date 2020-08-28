import boto3
import uuid
from contextlib import contextmanager
import logging
import hashlib

logger = logging.getLogger(__name__)

s3 = boto3.resource("s3")


class TemporaryS3Bucket(object):
    def __init__(self):
        self.objects = {}
        self.uploaded = False

    def __digest(self, body):
        return str(hashlib.md5(body).hexdigest()).lower()

    def add(self, body):
        if type(body) == str:
            body = body.encode()
        object_name = self.__digest(body)
        self.objects[object_name] = body
        return object_name

    def upload(self):
        if not self.uploaded:
            self.uploaded = True
            body_hashes = "".join([key for key, _ in self.objects.items()]).encode()
            body_hashes_hash = self.__digest(body_hashes)
            self.name = "formica-deploy-{}".format(body_hashes_hash)
            self.s3_bucket = s3.Bucket(self.name)
            self.s3_bucket.create(
                CreateBucketConfiguration=dict(LocationConstraint=boto3.session.Session().region_name))
            for name, body in self.objects.items():
                logger.info("Uploading to Bucket: {}/{}".format(self.name, name))
                self.s3_bucket.put_object(Key=name, Body=body)


@contextmanager
def temporary_bucket():
    temp_bucket = TemporaryS3Bucket()
    try:
        yield temp_bucket
    finally:
        if temp_bucket.uploaded:
            to_delete = [dict(Key=obj.key) for obj in temp_bucket.s3_bucket.objects.all()]
            if to_delete:
                logger.info("Deleting {} Objects from Bucket: {}".format(len(to_delete), temp_bucket.name))
                temp_bucket.s3_bucket.delete_objects(Delete=dict(Objects=to_delete))
            logger.info("Deleting Bucket: {}".format(temp_bucket.name))
            temp_bucket.s3_bucket.delete()