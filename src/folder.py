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
        """
        
        return ['samba', 'cube-image/', 'cube-t-b/', '1.0.6-rc42/', 
        ['at91bootstrap.bin', 
        'cube-image-cube-t-b.ubifs.cube-image-cube-t-b-20240325173504-1.0.6-rc42-.ubi',
          'u-boot.bin']]

        """
        self.path_to_file = []
        # cube-image
        for config_cube_sw, config_cube_types in self.config_folder_map.items():
            #   cube-t-b    
            for config_cube_type, config_settings in config_cube_types.items():    
                if "version" in config_settings["settings"]: 
                    config_settings_version = config_settings["settings"]["version"]
                else: 
                    config_settings_version = "all"

                if "items" in config_settings["settings"]: 
                    config_settings_items = config_settings["settings"]["items"]
                else: 
                    config_settings_items = ["samba", "samba-100hz"]

                if config_cube_type in self.files_struct:      
                    # rc40, {cube-image:{...}, cube-transport-image{...}, ...} 
                    for version_sw_in_file_struct, version_images_in_file_struct in self.files_struct[config_cube_type].items():
                        
                        path_to_files = []
                        #cube-image есть в {cube-image:{...}, cube-transport-image{...}, ...} 
                        if config_cube_sw in version_images_in_file_struct:
                            for version_image_in_file_struct, files_types_in_file_struct in version_images_in_file_struct.items():
                                #   cube-image     cube-image
                                if version_image_in_file_struct == config_cube_sw:
                                    for item in config_settings_items:  #  берем типы файлов из folder_map

                                        if item in files_types_in_file_struct:          #  если этот файл есть в структуре файлов
                                            tmp_path_to_file = [item, version_image_in_file_struct, config_cube_type, version_sw_in_file_struct, []]
                                            for number_file_in_file_struct, file_in_file_struct in files_types_in_file_struct[item].items():
                                                tmp_path_to_file[4].append(file_in_file_struct)
                                            if config_settings_version == "latest" and len(path_to_files) != 0 :


                                                if path_to_files[0][3] < tmp_path_to_file[0][3]:
                                                
                                                    path_to_files[0] = tmp_path_to_file
                                            else:
                                                path_to_files.append(tmp_path_to_file)
                        self.path_to_file.append(path_to_files)
                                                
                                    # temp_path : str = config_cube_type + version_sw_in_file_struct + version_image_in_file_struct
                                    # self.path_to_file.append(temp_path)
            

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
    # for i in test.path_to_file:
    #     print(i)
    #     print()
    print(test.path_to_file)