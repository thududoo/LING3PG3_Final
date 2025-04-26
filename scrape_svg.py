import requests
from bs4 import BeautifulSoup

links = [
    "https://commons.wikimedia.org/wiki/File:Hubei_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Guangxi_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Guizhou_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Jiangsu_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Henan_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Beijing_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Liaoning_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Qinghai_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Sichuan_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Xinjiang_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Chongqing_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Jilin_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Tibet_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Guangdong_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Hebei_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Jiangxi_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Shandong_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Ningxia_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Hainan_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Heilongjiang_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Zhejiang_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Tianjin_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Yunnan_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Shanghai_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Gansu_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Anhui_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Fujian_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Hunan_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Shaanxi_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Shanxi_locator_map_(China).svg", 
    "https://commons.wikimedia.org/wiki/File:Inner_Mongolia_locator_map_(China).svg", 
]

svgs = []

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}


for link in links:
    r = requests.get(link)
    # print(r.content)
    soup = BeautifulSoup(r.content, "html.parser")
    url = soup.find("a", {"class": "internal"}).get("href")
    print(url)
    svgs.append(url)

for svg_lnk in svgs:
    s = requests.get(svg_lnk, headers=headers).text
    svg_mame = svg_lnk.split("/")[-1].split("_")[0]+".svg"
    open(f"./data/{svg_mame}", "w").write(s)