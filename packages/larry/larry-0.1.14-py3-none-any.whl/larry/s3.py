import boto3
import botocore
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
from io import StringIO, BytesIO
import os
import json
from larry import utils
from larry import sts
import uuid
from urllib.request import Request
from urllib import parse
from urllib import request
from zipfile import ZipFile
from collections import Mapping

# Local S3 resource object
resource = None
# A local instance of the boto3 session to use
__session = boto3.session.Session()


def set_session(aws_access_key_id=None,
                aws_secret_access_key=None,
                aws__session_token=None,
                region_name=None,
                profile_name=None,
                boto_session=None):
    """
    Sets the boto3 session for this module to use a specified configuration state.
    :param aws_access_key_id: AWS access key ID
    :param aws_secret_access_key: AWS secret access key
    :param aws__session_token: AWS temporary session token
    :param region_name: Default region when creating new connections
    :param profile_name: The name of a profile to use
    :param boto_session: An existing session to use
    :return: None
    """
    global __session, resource
    __session = boto_session if boto_session is not None else boto3.session.Session(**utils.copy_non_null_keys(locals()))
    sts.set_session(boto_session=__session)
    resource = __session.resource('s3')


def delete_object(bucket=None, key=None, uri=None, s3_resource=None):
    """
    Deletes the object defined by the bucket/key pair (or uri).
    :param bucket: The S3 bucket
    :param key: The key of the object
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: Dict containing the boto3 response
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    return s3_resource.Bucket(bucket).Object(key=key).delete()


def get_object(bucket=None, key=None, uri=None, s3_resource=None):
    """
    Performs a 'get' of the object defined by the bucket/key pair (or uri).
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: Dict containing the Body of the object and associated attributes
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    return s3_resource.Bucket(bucket).Object(key=key).get()


def get_object_size(bucket=None, key=None, uri=None, s3_resource=None):
    """
    Returns the content_length of an S3 object.
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: Size in bytes
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    return s3_resource.Bucket(bucket).Object(key=key).content_length


def read_object(bucket=None, key=None, uri=None, amt=None, s3_resource=None):
    """
    Performs a 'get' of the object defined by the bucket/key pair (or uri)
    and then performs a 'read' of the Body of that object.
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param amt: The max amount of bytes to read from the object. All data is read if omitted.
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The bytes contained in the object
    """
    s3_resource = s3_resource if s3_resource else resource
    return get_object(bucket, key, uri, s3_resource=s3_resource)['Body'].read(amt)


def read_dict(bucket=None, key=None, uri=None, encoding='utf-8', s3_resource=None):
    """
    Reads in the s3 object defined by the bucket/key pair (or uri) and
    loads the json contents into a dict.
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param encoding: The charset to use when decoding the object bytes, utf-8 by default
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: A dict representation of the json contained in the object
    """
    s3_resource = s3_resource if s3_resource else resource
    return json.loads(read_object(bucket, key, uri, s3_resource=s3_resource).decode(encoding),
                      object_hook=utils.JSONDecoder)


def read_str(bucket=None, key=None, uri=None, encoding='utf-8', s3_resource=None):
    """
    Reads in the s3 object defined by the bucket/key pair (or uri) and
    decodes it to text.
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param encoding: The charset to use when decoding the object bytes, utf-8 by default
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The contents of the object as a string
    """
    s3_resource = s3_resource if s3_resource else resource
    return read_object(bucket, key, uri, s3_resource=s3_resource).decode(encoding)


def read_list_of_dict(bucket=None, key=None, uri=None, encoding='utf-8', newline='\n', s3_resource=None):
    """
    Reads in the s3 object defined by the bucket/key pair (or uri) and
    loads the JSON Lines data into a list of dict objects.
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param encoding: The charset to use when decoding the object bytes, utf-8 by default
    :param newline: The line separator to use when reading in the object, \n by default
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The contents of the object as a list of dict objects
    """
    s3_resource = s3_resource if s3_resource else resource
    obj = read_object(bucket, key, uri, s3_resource=s3_resource)
    lines = obj.decode(encoding).split(newline)
    records = []
    for line in lines:
        if len(line) > 0:
            record = json.loads(line, object_hook=utils.JSONDecoder)
            records.append(record)
    return records


def read_list_of_str(bucket=None, key=None, uri=None, encoding='utf-8', newline='\n', s3_resource=None):
    """
    Reads in the s3 object defined by the bucket/key pair (or uri) and
    loads the JSON Lines data into a list of dict objects.
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param encoding: The charset to use when decoding the object bytes, utf-8 by default
    :param newline: The line separator to use when reading in the object, \n by default
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The contents of the object as a list of dict objects
    """
    s3_resource = s3_resource if s3_resource else resource
    obj = read_object(bucket, key, uri, s3_resource=s3_resource)
    lines = obj.decode(encoding).split(newline)
    records = []
    for line in lines:
        if len(line) > 0:
            records.append(line)
    return records


def read_pillow_image(bucket=None, key=None, uri=None, s3_resource=None):
    """
    Reads in the s3 object defined by the bucket/key pair (or uri) and
    loads it into a Pillow image object
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The contents of the object as a Pillow image object
    """
    s3_resource = s3_resource if s3_resource else resource
    try:
        from PIL import Image
        return Image.open(BytesIO(read_object(bucket, key, uri, s3_resource=s3_resource)))
    except ImportError as e:
        # Simply raise the ImportError to let the user know this requires Pillow to function
        raise e


def write(body, bucket=None, key=None, uri=None, acl=None, content_type=None, s3_resource=None):
    """
    Write an object to the bucket/key pair (or uri).
    :param body: Data to write
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param acl: The canned ACL to apply to the object
    :param content_type: A standard MIME type describing the format of the object data
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The URI of the object written to S3
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    obj = s3_resource.Bucket(bucket).Object(key=key)
    if acl and content_type:
        obj.put(Body=body, ACL=acl, ContentType=content_type)
    elif acl:
        obj.put(Body=body, ACL=acl)
    elif content_type:
        obj.put(Body=body, ContentType=content_type)
    else:
        obj.put(Body=body)
    return compose_uri(bucket, key)


