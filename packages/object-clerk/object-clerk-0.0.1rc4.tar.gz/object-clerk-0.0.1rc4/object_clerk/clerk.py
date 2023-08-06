from hashlib import md5
import logging
from pathlib import Path
from sys import getsizeof
from typing import Union, Tuple
from io import BufferedReader, BytesIO
from boto3 import client as Boto3Client
from botocore.exceptions import ConnectionError, ClientError, HTTPClientError
from botocore.config import Config as BotoConfig
from retry import retry
from retry.api import retry_call

from object_clerk.exceptions import (
    ObjectClerkException,
    ObjectNotFoundException,
    ObjectSaveException,
    ObjectVerificationException,
)
from object_clerk.utils import mutate_client_exceptions

logger = logging.getLogger(__name__)  # TODO Logging pass

# Configure boto to not retry
BOTO_CONFIG = BotoConfig(connect_timeout=60, read_timeout=60, retries={"max_attempts": 0})

CONNECTION_RETRY_EXCEPTIONS = (ConnectionError, HTTPClientError)

INTERNAL_RETRY_CONFIG = {"tries": 3, "delay": 1}

# Set threshold at which the md5 checksum isn't valid to compare to the etag due to multipart uploads
MULTIPART_THRESHOLD = 1024 * 1024 * 1024 * 5  # 5 GB

__all__ = ["ObjectClerk"]


