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
#         },
#         "cube-d/":{
#             "settings": {
#                 "version": "latest"
#             }
#         }
#     },

    def search(self, file_struct : dict, keys : str, settings : dict):
        for key, value in file_struct.items():
            if key in keys:
                pass

    def dowload(self):
        self.path_to_file = []
        # cube-image
        for cube_po, cube_types in self.config_folder_map.items():
            #   cube-t-b    
            for cube_type, settings in cube_types.items():
                #   rc40    
                if cube_type in self.files_struct:      
                    for version_po, version_images in self.files_struct[cube_type].items():
                        if cube_po in version_images:
                            for version_image, files_type in version_images.items():
                                temp_path : str = cube_type + version_po + version_image
                                self.path_to_file.append(temp_path)

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
    test.dowload()
    for i in test.path_to_file:
        print(i)