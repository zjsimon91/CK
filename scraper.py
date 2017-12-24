#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests, re, os, time, json, pprint, itertools, pandas as pd, datetime
from random import *
from mysqlConn import MySqlConn
from selenium import webdriver


def iter_grouper(n, iterable):
    it = iter(iterable)
    item = itertools.islice(it, n)
    while item:
        yield item
        item = itertools.islice(it, n)


def userAgent():
    agents = ["Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
              "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3",
              "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
              "Opera/9.00 (Windows NT 5.1; U; en)",
              "Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522+ (KHTML, like Gecko) Safari/419.3",
              "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3",
              "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, Like Gecko) Version/6.0.0.141 Mobile Safari/534.1+"]
    return agents[randint(0, len(agents) - 1)]


def clean(x): return re.sub("^\s*|\s*$", "", x)


class KittyScratcher:
    def __init__(self):
        self.ids = []
        for root, dirs, files in os.walk("Pages"):
            for file in files:
                self.ids.append(int(file.split('.')[0]))

    def getSite(self, id):
        time.sleep(random() + .2)
        url = "https://cryptokittydex.com/kitties/{id}".format(id=id)
        headers = {
            'User-Agent': userAgent(),
            'From': 'youremail@domain.com'  # This is another valid field
        }

        r = requests.get(url, headers=headers)

        return r

    def getInfo(self, id):
        t = self.getSite(id)
        t = open("Pages/{id}.html".format(id=id), 'r').read()

        soup = BeautifulSoup(t, "lxml")
        d = {"id": id}

        geneList = soup.find('ul', class_="list-unstyled list-inline list-genes")
        geneList = [clean(each.text) for each in geneList.findAll('li')]
        d['genetics'] = geneList

        parents = soup.find('h4', text="Parents").find_next_siblings("a", class_="kitty")[:2]
        parents = [int(clean(each['href'].split('/')[-1])) for each in parents]
        d['parents'] = parents

        kids = soup.find('h4', text="Bebehs").find_next_siblings('li')
        kids = [int(each.find('div', class_='kitty-number').text) for each in kids]
        d['kids'] = kids

        info_block = soup.find('ul', class_='list-unstyled')
        info = info_block.find_all('li')
        d['owner'] = clean(info[0].text.split(':')[1])
        d['born'] = clean(info[1].text.split(':')[1])
        d['generation'] = int(clean(info[2].text.split(':')[1]))
        d['block_number'] = (clean(info[3].text.split(':')[1]))
        d['block_hash'] = (clean(info[4].text.split(':')[1]))
        d['tags'] = [each.text for each in info[-1].find_all("a")]

        sales = soup.find('h4', text="Sale history").find_next_siblings('table')
        try:
            if sales:
                sales = sales[0].find_all('tr')[-1]
                price, date = sales.find_all('td')
                d['last_price'] = re.search('\d+\.\d+', price.text).group(0)
                d['last_time_sold'] = str(datetime.datetime.strptime(clean(date.text), '%b. %d, %Y,  %H:%M %p UTC'))
            else:
                d['last_price'] = 0
                d['last_time_sold'] = str(datetime.datetime(1970, 1, 1))
        except:
            pass
        return d

    def savePage(self, id, recursive=0):
        if id in self.ids:
            print "saved"
            return ""

        r = self.getSite(id)
        code = r.status_code
        if code == 200:
            with open("Pages/{id}.html".format(id=id), "w") as f:
                f.write(r.text)
                self.ids.append(id)
            print "got", id
        else:
            print code
            print r.text
            time.sleep(20)
            if 0 < recursive <= 3:
                return self.savePage(id, recursive=recursive + 1)
        return r

    def prepMainTable(self, d):
        cat = {}
        cat['id'] = d['id']
        cat['block_hash'] = d['block_hash']
        cat['block_number'] = d['block_number']
        cat['born'] = str(datetime.datetime.strptime(d['born'], '%B %d, %Y at %H'))
        cat['generation'] = d['generation']
        cat['genetics'] = "".join(d['genetics'])
        if d["parents"]:
            a, b = d['parents']
        else:
            a, b = 0, 0
        cat['parent_x'] = a
        cat['parent_y'] = b

        genetics = bin(int("".join(d['genetics']), 16))[2:].zfill(len(d['genetics']) * 4)
        genetics = [{"cat_id": d['id'], "digit": i, 'value': each} for i, each in enumerate(genetics)]
        tags = [{"cat_id": d['id'], "tag": each} for each in d['tags']]

        return [cat, genetics, tags]

    def getTagCats(self, tag, pages=3):

        headers = {
            'User-Agent': userAgent(),
            'From': 'youremail@domain.com'  # This is another valid field
        }

        cats = []
        for i in range(1, pages + 1):
            url = "https://cryptokittydex.com/cattributes/{tag}?page={page}".format(tag=tag, page=i)
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            ul = soup.find('ul', class_='list-unstyled list-inline list-kitties')
            cats.extend([int(each['href'].split('/')[2]) for each in ul.find_all('a', class_="kitty")])

        time.sleep(10)
        for each in cats:
            self.savePage(each)

    def scrapeMarketPlace(self, pages=3):
        driver = webdriver.Chrome(executable_path=r'/Users/admin/Desktop/PythonWork/chromedriver')
        conn = MySqlConn()
        cats = []
        for i in range(1, pages + 1):
            url = "https://www.cryptokitties.co/marketplace/sale/{0}".format(i)
            url = url + "?orderBy=current_price&orderDirection=asc&search=gen%3A3%20cooldown%3Aswift&sorting=cheap"
            driver.get(url)
            time.sleep(5)
            htmlSource = driver.page_source
            soup = BeautifulSoup(htmlSource, 'lxml')
            grid = soup.find('div', class_="KittiesGrid")
            cats = grid.find_all('div', class_="KittiesGrid-item")
            df = pd.DataFrame([ks.parseBid(each) for each in cats])
            conn.insertDF(df, 'crypto.marketplace', 'REPLACE')
            conn.db.commit()

    def parseBid(self, s):
        status = s.find('div', class_="KittyCard-status")
        price = status.find('span', class_="KittyStatus-note")
        price = re.search('\d+\.\d+', price.text).group(0)
        cooldown = s.find('div', class_="KittyCard-coldown").text
        details = s.find('div', class_="KittyCard-subname").text.split()
        id, gen = map(int, [details[1], details[-1]])
        return {'id': id, "generation": gen, "cooldown": cooldown, "price": price}


