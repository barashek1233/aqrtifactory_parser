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


def search_new_links(links_list : list):
    """
    Фнукция делает get запрос по адресу указанному в параметре linls_list спику и возвращает список всех ссылкок по указанному адресу, 
    если в списке ошибка данных вернет спиок c одним занчением "Error links_list, если не удалось выполнить get запрос вернет None
    
    Параметры:
    links_list (list): пример: ["http://10.125.0.41/artifactory/aQsi-cube/release/cube-d/", "1.0.6-rc42/", "cube_image/"]
    
    Возвращает:
    list: если ошибка типа данных в ссылке : ["error", link, type(link), itter] -> "error": текст что ошибка, link: значение из за которой произошла ошибка, type(link): тип данных значения, itter: номер элемента в списке, начиная с 0.
    list: если нет ошибок вернет список ссылок со страницы.
    None: если не удалось выполнить get запрос
    """
    links_str : str = ""
    itter = 0
    logs.debug(f"links_list: {links_list}")
    for link in links_list:
        if type(link) != str:
            logs.debug(f"Error link, {link} is not type str/ WTF??")
            return ["error", link, type(link), itter]
        else:
            links_str = links_str + link
        itter = itter + 1
    
    return_list_links_on_page : list | None = getting_links(links_str, links_str)

    if return_list_links_on_page is None:
        logs.debug(f"return_list_links_on_page is None {return_list_links_on_page}")
        return return_list_links_on_page
    
    for link_on_page in return_list_links_on_page:
        if link_on_page == "../":
            logs.debug(f"removing value: '{link_on_page}' from response")
            return_list_links_on_page.remove(link_on_page)

    return return_list_links_on_page
        

def populating_the_dictionary_with_get_queries(main_link : list, type_cube : str, data_from_file_struct : dict) -> dict:
    test_dict = {}
    test_dict["sam-ba"] = ["1", "2", "3"]
    test_dict["sam-ba-100hz"] = ["1", "2", "3"]
    
    main_link.append(type_cube)
    logs.debug(f"main_link: {main_link}")
    list_links_on_page : list | None = search_new_links(main_link)
    logs.debug(f"list_links_on_page: {list_links_on_page}")
    if list_links_on_page is None:
        return list_links_on_page
    for item in list_links_on_page:
        # if item is not data_from_file_struct:
        logs.debug(f"item is not data_from_file_struct: {item}")
        if item[-1] == "/":
            logs.debug(f"item[-1] == / {item[-1]}")
            data_from_file_struct[item] = {}
            logs.debug(f"create item: {item} {data_from_file_struct[item]}")
            data_from_file_struct[item] = populating_the_dictionary_with_get_queries(main_link, item, data_from_file_struct[item])
        else:
            # написать фнукцию раскидывающую по версия самбы и сву пакеты пока типо она тут есть, и возвращает готовый словарь такого толка data_from_file_struct[type_cube] 
            logs.debug(f"return test_dict")
            return test_dict
            # data_from_file_struct[item] = populating_the_dictionary_with_get_queries(main_link, item, data_from_file_struct[item])
        main_link.pop()

    return data_from_file_struct
                
    # file_struct : dict = data_from_file_struct[type_cube]

    # if list_links_on_page is None:
    #     pass
    # elif list_links_on_page[0] == "error":
    #     pass
    
    
    



def main():
    load_dotenv()
    URL_T_B = os.getenv("URL")
    # URL_D = os.getenv("URL_D")
    FILE_STRUCT = os.getenv("FILE_STRUCT")

    # cube_t_b_links_to_versions = getting_links(URL_T_B, "cube-t-b/")
    # cube_d_links_to_versions = getting_links(URL_D, "cube-d")

    data_from_file_struct = check_file_struct(FILE_STRUCT)
    if len(data_from_file_struct) == 0:
        logs.info("File_struct not found? Creating")
        list_url = ["http://10.125.0.41/artifactory/aQsi-cube/prerelease/"]
        data_from_file_struct = populating_the_dictionary_with_get_queries(list_url, "cube-t-b/", data_from_file_struct)

    json_str = json.dumps(data_from_file_struct, indent=8)
    print(json_str)






if __name__ == "__main__":
    main()