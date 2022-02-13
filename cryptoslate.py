import csv
import os.path
import threading
import traceback

import requests
from bs4 import BeautifulSoup

filename = "cryptoslate.csv"
headers = ['#', 'Coin', 'Sym', 'Info Page', 'Marketcap', 'Price', '24h volume', 'Circ. Supply', 'BC', '24hr', '7d',
           'URL']

threadcount = 25
semaphore = threading.Semaphore(threadcount)
writelock = threading.Lock()
data = ""


def get(tr, cls, convert=False):
    txt = tr.find('td', {'class': cls}).text.strip()
    m = {'K': 3, 'M': 6, 'B': 9, 'T': 12}
    if convert and txt[-1] in m.keys():
        txt = txt.replace(',', '').replace("$", "")
        return "${:,}".format(int(float(txt[:-1]) * 10 ** m[txt[-1]] / 1000))
    return txt


def scrape(u):
    semaphore.acquire()
    soup = BeautifulSoup(requests.get(u).content, 'lxml')
    for tr in soup.findAll('tr'):
        if tr.find('td', {'class': 'col rank'}) is not None:
            name = tr.find('td', {'class': 'col name'})
            info = name.find('a')['href']
            try:
                if info not in data:
                    try:
                        url = BeautifulSoup(requests.get(info).content, 'lxml').find('a', {'class': 'btn website'})[
                            'href']
                    except:
                        url = "Not avl"
                    row = [
                        get(tr, 'col rank'),
                        name.a.find(text=True, recursive=False).strip(),
                        name.span.text.strip(),
                        info,
                        get(tr, 'col market-cap', True),
                        get(tr, 'col price', True),
                        get(tr, 'col volume', True),
                        get(tr, 'col supply', True),
                        get(tr, 'col blockchain'),
                        get(tr, 'col change-24h'),
                        get(tr, 'col change-7d'),
                        url
                    ]
                    print(row)
                    append(filename, row)
            except:
                traceback.print_exc()
                row = [info, name.text, u]
                print("Error: ", row)
                append("cryptoslate-error.csv", row)
    semaphore.release()


def append(file, row):
    with writelock:
        with open(file, 'a', encoding='utf8', errors='ignore', newline='') as outfile:
            csv.writer(outfile).writerow(row)


def main():
    os.system('color 0a')
    logo()
    global data
    if not os.path.isfile(filename):
        with open(filename, 'w', encoding='utf8', errors='ignore', newline='') as outfile:
            csv.writer(outfile).writerow(headers)
    else:
        with open(filename, 'r', encoding='utf8', errors='ignore', newline='') as outfile:
            data = outfile.read()
    print(f"Thread count: {threadcount}")
    print(headers)
    for i in range(1, 27):
        threading.Thread(target=scrape, args=(f'https://cryptoslate.com/coins/page/{i}/',)).start()


def logo():
    print("""
    _________                        __          _________.__          __          
    \_   ___ \_______ ___.__._______/  |_  ____ /   _____/|  | _____ _/  |_  ____  
    /    \  \/\_  __ <   |  |\____ \   __\/  _ \\\\_____  \ |  | \__  \\\\   __\/ __ \ 
    \     \____|  | \/\___  ||  |_> >  | (  <_> )        \|  |__/ __ \|  | \  ___/ 
     \______  /|__|   / ____||   __/|__|  \____/_______  /|____(____  /__|  \___  >
            \/        \/     |__|                      \/           \/          \/ 
============================================================================================
              CryptoSlate coins scraper by : fiverr.com/muhammadhassan7
============================================================================================
Features:\n1. Multithreaded\n2. Resumable(duplicate checker)\n""")


if __name__ == "__main__":
    main()
