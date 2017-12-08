from bs4 import BeautifulSoup
import requests,re
from random import *

def userAgent():
    agents = ["Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
                "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3",
                "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
                "Opera/9.00 (Windows NT 5.1; U; en)",
                "Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522+ (KHTML, like Gecko) Safari/419.3",
                "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3",
                "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, Like Gecko) Version/6.0.0.141 Mobile Safari/534.1+"]
    return agents[randint(0,len(agents)-1)]

def clean(x): return re.sub("\s","",x)

class KittyScratcher:
    def __init__(self):
        pass

    def getSite(self,id):
        url = "https://cryptokittydex.com/kitties/{id}".format(id=134474)
        headers = {
            'User-Agent': userAgent(),
            'From': 'youremail@domain.com'  # This is another valid field
        }

        print url
        r = requests.get(url,headers=headers)

        return r.text

    def getInfo(self,id):
        t = open("test.txt",'r').read()
        soup = BeautifulSoup(t,"lxml")

        geneList = soup.find('ul',class_ = "list-unstyled list-inline list-genes")
        geneList = [clean(each.text) for each in geneList.findAll('li')]
        print len(geneList)



if __name__ == "__main__":
    ks = KittyScratcher()
    print ks.getInfo(1)