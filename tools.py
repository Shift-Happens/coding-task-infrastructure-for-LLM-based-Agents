from typing import List
import os
import glob
from langchain.tools import BaseTool
from pathlib import Path

class FileSystemTool(BaseTool):
    name = "filesystem"
    description = "Perform file system operations"

    def _run(self, command: str) -> str:
        operations = {
            'list': self._list_files,
            'read': self._read_file,
            'write': self._write_file,
            'search': self._search_content,
            'rename': self._rename_file
        }
        op, *args = command.split('|')
        return operations[op](*args)

    def _list_files(self, pattern: str) -> str:
        return "\n".join(glob.glob(pattern))

    def _read_file(self, filepath: str) -> str:
        return Path(filepath).read_text()

    def _write_file(self, filepath: str, content: str) -> str:
        Path(filepath).write_text(content)
        return f"Written to {filepath}"

    def _search_content(self, pattern: str, text: str) -> bool:
        return text.find(pattern) != -1

    def _rename_file(self, old: str, new: str) -> str:
        os.rename(old, new)
        return f"Renamed {old} to {new}"
