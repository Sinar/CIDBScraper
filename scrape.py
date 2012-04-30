import requests
import random
import sqlite3
import time
import datetime
import os

# Run through a privoxy proxy, again to hide request, through a few machine
PROXY = "127.0.0.1:8118"

PROXY_DICT = {'http':PROXY,'https':PROXY}

# This is ugly, but then so is the page, trying to find a fix
ID_LIST = range(1,158000)

ADDRESS = "http://202.190.73.10/directory/local_contractor_details.php?cont_id=%s"

USER_AGENT = "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"

def crawler():
    crawl_completed = False
    while not crawl_completed:

        page_id = random.sample(ID_LIST,1)[0]
        output_path = 'output/%s.html' % (str(page_id))
        
        while os.path.exists(output_path):
            # just so we can hide our request a bit more, most probably an overkill
            page_id = random.sample(ID_LIST,1)[0]
            output_path = 'output/%s.html' % (str(page_id))
            ID_LIST.pop(ID_LIST.index(page_id))
        
        header = {'User-Agent':USER_AGENT}
        try:
            data = requests.get(ADDRESS%str(page_id),headers=header,proxies=PROXY_DICT)
            data.raise_for_status()
        except requests.HTTPError:
            print ADDRESS%str(page_id)
            return
        
        f = open(output_path,"w")
        f.write(data.text)
        f.close()
        
#        next_crawl = random.sample(xrange(5,10),1)[0] 
#        now = datetime.datetime.now()
#        next_time = now + datetime.timedelta(0,next_crawl)
        print "write to %s" % output_path
 #       print "next print in %d second at %s" % (next_crawl,next_time)
        

#        time.sleep(next_crawl)
        if len(os.listdir('output')) >= len(ID_LIST):
            crawl_completed = True
            break

if __name__ == "__main__":
    crawler()
