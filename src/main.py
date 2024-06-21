import os
import requests
from log.logger import get_logger
from dotenv import load_dotenv
from bs4 import BeautifulSoup

logs = get_logger()


def get_respons_from_url(url):
    logs = get_logger()
    try:
        respons = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        logs.error(f"Произошла ошибка запроса: {e}")
        respons = None
    except requests.exceptions.ConnectionError as e:
        logs.error(f"Ошибка соединения: {e}")
        respons = None
    except requests.exceptions.Timeout as e:
        logs.error(f"Превышен таймаут: {e}")
        respons = None
    except requests.exceptions.TooManyRedirects as e:
        logs.error(f"Слишком много перенаправлений: {e}")
        respons = None
    except requests.exceptions.HTTPError as e:
        logs.error(f"HTTP ошибка: {e}")
        respons = None
    return respons

def get_all_links_from_respons(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a', href=True)]

    for link in links:
        print(link)

def main():
    load_dotenv()
    URL = os.getenv("URL")
    response = get_respons_from_url(URL)

    if response is not None:
        get_all_links_from_respons(response)
    elif response is None:
        print(None)


if __name__ == "__main__":
    main()