def quickScrape():
    ks = KittyScratcher()
    q = """SELECT parent from (
                  SELECT parent_x AS parent
                  FROM crypto.cat
                  UNION SELECT parent_y
                        FROM crypto.cat
            ) as p
                  LEFT JOIN crypto.cat c
                  on p.parent = c.id
            WHERE parent <> 0 and c.id is NULL """

    conn = MySqlConn()
    for i in range(1000):
        try:
            checkList = conn.getFrame(q)['parent'].values
            finishedList = list(ks.ids)

            if len(checkList) == 0:
                checkList = [random() * 100000 for i in range(2000)]
                shuffle(checkList)
            print len(checkList), "starting scrape loop"
            for each in checkList:
                r = ks.savePage(each)
        except Exception, e:
            time.sleep(5)
            print "bug", e
        # quickScrape()
        print "inserted new"


def tosql():
    ks = KittyScratcher()
    conn = MySqlConn()
    ids = conn.getFrame("""SELECT id from crypto.marketplace m
                            LEFT JOIN crypto.cat c USING (id)
                            WHERE c.id is NULL;""")['id'].values
    print ids

    for each in iter_grouper(500, ids):
        s = datetime.datetime.now()
        cat, genetics, tags = [], [], []
        for id in each:
            try:
                ks.savePage(id,1)
                info = ks.getInfo(id)
            except Exception, e:
                print id
                raise e
            c, g, t = ks.prepMainTable(info)
            cat.append(c)
            genetics.extend(g)
            tags.extend(t)

        if len(cat) == 0: return ""
        cat = pd.DataFrame(cat)
        genetics = pd.DataFrame(genetics)
        tags = pd.DataFrame(tags)

        conn.insertDF(cat, 'crypto.cat')
        conn.insertDF(genetics, 'crypto.genetics')
        conn.insertDF(tags, 'crypto.tags')
        conn.db.commit()

        print "chunked", datetime.datetime.now() - s


if __name__ == "__main__":
    # quickScrape()
    tosql()
    # ks = KittyScratcher()
    # ks.scrapeMarketPlace(2)



    # r = requests.get("https://api.cryptokitties.co/kitties/123606")
    # print r.json()

    # ks.getTagCats('mainecoon',5)
    # print ks.savePage(1999)
    # print ks.getInfo(1999)
