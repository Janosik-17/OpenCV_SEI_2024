from requests_html import HTMLSession
session = HTMLSession()
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

base_url = "https://bilgym.sk/"
koncovky = ["programy-a-projekty-skoly/", "nepedagogicka-podpora/", "kontakt-podporny-tim/", "kontakt-ucitelia/", "spravna-rada/", "kontakt-vedenie-skoly/"]

def scrape_site(url_input):
    img_list = []
    info_list = []
    url = base_url + url_input
    page = session.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    content = soup.find("div", class_="entry-content")
    content_divs = content.find_all("div", class_="wp-block-image")
    content_divs2 = content.find_all("figure", class_="wp-block-image size-large")
    content_info = content.find_all("h3", class_="wp-block-heading has-text-align-left")
    for div in content_divs:
        under_div = div.find("img")
        img_src = under_div.get("src")
        img_list.append(img_src.encode("utf-8"))
    for fig in content_divs2:
        under_fig = fig.find("img")
        img_src = under_fig.get("src")
        img_list.append(img_src.encode("utf-8"))
    for inf in content_info:
        under_inf = inf.find("strong")
        info = under_inf.get_text().encode("utf-8")
        info_list.append(info)
    print(img_list)
    print(info_list)
    return img_list, info_list

def scrape_all(koncovky):
    over_img_list = []
    over_info_list = []
    for num in range(0, 5):
        ret_img_list, ret_info_list = scrape_site(koncovky[num])
        over_img_list.append(ret_img_list)
        over_info_list.append(ret_info_list)
    return over_img_list, over_info_list


print(scrape_all(koncovky))
        
