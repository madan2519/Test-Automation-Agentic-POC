import os
from config.settings import settings
from utils.logger import logger

class ScriptWriterTool:
    def __init__(self):
        self.storage_path = settings.SCRIPT_STORAGE_PATH
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def write_script(self, filename: str, content: str) -> str:
        try:
            file_path = os.path.join(self.storage_path, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Script written to: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error writing script: {e}")
            raise e

script_writer_tool = ScriptWriterTool()
