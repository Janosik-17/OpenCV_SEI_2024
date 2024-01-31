from requests_html import HTMLSession
session = HTMLSession()
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

base_url = "https://bilgym.sk/"
projektanti = "programy-a-projekty-skoly/"
nepedagogicka_podpora = "nepedagogicka-podpora/"
podporný_tím = "kontakt-podporny-tim/"
ucitelia = "kontakt-ucitelia/"
spravna_rada = "spravna-rada/"
vedenie = "kontakt-vedenie-skoly/"

def scrape_site(url_input):
    img_list = []
    info_list = []
    url = base_url + url_input
    page = session.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    content = soup.find("div", class_="entry-content")
    content_divs = content.find_all("div", class_="wp-block-image")
    for div in content_divs:
            under_div = div.find("img")
            img_src = under_div.get("src")
            img_list.append(img_src.encode("utf-8"))
            print(img_src.encode("utf-8"))
    print(img_list)
    print(info_list)
    return 0

scrape_site(ucitelia)
        
