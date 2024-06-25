import os
import json
import requests
from log.logger import get_logger
from dotenv import load_dotenv
from bs4 import BeautifulSoup

logs = get_logger()

with open("config_file_struct.json", "r") as file:
    config_file_struct = json.load(file)



def get_respons_from_url(url : str):
    """
    Ункция выполняет get запрос по адресу указанному в передаваемом значении
    При возникновении ошибки вернет None

    Принимает: url(str)

    Возвращает: requests.Response | None 
    """
    try:
        respons = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        logs.error(f"get_respons_from_url | A request error occurred: {e}")
        respons = None
    except requests.exceptions.ConnectionError as e:
        logs.error(f"get_respons_from_url | Connection error: {e}")
        respons = None
    except requests.exceptions.Timeout as e:
        logs.error(f"get_respons_from_url | Timeout exceeded: {e}")
        respons = None
    except requests.exceptions.TooManyRedirects as e:
        logs.error(f"get_respons_from_url | Too many redirects: {e}")
        respons = None
    except requests.exceptions.HTTPError as e:
        logs.error(f"get_respons_from_url | HTTP error: {e}")
        respons = None
    else:
        logs.info("get_respons_from_url | Request completed successfully")
    return respons


def get_all_links_from_respons(response):
    """
    Функция ищет в теле ответа все ссылки
    При возникновении ошибки вернет None 
    
    Принимает: respons (Respons)
    Возвращает: list | None
    """
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a', href=True)]
    except AttributeError as e:
        logs.error(f"get_all_links_from_respons| Error getting href: {e}")
        links = None
    except Exception as e:
        logs.error(f"get_all_links_from_respons | Other error: {e}")
        links = None
    else:
        logs.info(f"get_all_links_from_respons | Done")
        
    logs.debug(f"get_all_links_from_respons | links: {links}")
    return links


def getting_links(URL : str):
    """
    Функция принимает URL с которого нужно получить ссылки все ссылки.
    Вызывает функцию которая делает get запрос.
    Возвращает None если ошибка запроса или ошибка с поиском ссылок на странице.
    Если ошибок нет вернет список всех ссылок со страницы

    Принимает: URL (str)

    Возвращает: None | List
    """
    logs.info(f"getting_links | Relise link : {URL}")
    response = get_respons_from_url(URL)

    if response is not None:
        logs.info(f"getting_links | {URL} | Good Response, return links")
        links = get_all_links_from_respons(response)
    else:
        logs.error(f"getting_links | {URL} | Respons is None Error")
        links = None

    return links


def check_file_struct(file_name : str) -> dict:
    """
    Функция проверки наличия файла передаваемого в парматре file_name
    Если файла нет или файл не JSON, вернет пустой словарь
    Если файл есть, вернет словарь со значениями из файла

    Принимает: file_name (str): путь до файла
    
    Возвращает: dict
    """
    data = {}
    if ".json" not in file_name:
        logs.warning(f"file name: {file_name} < need .json")
        return data
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        logs.warning(f"check_file_struct | file_name: {file_name} not found ALARM!!!!")  # вот тут надо буедет сделать логирование в телеграм потому что если этого файла нет программа запущена в первый раз или файл удалилс
    else:
        logs.info(f" check_file_struct | file_name: {file_name} open")
    return data


def search_new_links(links_list : list):
    """
    Фнукция делает get запрос по адресу указанному в параметре linls_list спику и возвращает список всех ссылкок по указанному адресу, 
    если в списке ошибка данных, вернет None, если не удалось выполнить get запрос вернет None
    
    Параметры:
    links_list (list): пример: ["http://10.125.0.41/artifactory/aQsi-cube/release/cube-d/", "1.0.6-rc42/", "cube_image/"]
    
    Возвращает:
    list: если нет ошибок вернет список ссылок со страницы.
    None: если не удалось выполнить get запрос или проблема в ссылке
    """
    links_str : str = ""
    logs.debug(f"search_new_links | links_list: {links_list}")
    for link in links_list:
        if type(link) != str:
            logs.warning(f"search_new_links | Error link, {link} | type: {type(link)} | is not type str/ WTF??")
            return None
        else:
            links_str = links_str + link
    
    return_list_links_on_page = getting_links(links_str)

    if return_list_links_on_page is None:
        logs.warning(f"search_new_links | return_list_links_on_page is None {return_list_links_on_page}")
        return return_list_links_on_page
    
    for link_on_page in return_list_links_on_page:
        if link_on_page == "../":
            logs.debug(f"search_new_links | removing value: '{link_on_page}' from response")
            return_list_links_on_page.remove(link_on_page)

    return return_list_links_on_page
        