def write_temp_object(value, prefix, acl=None, s3_resource=None, bucket_identifier=None, region=None,
                      bucket=None):
    """
    Write an object to a temp bucket with a unique UUID.
    :param value: Object to write to S3
    :param prefix: Prefix to attach ahead of the UUID as the key
    :param acl: The canned ACL to apply to the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :param bucket_identifier: The identifier to attach to the temp bucket that will be used for writing to s3, typically
    the account id (from STS) for the account being used
    :param region: The s3 region to store the data in
    :param bucket: The bucket to use instead of creating/using a temp bucket
    :return: The URI of the object written to S3
    """
    s3_resource = s3_resource if s3_resource else resource
    if bucket is None:
        bucket = get_temp_bucket(region=region, bucket_identifier=bucket_identifier, s3_resource=s3_resource)
    key = prefix + str(uuid.uuid4())
    return write_object(value, bucket=bucket, key=key, acl=acl, s3_resource=s3_resource)


def write_object(value, bucket=None, key=None,
                 uri=None,
                 acl=None,
                 newline='\n',
                 content_type=None,
                 s3_resource=None):
    """
    Write an object to the bucket/key pair (or uri), converting the python
    object to an appropriate format to write to file.
    :param value: Object to write to S3
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param acl: The canned ACL to apply to the object
    :param newline: Character(s) to use as a newline for list objects
    :param content_type: Content type to apply to the file, if not present a suggested type will be applied
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The URI of the object written to S3
    """
    s3_resource = s3_resource if s3_resource else resource
    extension_types = {
        'css': 'text/css',
        'html': 'text/html',
        'xhtml': 'text/html',
        'htm': 'text/html',
        'xml': 'text/xml',
        'csv': 'text/csv',
        'txt': 'text/plain',
        'png': 'image/png',
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'gif': 'image/gif',
        'jsonl': 'application/x-jsonlines',
        'json': 'application/json',
        'js': 'application/javascript',
        'zip': 'application/zip',
        'pdf': 'application/pdf',
        'sql': 'application/sql'
    }
    if uri:
        (bucket, key) = decompose_uri(uri)
    extension = key.split('.')[-1]
    # JSON
    if isinstance(value, Mapping):
        if content_type is None:
            content_type = 'application/json'
        return write(json.dumps(value, cls=utils.JSONEncoder), bucket, key, uri,
                     acl, content_type=content_type, s3_resource=s3_resource)
    # Text
    elif isinstance(value, str):
        if content_type is None:
            content_type = extension_types.get(extension, 'text/plain')
        return write(value, bucket, key, uri, acl, content_type=content_type, s3_resource=s3_resource)
    elif isinstance(value, list):
        if content_type is None:
            content_type = extension_types.get(extension, 'text/plain')
        buff = StringIO()
        for row in value:
            if isinstance(row, Mapping):
                buff.write(json.dumps(row, cls=utils.JSONEncoder) + newline)
            else:
                buff.write(str(row) + newline)
        return write(buff.getvalue(), bucket, key, uri, acl, content_type=content_type, s3_resource=s3_resource)
    elif value is None:
        return write('', bucket, key, uri, acl, s3_resource=s3_resource, content_type=content_type)
    else:
        # try to write it as an image
        try:
            buff = BytesIO()
            fmt = 'PNG' if value.format is None else value.format
            value.save(buff, fmt)
            buff.seek(0)
            if content_type is None:
                content_type = extension_types.get(extension, extension_types.get(fmt.lower(), 'text/plain'))
            return write(buff, bucket, key, uri, content_type=content_type, s3_resource=s3_resource)
        except Exception:
            return write(value, bucket, key, uri, acl, content_type=content_type, s3_resource=s3_resource)


