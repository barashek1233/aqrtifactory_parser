import os
import json
import requests
from log.logger import get_logger
from dotenv import load_dotenv
from bs4 import BeautifulSoup

logs = get_logger()


def get_respons_from_url(url):
    try:
        respons = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        logs.error(f"A request error occurred: {e}")
        respons = None
    except requests.exceptions.ConnectionError as e:
        logs.error(f"Connection error: {e}")
        respons = None
    except requests.exceptions.Timeout as e:
        logs.error(f"Timeout exceeded: {e}")
        respons = None
    except requests.exceptions.TooManyRedirects as e:
        logs.error(f"Too many redirects: {e}")
        respons = None
    except requests.exceptions.HTTPError as e:
        logs.error(f"HTTP error: {e}")
        respons = None
    else:
        logs.info("Request completed successfully")
    return respons


def get_all_links_from_respons(response):
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a', href=True)]
    except AttributeError as e:
        logs.error(f"Error getting href: {e}")
        links = None
    except Exception as e:
        logs.error(f"Other error: {e}")
        links = None
    else:
        logs.info(f"Done")
        
    logs.debug(f"links: {links}")
    return links


def getting_links(URL : str, cube_name : str):
    logs.info(f"{cube_name} | Relise link : {URL}")
    response = get_respons_from_url(URL)

    if response is not None:
        logs.info(f"{cube_name} | Good Response, return links")
        links = get_all_links_from_respons(response)
    else:
        logs.error(f"{cube_name} | Respons is None Error")
        links = None

    return links


def check_file_struct(file_struct : str):
    try:
        with open(file_struct, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        logs.warning(f"File_struct: {file_struct} not found ALARM!!!!")  # вот тут надо буедет сделать логирование в телеграм потому что если этого файла нет программа запущена в первый раз или файл удалилс
        data = {}
    else:
        logs.info(f"File_struct: {file_struct} open")
    return data


def search_new_links(links : list):
    pass

def main():
    load_dotenv()
    URL_T_B = os.getenv("URL_T_B")
    URL_D = os.getenv("URL_D")
    FILE_STRUCT = os.getenv("FILE_STRUCT")

    cube_t_b_links_to_versions = getting_links(URL_T_B, "cube-t-b")
    # cube_d_links_to_versions = getting_links(URL_D, "cube-d")

    data_from_file_struct = check_file_struct(FILE_STRUCT)
    if len(data_from_file_struct) == 0:
        logs.info("File_struct not found? Creating")
        data_from_file_struct["cube-t-b/"] = {}

        for version in cube_t_b_links_to_versions:
            data_from_file_struct["cube-t-b/"][version] = {}
            cube_t_b_links_to_images = getting_links(URL_T_B + version, f"cube-t-b vers: {version}")

            for link_image in cube_t_b_links_to_images:
                if link_image == "cube-image/" or link_image == "cube-transport-image/":
                    data_from_file_struct["cube-t-b/"][version][link_image] = {}
                    cube_t_b_links_to_all_files = getting_links(URL_T_B + version + link_image, f"cube-t-b vers: {version} | image: {link_image}")
                    if cube_t_b_links_to_all_files is not None:  #  Добавить проверок на отуствие ероров и вообще переделать на переиспользование так как тут явно их можно прееиспользовать но как точно вопрос
                        data_from_file_struct["cube-t-b/"][version][link_image]["sam-ba"] = []
                        data_from_file_struct["cube-t-b/"][version][link_image]["sam-ba-100hz"] = [] 
                        key_ubi = 0
                        key_ubi_100hz = 0
                        for link_to_file in cube_t_b_links_to_all_files:
                            if "at91bootstrap.bin" in link_to_file:
                                data_from_file_struct["cube-t-b/"][version][link_image]["sam-ba"].append(link_to_file)
                                data_from_file_struct["cube-t-b/"][version][link_image]["sam-ba-100hz"].append(link_to_file)
                            elif ".ubi" in link_to_file:
                                if "100hz" in link_to_file and key_ubi_100hz == 0:
                                    data_from_file_struct["cube-t-b/"][version][link_image]["sam-ba-100hz"].append(link_to_file)
                                    key_ubi_100hz = 1
                                else:
                                    if key_ubi == 0:
                                        data_from_file_struct["cube-t-b/"][version][link_image]["sam-ba"].append(link_to_file)
                                        key_ubi = 1
                            elif "u-boot.bin" in link_to_file:
                                data_from_file_struct["cube-t-b/"][version][link_image]["sam-ba"].append(link_to_file)
                                data_from_file_struct["cube-t-b/"][version][link_image]["sam-ba-100hz"].append(link_to_file)

    json_str = json.dumps(data_from_file_struct, indent=4)
    print(json_str)






if __name__ == "__main__":
    main()