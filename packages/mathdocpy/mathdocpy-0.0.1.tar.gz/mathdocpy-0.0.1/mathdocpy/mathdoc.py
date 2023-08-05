from typing import Dict
import json
import subprocess
from mathdocpy.file_utils import get_regular_path, is_acceptable_file

class Mathdoc:
    def __init__(self, file_location: str):
        if is_acceptable_file(file_location):
            self.file_location = get_regular_path(file_location)
        else:
            raise FileNotFoundError("The file filename not found.".replace("filename", file_location))
    
    def compile(self) -> str:
        return subprocess.check_output(["mathdoc", "--compile", self.file_location], stderr=subprocess.DEVNULL).decode('utf-8')
    
    def getAST(self) -> dict:
        return json.loads(
            subprocess.check_output(["mathdoc", "--getast", self.file_location], stderr=subprocess.DEVNULL)
        )
    
    def getConfig(self) -> Dict[str, str]:
        return json.loads(
            subprocess.check_output(["mathdoc", "--getast", self.file_location, "--config-only"], stderr=subprocess.DEVNULL)
        )