def write_pillow_image(image, image_format, bucket=None, key=None, uri=None, s3_resource=None):
    """
    Write an image to the bucket/key pair (or uri).
    :param image: The image to write to S3
    :param image_format: The format of the image (png, jpeg, etc)
    :param bucket: The S3 bucket for the object
    :param key: The key of the object
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The URI of the object written to S3
    """
    s3_resource = s3_resource if s3_resource else resource
    buff = BytesIO()
    image.save(buff, image_format)
    buff.seek(0)
    return write(buff, bucket, key, uri, s3_resource=s3_resource)


def write_as_csv(rows, bucket=None, key=None, uri=None, acl=None, delimiter=',', columns=None, headers=None,
                 s3_resource=None):
    """
    Write an object to the bucket/key pair (or uri), converting the python
    object to an appropriate format to write to file.
    :param rows: List of data to write, rows can be of type list, dict or str
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param acl: The canned ACL to apply to the object
    :param delimiter: Column delimiter to use, ',' by default
    :param columns: The columns to write out from the source rows, dict keys or list indexes
    :param headers: Headers to add to the output
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The URI of the object written to S3
    """
    s3_resource = s3_resource if s3_resource else resource

    def _array_to_string(_row, _delimiter, _indices=None):
        if _indices is None:
            _indices = range(len(_row))
        _line = ''
        for x in _indices:
            _line = str(row[x]) if x == 0 else _line + _delimiter + str(row[x])
        return _line

    buff = StringIO()

    # empty
    if rows is None or len(rows) == 0:
        if headers:
            buff.write(_array_to_string(headers, delimiter) + "\n")
        buff.write('')

    # list
    elif isinstance(rows[0], list):
        indices = columns if columns else None
        if headers:
            buff.write(_array_to_string(headers, delimiter) + "\n")
        for row in rows:
            buff.write(_array_to_string(row, delimiter, indices) + "\n")

    # dict
    elif isinstance(rows[0], Mapping):
        keys = columns if columns else rows[0].keys()
        buff.write(_array_to_string(headers if headers else keys, delimiter) + "\n")

        for row in rows:
            line = ''
            for i, k in enumerate(keys):
                value = '' if row.get(k) is None else str(row.get(k))
                line = value if i == 0 else line + delimiter + value
            buff.write(line + "\n")

    # string
    elif isinstance(rows[0], str):
        buff.writelines(rows)
    else:
        raise Exception('Invalid input')
    return write(buff.getvalue(), bucket, key, uri, acl, s3_resource=s3_resource)


def rename_object(old_bucket_name, old_key, new_bucket_name, new_key, s3_resource=None):
    """
    Renames an object in S3.
    :param old_bucket_name: Source bucket
    :param old_key: Source key
    :param new_bucket_name: Target bucket
    :param new_key: Target key
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: None
    """
    s3_resource = s3_resource if s3_resource else resource
    copy_source = {
        'Bucket': old_bucket_name,
        'Key': old_key
    }
    s3_resource.meta.client.copy(copy_source, new_bucket_name, new_key)
    s3_resource.meta.client.delete_object(Bucket=old_bucket_name, Key=old_key)


