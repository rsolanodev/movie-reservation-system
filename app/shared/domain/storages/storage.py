from typing import BinaryIO, Protocol


class Storage(Protocol):
    acl_policy: str = ""
    storage_path: str = ""
    fallback_content_type: str = "application/octet-stream"

    def upload_file(self, file: BinaryIO, name: str) -> str: ...
