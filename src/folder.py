import os
import json
from dotenv import load_dotenv
from log.logger import get_logger

class creator_folder():
    
    def __init__(self):
        load_dotenv()
        CONFIG_FOLDER_MAP = os.getenv("CONFIG_FOLDER_MAP")
        FILE_STRUCT = os.getenv("FILE_STRUCT")
        self.__logs = get_logger()
        with open(CONFIG_FOLDER_MAP, "r") as file:
            self.config_folder_map = json.load(file)
        with open(FILE_STRUCT, "r") as file:
            self.files_struct = json.load(file)


# "cube-image/": {
#         "cube-t-b/":{
#             "settings": {
#                 "version": "latest"
#             }
#         }

    def search(self, file_struct : dict, keys : str, settings : dict):
        pass

    def dowload(self, path_folder : str, keys : list, settings : dict):
        pass
    
    def create_and_download(self):
        for cube_version_po, cube_types in self.config_folder_map.items():
            path = [cube_version_po]
            os.makedirs("./test/".join(path), exist_ok=True)
            for cube_type, settings in cube_types.items():
                path.append(cube_type)
                
                os.makedirs("./test".join(path), exist_ok=True)
                self.dowload("./test".join(path), path, settings)
                path.pop()




if __name__ == "__main__":
    test = creator_folder()
    test.create_and_download()