def object_exists(bucket=None, key=None, uri=None, s3_resource=None):
    """
    Checks to see if an object with the given bucket/key (or uri) exists.
    :param bucket: The S3 bucket for the object
    :param key: The key of the object
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: True if the key exists, if not, False
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    try:
        s3_resource.Object(bucket, key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise e
    return True


def _find_largest_common_prefix(values):
    """
    Searches through a list of values to find the longest possible common prefix amongst them. Useful for optimizing
    more costly searches. Supports lists of strings or tuples. If tuples are used, the first value is assumed to be
    the value to search on.
    :param values: List of values (strings or tuples containing a string in the first position)
    :return: String prefix common to all values
    """
    if isinstance(values[0], tuple):
        prefix, *_ = values[0]
    else:
        prefix = values[0]

    for value in values:
        key = value[0] if isinstance(value, tuple) else value
        while key[:len(prefix)] != prefix and len(prefix) > 0:
            prefix = prefix[:-1]
    return prefix


def find_keys_not_present(bucket, keys=None, uris=None, s3_resource=None):
    """
    Searches an S3 bucket for a list of keys and returns any that cannot be found.
    :param bucket: The S3 bucket to search
    :param keys: A list of keys to search for (strings or tuples containing a string in the first position)
    :param uris: A list of S3 URIs to search for (strings or tuples containing a string in the first position)
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: A list of keys that were not found (strings or tuples based on the input values)
    """
    s3_resource = s3_resource if s3_resource else resource

    # If URIs are passed, convert to a list of keys to use for the search
    if uris:
        keys = []
        for value in uris:
            if isinstance(value, tuple):
                uri, *z = value
                b, key = decompose_uri(uri)
                keys.append(tuple([key]) + tuple(z))
            else:
                b, key = decompose_uri(value)
                keys.append(key)

    # Find the longest common prefix to use as the search term
    prefix = _find_largest_common_prefix(keys)

    # Get a list of all keys in the bucket that match the prefix
    bucket_obj = s3_resource.Bucket(bucket)
    all_keys = []
    for obj in bucket_obj.objects.filter(Prefix=prefix):
        all_keys.append(obj.key)

    # Search for any keys that can't be found
    not_found = []
    for value in keys:
        key = value[0] if isinstance(value, tuple) else value
        if key not in all_keys:
            not_found.append(value)
    return not_found


def decompose_uri(uri):
    """
    Decompose an S3 URI into a bucket and key
    :param uri: S3 URI
    :return: Tuple containing a bucket and key
    """
    bucket_name = get_bucket_name(uri)
    return bucket_name, get_bucket_key(bucket_name, uri)


def get_bucket_name(uri):
    """
    Retrieve the bucket portion from an S3 URI
    :param uri: S3 URI
    :return: Bucket name
    """
    return uri.split('/')[2]


def get_bucket_key(bucket_name, uri):
    """
    Retrieves the key portion of an S3 URI
    :param bucket_name: S3 bucket name
    :param uri: S3 URI
    :return: Key value
    """
    pos = uri.find(bucket_name) + len(bucket_name) + 1
    return uri[pos:]


def compose_uri(bucket, key):
    """
    Compose a bucket and key into an S3 URI
    :param bucket: Bucket name
    :param key: Object key
    :return: S3 URI string
    """
    return "s3://{}/{}".format(bucket, key)


def list_objects(bucket=None, prefix=None, uri=None, include_empty_keys=False, s3_resource=None):
    """
    Returns a list of the object keys in the provided bucket that begin with the provided prefix.
    :param bucket: The S3 bucket to query
    :param prefix: The key prefix to use in searching the bucket
    :param uri: An s3:// path containing the bucket and prefix
    :param include_empty_keys: True if you want to include keys associated with objects of size=0
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: A generator of object keys
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, prefix) = decompose_uri(uri)
    paginator = s3_resource.meta.client.get_paginator('list_objects')
    operation_parameters = {'Bucket': bucket, 'Prefix': prefix}
    page_iterator = paginator.paginate(**operation_parameters)
    for page in page_iterator:
        for obj in page.get('Contents', []):
            if obj['Size'] > 0 or include_empty_keys:
                yield obj['Key']


def fetch(url, bucket=None, key=None, uri=None, s3_resource=None, **kwargs):
    """
    Retrieves the data defined by a URL to an S3 location.
    :param url: URL to retrieve
    :param bucket: The S3 bucket for the object
    :param key: The key of the object
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The URI of the object written to S3
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    req = Request(url, **kwargs)
    with request.urlopen(req) as response:
        return write_object(response.read(), bucket=bucket, key=key, s3_resource=s3_resource)


def download(directory, bucket=None, key=None, uri=None, use_threads=True, s3_resource=None):
    """
    Downloads the an S3 object to a directory on the local file system.
    :param directory: The directory to download the object to
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param use_threads: Enables the use_threads transfer config
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: Path of the local file
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    config = TransferConfig(use_threads=use_threads)
    s3_object_local = os.path.join(directory, key.split('/')[-1])
    try:
        s3_resource.Bucket(bucket).download_file(key, s3_object_local, Config=config)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    return s3_object_local


