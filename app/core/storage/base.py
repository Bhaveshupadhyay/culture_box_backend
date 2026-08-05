from abc import ABC, abstractmethod
from typing import BinaryIO, Union, IO

class StorageProvider(ABC):
    @abstractmethod
    async def upload_file(self, file_content: Union[bytes, IO[bytes]], file_path: str, content_type: str) -> str:
        """
        Uploads a file (raw bytes or binary file stream) and returns the public or signed URL.
        """
        pass
        
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Deletes a file by its path.
        """
        pass
        
    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """
        Returns the public or signed URL for a given file path.
        """
        pass