# {
#     "samba": {
#         "1" : [[1, "at91bootstrap.bin"]], 
#         "2" : [[1, ".ubi"], [0, "100hz"]],
#         "3" : [[1, "u-boot.bin"]]
#     },
#     "samba-100hz" : {
#         "1" : [[1, "at91bootstrap.bin"]], 
#         "2" : [[1, ".ubi"], [1, "100hz"]],
#         "3" : [[1, "u-boot.bin"]]
#     },
#     "swupdate" : {
#         "1" : [[1, "at91bootstrap"], [1, ".swu.bin" ], [0, "100hz"]],
#         "2" : [[1, "bootloader"], [1, ".swu.bin" ], [0, "100hz"]],
#         "3" : [[1, "recovery"], [1, ".swu.bin" ], [0, "100hz"]],
#         "4" : [[1, "rootfs"], [1, ".swu.bin" ], [0, "100hz"]]
#     },
#     "swupdate-100hz" : {
#         "1" : [[1, "at91bootstrap"], [1, ".swu.bin" ], [1, "100hz"]],
#         "2" : [[1, "bootloader"], [1, ".swu.bin" ], [1, "100hz"]],
#         "3" : [[1, "recovery"], [1, ".swu.bin" ], [1, "100hz"]],
#         "4" : [[1, "rootfs"], [1, ".swu.bin" ], [1, "100hz"]]
#     } 
# }    ->    config_file_struct : dict

def file_type_check(item : str, data_from_file_struct : list):  #  подкгружаем конфиги файлаов
    for name_group_file_name, rules_all_files in config_file_struct.items():         # rules_all_files -> "1" : [[1, "at91bootstrap"], [1, ".swu.bin" ], [0, "100hz"]],
        for number_file, rule_for_file in rules_all_files.items():                   # rule_for_file   -> [[1, "at91bootstrap"], [1, ".swu.bin" ], [0, "100hz"]]
            flag : int = 1
            for rule in rule_for_file:
                if rule[0] == 1:   #   true то есть значение должно быть
                    if rule[1] in item:
                        flag = 1
                    else:
                        flag = 0
                elif rule[0] == 0: #   flase то есть значения не должно быть
                    if rule[1] not in item:
                        flag = 1
                    else:
                        flag = 0
            if flag == 1:
                if name_group_file_name not in data_from_file_struct:
                    logs.debug(f"file_type_check | {name_group_file_name} not in {data_from_file_struct}")
                    data_from_file_struct[name_group_file_name] = {number_file: item}
                else:
                    logs.debug(f"file_type_check | {name_group_file_name} in {data_from_file_struct}")
                    if number_file in data_from_file_struct[name_group_file_name]:
                        if data_from_file_struct[name_group_file_name][number_file] < item:
                            data_from_file_struct[name_group_file_name][number_file] = item



def populating_the_dictionary_with_get_queries(main_link : list, type_link : str, data_from_file_struct : dict) -> dict:
    
    main_link.append(type_link)
    logs.debug(f"populating_the_dictionary_with_get_queries | main_link: {main_link}")

    list_links_on_page : list | None = search_new_links(main_link)
    logs.debug(f"populating_the_dictionary_with_get_queries | list_links_on_page: {list_links_on_page}")
    if list_links_on_page is None:
        return None
    for item in list_links_on_page:
        # if item is not data_from_file_struct:
        logs.debug(f"populating_the_dictionary_with_get_queries | item is not data_from_file_struct: {item}")
        if item[-1] == "/":
            logs.debug(f"item[-1] == /")
            data_from_file_struct[item] = {}
            logs.debug(f"populating_the_dictionary_with_get_queries | create item: {item} {data_from_file_struct[item]}")
            data_from_file_struct[item] = populating_the_dictionary_with_get_queries(main_link, item, data_from_file_struct[item])
        else:
            file_type_check(item, data_from_file_struct)
            # if "swu.bin" in item:
            #     logs.debug(f"populating_the_dictionary_with_get_queries | File for swupdate: {item} found")
            #     if 'file_swupdate' not in data_from_file_struct:
            #         logs.debug(f"populating_the_dictionary_with_get_queries | file_swupdate not in data_from_file_struct, creating and adding {item}")
            #         data_from_file_struct["file_swupdate"] = [item]
            #     else:
            #         logs.debug(f"populating_the_dictionary_with_get_queries | file_swupdate in data_from_file_struct, adding {item}")
            #         data_from_file_struct["file_swupdate"].append(item)

            # elif ".bin" in item or ".ubi" in item:
            #     logs.debug(f"populating_the_dictionary_with_get_queries | File samba: {item} found")
            #     if 'file_samba' not in data_from_file_struct:
            #         logs.debug(f"populating_the_dictionary_with_get_queries | file_samba not in data_from_file_struct, creating and adding {item}")
            #         data_from_file_struct["file_samba"] = [item]
            #     else:
            #         logs.debug(f"populating_the_dictionary_with_get_queries | file_samba in data_from_file_struct, adding {item}")
            #         data_from_file_struct["file_samba"].append(item)
            # else:
            #     logs.debug(f"populating_the_dictionary_with_get_queries | Other file: {item} found")
            #     if 'file_other' not in data_from_file_struct:
            #         logs.debug(f"populating_the_dictionary_with_get_queries | file_other not in data_from_file_struct, creating and adding {item}")
            #         data_from_file_struct["file_other"] = [item]
            #     else:
            #         logs.debug(f"populating_the_dictionary_with_get_queries | file_other in data_from_file_struct, adding {item}")
            #         data_from_file_struct["file_other"].append(item)
    logs.debug(f"populating_the_dictionary_with_get_queries | {main_link} pop {main_link[-1]}")
    main_link.pop()

    return data_from_file_struct
                
    # file_struct : dict = data_from_file_struct[type_link]

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