class ObjectClerk:
    """
    A wrapper for the following boto3 s3 client operations below the multipart upload threshold of 5 GB:
    - get_object : get_object
    - head_object : get_object_info
    - upload_fileobj : upload_object
    - copy_object : copy_object
    - delete_object : delete_object
    """
    def __init__(
        self,
        host: str,
        port: int,
        access_key: str,
        secret_key: str,
        retry_delay: int,
        retry_backoff: int,
        retry_jitter: Union[int, Tuple[int, int]],
        retry_max_delay: int,
        retry_tries: int = -1,
        use_ssl: bool = False,
    ):
        """
        Intialize the Object clerk with the location of the s3 gateway
        and configuration for retrying connection issues
        :param host: Host name or ip for an s3 Gateway
        :param port: Post the s3 gateway listens on
        :param access_key: Access Key for the gateway
        :param secret_key: Secret Key for the gateway
        :param retry_delay: initial delay between attempts for connection errors.
        :param retry_backoff: multiplier applied to delay between attempts to connect.
        :param retry_jitter: extra seconds added to delay between attempts to connect.
                   fixed if a number, random if a range tuple (min, max)
        :param retry_max_delay: the maximum value of delay between connection attempts.
        :param retry_tries: Number of time to retry connecting ot hte gateway. -1 for indefinite retries
        :param use_ssl: True for https and False for http
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.host = host
        self.port = port
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.retry_jitter = retry_jitter
        self.retry_max_delay = retry_max_delay
        self.retry_tries = retry_tries
        self.use_ssl = use_ssl
        self.retry_config = {
            "tries": self.retry_tries,
            "delay": self.retry_delay,
            "max_delay": self.retry_max_delay,
            "backoff": self.retry_backoff,
            "jitter": self.retry_jitter,
            "exceptions": CONNECTION_RETRY_EXCEPTIONS,
        }
        protocol = "https" if self.use_ssl else "http"
        self.endpoint_url = f"{protocol}://{self.host}:{self.port}"
        self.client = Boto3Client(
            service_name="s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
        )
        logger.info(str(self))

    def __repr__(self):
        return f"ObjectClerk(host={self.host}, port={self.port}, access_key={self.access_key}, " \
               f"secret_key=<SECRET KEY>, retry_delay={self.retry_delay}, retry_backoff={self.retry_backoff}, " \
               f"retry_jitter={self.retry_jitter}, retry_max_delay={self.retry_max_delay}, " \
               f"retry_tries={self.retry_tries}, use_ssl={self.use_ssl})"

    def __str__(self):
        return f"ObjectClerk connected to {self.endpoint_url} retrying connection errors with {self.retry_config}"

    @staticmethod
    def _get_object_checksum(object_stream: bytes) -> str:
        """

        :param object_stream:
        :return:
        """
        # Verify that the size doesn't exceed the limit at which the etag is != md5 checksum
        size = getsizeof(object_stream)
        if size > MULTIPART_THRESHOLD:
            logger.warning(f"Cannot verify the check sum of a file > {MULTIPART_THRESHOLD} bytes")
            raise ObjectClerkException(
                f"Cannot verify the check sum of a file > {MULTIPART_THRESHOLD} bytes"
            )
        return md5(object_stream).hexdigest()

    @staticmethod
    def _verify_checksum(object_checksum: str, etag: str) -> None:
        """

        :param object_checksum:
        :param etag:
        :return:
        """
        # Strip leading and trailing quotes on the etag if they exist
        etag = etag.replace('"', '')
        if object_checksum == etag:
            return

        logger.warning(
            f"Object checksum verification failed: check_sum={object_checksum}, etag={etag}"
        )
        raise ObjectVerificationException(
            f"Object checksum verification failed: check_sum={object_checksum}, etag={etag}"
        )

    @mutate_client_exceptions
    def _get_object(self, bucket: str, object_key: str) -> bytes:
        """

        :param bucket:
        :param object_key:
        :return:
        """
        logger.debug(f"Attempting object retrieval: bucket={bucket}, object_key={object_key}")
        return self.client.get_object(Bucket=bucket, Key=object_key)

    @retry(exceptions=ObjectVerificationException, **INTERNAL_RETRY_CONFIG)
    def get_object(
        self, bucket: str, object_key: str, verify_checksum: bool = True
    ) -> bytes:  # TODO check type
        """

        :param bucket:
        :param object_key:
        :param verify_checksum:
        :return:
        """
        response = retry_call(
            self._get_object,
            fkwargs={"bucket": bucket, "object_key": object_key},
            **self.retry_config,
        )
        object_stream = response.get("Body").read()
        etag = response.get("ETag")
        if verify_checksum:
            checksum = self._get_object_checksum(object_stream)
            self._verify_checksum(checksum, etag)
        return object_stream

    @mutate_client_exceptions
    def _get_object_info(self, bucket: str, object_key: str) -> dict:
        """

        :param bucket:
        :param object_key:
        :return:
        """
        logger.debug(f"Attempting object info retrieval: bucket={bucket}, object_key={object_key}")
        return self.client.head_object(Bucket=bucket, Key=object_key)

    @retry(exceptions=ObjectNotFoundException, **INTERNAL_RETRY_CONFIG)
    def get_object_info(self, bucket: str, object_key: str) -> dict:
        """

        :param bucket:
        :param object_key:
        :return:
        """
        response = retry_call(
            self._get_object_info,
            fkwargs={"bucket": bucket, "object_key": object_key},
            **self.retry_config,
        )
        return response["ResponseMetadata"].get("HTTPHeaders")

    @mutate_client_exceptions
    def _delete_object(self, bucket: str, object_key: str) -> None:
        """

        :param bucket:
        :param object_key:
        :return:
        """
        logger.debug(f"Attempting object delete: bucket={bucket}, object_key={object_key}")
        self.client.delete_object(Bucket=bucket, Key=object_key)

    def delete_object(self, bucket: str, object_key: str) -> None:
        """

        :param bucket:
        :param object_key:
        :return:
        """
        retry_call(
            self._delete_object,
            fkwargs={"bucket": bucket, "object_key": object_key},
            **self.retry_config,
        )

    @staticmethod
    def _to_readable_object(
        file: Union[str, Path, BufferedReader, BytesIO, bytes]
    ) -> BytesIO:
        """

        :param file:
        :return:
        """
        if isinstance(file, BytesIO):
            return file
        if isinstance(file, BufferedReader):
            return BytesIO(file.read())
        if isinstance(file, bytes):
            return BytesIO(file)
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path):
            raise TypeError("file must be of one of type str, Path, BufferedReader, BytesIO, bytes")
        try:
            file = file.open(mode="rb")
        except OSError as e:
            raise ObjectSaveException(f"File cannot be opened: detail={e}")
        return BytesIO(file.read())

    @mutate_client_exceptions
    def _upload_object(self, file_obj: Union[BufferedReader, BytesIO], bucket: str, object_key: str) -> None:
        """

        :param file_obj:
        :param bucket:
        :param object_key:
        :return:
        """
        logger.debug(f"Attempting object upload: bucket={bucket}, object_key={object_key}")
        # Ensure byte stream is at the beginning for retries
        file_obj.seek(0)
        self.client.upload_fileobj(file_obj, Bucket=bucket, Key=object_key)

    @retry(exceptions=ObjectVerificationException, **INTERNAL_RETRY_CONFIG)
    def upload_object(
        self, file: Union[str, Path, BufferedReader], bucket: str, object_key: str, verify_checksum: bool = True
    ) -> None:
        """

        :param file:
        :param bucket:
        :param object_key:
        :param verify_checksum:
        :return:
        """
        file_obj = self._to_readable_object(file)
        # get checksum before boto operations
        checksum = self._get_object_checksum(file_obj.read())
        # reset back to start of the stream
        file_obj.seek(0)
        retry_call(
            self._upload_object,
            fkwargs={"file_obj": file_obj, "bucket": bucket, "object_key": object_key},
            **self.retry_config,
        )
        if verify_checksum:
            etag = self.get_object_info(bucket, object_key).get("etag")
            try:
                self._verify_checksum(checksum, etag)
            except ObjectVerificationException as e:
                logger.warning(f"Saved object does not match check sum: detail={e}")
                self.delete_object(bucket, object_key)
                logger.debug(f"Saved object is removed: bucket={bucket}, object_key={object_key}")
                raise e

    @mutate_client_exceptions
    def _copy_object(
        self, source_bucket: str, source_object_key: str, destination_bucket: str, destination_object_key: str
    ) -> None:
        """

        :param source_bucket:
        :param source_object_key:
        :param destination_bucket:
        :param destination_object_key:
        :return:
        """
        logger.debug(f"Attempting object retrieval: source_bucket={source_bucket}, "
                     f"source_object_key={source_object_key}, destination_bucket={destination_bucket}, "
                     f"destination_object_key={destination_object_key}")
        copy_source = {"Bucket": source_bucket, "Key": source_object_key}
        self.client.copy_object(
            Bucket=destination_bucket, Key=destination_object_key, CopySource=copy_source
        )

    @retry(exceptions=ObjectVerificationException, **INTERNAL_RETRY_CONFIG)
    def copy_object(
        self,
        source_bucket: str,
        source_object_key: str,
        destination_bucket: str,
        destination_object_key: str,
        verify_checksum: bool = True,
    ) -> None:
        """

        :param source_bucket:
        :param source_object_key:
        :param destination_bucket:
        :param destination_object_key:
        :param verify_checksum:
        :return:
        """
        source_object_info = self.get_object_info(source_bucket, source_object_key)
        if int(source_object_info["content-length"]) > MULTIPART_THRESHOLD:
            logger.warning(
                f"Attempt to copy file greater than multipart threshold: threshold={MULTIPART_THRESHOLD}, "
                f"size={source_object_info['content-length']}, bucket={source_bucket}, object_key={source_object_key}"
            )
            raise ObjectSaveException(
                f"API doesn't support uploads over {MULTIPART_THRESHOLD} bytes.  "
                f"Use the Boto3 mutltipart upload api."
            )

        retry_call(
            self._copy_object,
            fkwargs={
                "source_bucket": source_bucket,
                "source_object_key": source_object_key,
                "destination_bucket": destination_bucket,
                "destination_object_key": destination_object_key,
            },
            **self.retry_config,
        )

        if verify_checksum:
            destination_object_info = self.get_object_info(
                destination_bucket, destination_object_key
            )
            if source_object_info["etag"] == destination_object_info["etag"]:
                return
            self.delete_object(destination_bucket, destination_object_key)
            logger.warning(
                f"Copied object does not match check sum: source_bucket={source_bucket}, "
                f"source_object_key={source_bucket}, source_checksum={source_object_info['etag']}, "
                f"destination_bucket={destination_bucket}, destination_object_key={destination_object_key}, "
                f"destination_check_sum={destination_object_info['etag']}"
            )
            self.delete_object(destination_bucket, destination_object_key)
            logger.debug(
                f"Copied object is removed: bucket={destination_bucket}, object_key={destination_object_key}"
            )
            raise ObjectVerificationException(
                f"Object checksum verification failed: "
                f"source_etag={source_object_info['etag']}, "
                f"destination_etag={destination_object_info['etag']}"
            )
