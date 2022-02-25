import requests
from bs4 import BeautifulSoup as bs

def get_free_proxies():
    url = "https://free-proxy-list.net/"
    soup = bs(requests.get(url).content, "html.parser")
    soup_text = soup.find("textarea", {"class": "form-control"}).text
    ips_list = soup_text.splitlines()[3:]
    ips_list = ['http://' + item for item in ips_list]
    return ips_list

if __name__ == '__main__':
    print(get_free_proxies())