def upload(file_name, bucket=None, key=None, uri=None, s3_resource=None):
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    s3_resource.Bucket(bucket).upload_file(file_name, key)
    return compose_uri(bucket, key)


def download_to_temp(bucket=None, key=None, uri=None, s3_resource=None):
    """
    Downloads the an S3 object to a temp directory on the local file system.
    :param bucket: The S3 bucket for object to retrieve
    :param key: The key of the object to be retrieved from the bucket
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: Path of the local file
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    temp_dir = _create_temp_dir()
    file = os.path.join(temp_dir, key.split('/')[-1])
    if not os.path.isfile(file):
        print('starting download')
        download(temp_dir, bucket, key, use_threads=True, s3_resource=s3_resource)
        print('download complete')
    return file


def _create_temp_dir():
    """
    Creates a temp directory in the current path.
    :return: The path of the temp directory
    """
    _temp_dir = os.getcwd() + "/temp"
    if not os.path.isdir(_temp_dir):
        os.makedirs(_temp_dir)
    return _temp_dir


def make_public(bucket=None, key=None, uri=None, s3_resource=None):
    """
    Makes the object defined by the bucket/key pair (or uri) public.
    :param bucket: The S3 bucket for object
    :param key: The key of the object
    :param uri: An s3:// path containing the bucket and key of the object
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :return: The URL of the object
    """
    s3_resource = s3_resource if s3_resource else resource
    if uri:
        (bucket, key) = decompose_uri(uri)
    s3_resource.meta.client.put_object_acl(Bucket=bucket, Key=key, ACL='public-read')
    return get_public_url(bucket=bucket, key=key)


def get_public_url(bucket=None, key=None, uri=None):
    """
    Returns the public URL of an S3 object (assuming it's public).
    :param bucket: The S3 bucket for object
    :param key: The key of the object
    :param uri: An s3:// path containing the bucket and key of the object
    :return: The URL of the object
    """
    if uri:
        (bucket, key) = decompose_uri(uri)
    return 'https://{}.s3.amazonaws.com/{}'.format(bucket, parse.quote(key))


def create_bucket(bucket, acl='private', region=__session.region_name, s3_resource=None):
    s3_resource = s3_resource if s3_resource else resource
    bucket_obj = s3_resource.Bucket(bucket)
    bucket_obj.load()
    if bucket_obj.creation_date is None:
        bucket_obj.create(ACL=acl, CreateBucketConfiguration={'LocationConstraint': region})
        bucket_obj.wait_until_exists()
    return bucket_obj


def delete_bucket(bucket, s3_resource=None):
    s3_resource = s3_resource if s3_resource else resource
    bucket_obj = s3_resource.Bucket(bucket)
    bucket_obj.delete()


def get_temp_bucket(region=None, s3_resource=None, bucket_identifier=None):
    """
    Create a bucket that will be used as temp storage for larry commands.
    The bucket will be created in the region associated with the current session
    using a name based on the current session account id and region.
    :param region: Region to locate the temp bucket
    :param s3_resource: Boto3 resource to use if you don't wish to use the default resource
    :param bucket_identifier: The bucket identifier to use as a unique identifier for the bucket, defaults to the
    account id associated with the session
    :return: The name of the created bucket
    """
    if region is None:
        region = __session.region_name
    if bucket_identifier is None:
        bucket_identifier = sts.account_id()
    bucket = '{}-larry-{}'.format(bucket_identifier, region)
    create_bucket(bucket, region=region, s3_resource=s3_resource)
    return bucket


# TODO: add filter parameter
# TODO: rationalize the list params
def download_to_zip(file, bucket, prefix=None, prefixes=None):
    if prefix:
        prefixes = [prefix]
    with ZipFile(file, 'w') as zfile:
        for prefix in prefixes:
            for key in list_objects(bucket, prefix):
                zfile.writestr(parse.quote(key), data=read_object(bucket, key))


def file_name_portion(uri):
    file = decompose_uri(uri)[1].split('/')[-1]
    return file[:file.rfind('.')]
