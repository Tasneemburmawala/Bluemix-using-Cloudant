import hashlib
import os
def md5(file_upload):
    fname = file_upload.filename
    file_content = file_upload.read()

    fo = open(fname, "w")
    fo.write(file_content);
    hash_md5 = hashlib.md5()
    with open(os.path.abspath(fname), "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    # os.remove(fname)
    return hash_md5.hexdigest()
