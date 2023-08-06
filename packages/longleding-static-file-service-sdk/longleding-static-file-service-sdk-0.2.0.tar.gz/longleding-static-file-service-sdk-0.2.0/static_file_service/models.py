# -*- coding: utf-8 -*-
from datetime import datetime, timezone, timedelta

from .staticFileService_pb2 import OSSBucketInfoMessage, UploadCredentialsMessage


class StaticFileServiceException(Exception):
    pass


class OSSBucketInfo:

    def __init__(self, bucket_name: str, endpoint: str):
        self.bucket_name = bucket_name
        self.endpoint = endpoint

    @classmethod
    def from_pb(cls, oss_bucket_info: OSSBucketInfoMessage):
        return cls(oss_bucket_info.bucket_name, oss_bucket_info.endpoint)

    def _desc(self):
        return "<OSSBucketInfo(bucket_name:{} endpoint:{})>".format(
            self.bucket_name,
            self.endpoint
        )

    def __str__(self):
        return self._desc()

    def __repr__(self):
        return self._desc()


class UploadCredentials:

    def __init__(self, access_key_id: str, access_key_secret: str, expiration: datetime, security_token: str):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.expiration = expiration
        self.security_token = security_token

    @classmethod
    def from_pb(cls, upload_credentials: UploadCredentialsMessage):
        expiration = datetime.fromtimestamp(upload_credentials.expiration.seconds)
        expiration.replace(tzinfo=timezone(timedelta(hours=8)))
        return cls(upload_credentials.access_key_id,
                   upload_credentials.access_key_secret,
                   expiration,
                   upload_credentials.security_token)

    def _desc(self):
        return "<UploadCredentials(access_key_id:{} access_key_secret:{} expiration:{} security_token:{})>".format(
            self.access_key_id,
            self.access_key_secret,
            self.expiration,
            self.security_token
        )

    def __str__(self):
        return self._desc()

    def __repr__(self):
        return self._desc()
