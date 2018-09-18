import os
import hashlib
import binascii
import filetype
import datetime

def rebase_file_path(filename, prefix):
    if filename.startswith('/'):
        filepath = filename[1:]
    else:
        filepath = filename
    filedir = os.path.dirname(filepath)
    pfixroot = prefix.replace(filedir, '')
    if pfixroot == prefix:
        raise OSError('{} does not resolve to current directory'.format(filename))
    if pfixroot.endswith('/'):
        pfixroot = pfixroot[:-1]
    rebased_path = os.path.join(pfixroot, filepath)
    return rebased_path

def get_size_in_bytes(posix_path):
    """Safely returns file size in bytes"""
    if not os.path.exists(posix_path):
        raise OSError('{} not found'.format(posix_path))
    try:
        if os.path.isfile(posix_path):
            gs = os.path.getsize(posix_path)
            if gs is None:
                raise OSError('Failed to get size for {}'.format(posix_path))
            else:
                return gs
        elif os.path.isdir(posix_path):
            return 0
    except Exception as exc:
        raise OSError('Unexplained failure in get_size_in_bytes', exc)

def compute_checksum(posix_path, fake_checksum=False):
    """Approved method to generate SHA1 file checksums"""
    # mocking support
    if fake_checksum:
        return binascii.hexlify(os.urandom(20)).decode()
    if not os.path.exists(posix_path):
        raise OSError('{} not found'.format(posix_path))
    if not os.path.isfile(posix_path):
        raise OSError('{} is not a file'.format(posix_path))
    try:
        hash_sha = hashlib.sha1()
        with open(posix_path, "rb") as f:
            for chunk in iter(lambda: f.read(131072), b""):
                hash_sha.update(chunk)
        return hash_sha.hexdigest()
    except Exception as exc:
        raise OSError('Unexplained failure in compute_checksum', exc)

def validate_checksum(posix_path, known_checksum):
    """Validate checksum of a file and return Boolean response"""
    computed = compute_checksum(posix_path, False)
    if computed == known_checksum:
        return True
    else:
        return False

def guess_mimetype(posix_path, default='text/plaintext'):
    """Uses fingerprinting to figure out MIME type"""
    if not os.path.exists(posix_path):
        raise OSError('{} not found'.format(posix_path))
    if not os.path.isfile(posix_path):
        raise OSError('{} is not a file'.format(posix_path))
    try:
        ftype = filetype.guess(posix_path)
        if ftype is None:
            return default
        else:
            return ftype.mime
    except Exception as exc:
        raise OSError('Unexplained failure in guess_mimetype', exc)

def get_filetype(posix_path):
    # Returns the file type. This is a stub for more sophisticated mechanism
    return guess_mimetype(posix_path)

def get_modification_date(posix_path):
    t = os.path.getmtime(posix_path)
    return datetime.datetime.fromtimestamp(t)

def splitall(path):
    # Returns a list of all path elements
    # Ref: https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch04s16.html
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

