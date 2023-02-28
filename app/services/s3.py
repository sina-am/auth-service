from hashlib import md5
from os import path
import mimetypes
import boto3
from app.core.config import settings
from app.core.logging import logger
from app.models.profile import PictureIn


class S3Service():
    def __init__(self, base_directory: str) -> None:
        try:
            self.s3 = boto3.client(
                's3',
                endpoint_url=settings.s3.endpoint_url,
                aws_access_key_id=settings.s3.aws_access_key_id,
                aws_secret_access_key=settings.s3.aws_secret_access_key
            )
        except Exception as exc:
            logger.error(exc)
        else:
            self.base_directory = base_directory
            self.bucket_name = settings.s3.bucket_name

    def get_filename(self, name: str, content_type: str):
        suffix = mimetypes.guess_extension(content_type)
        if suffix:
            return path.join(self.base_directory, md5(name.encode()).hexdigest() + suffix)
        raise TypeError('invalid content-type')

    def create_object(self, key: str, content_type: str):
        return self.s3.put_object(
            ACL='public-read',
            Bucket=self.bucket_name,
            Key=key,
            ContentType=content_type
        )

    def generate_presigned_url(
        self, name: str, content_type: str,
        content_length: int, expired: int = 3600
    ) -> str:

        key = self.get_filename(name, content_type)
        try:
            self.create_object(key, content_type)
            signed_url = self.s3.generate_presigned_url(
                'put_object',
                {
                    'Key': key,
                    'Bucket': self.bucket_name,
                    'ContentType': content_type
                },
                expired
            )
        except Exception as exc:
            raise ConnectionError(exc)
        else:
            return signed_url


def create_profile_picture_url(info: PictureIn, user_id: str) -> str:
    """ Create a object for profile picture and return the presigned url. """
    service = S3Service('images/profile')
    return service.generate_presigned_url(
        user_id,
        info.content_type,
        info.content_length
    )
