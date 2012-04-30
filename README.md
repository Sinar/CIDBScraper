CIDBScraper
===========

This is our scraper for CIDB database, this is precisely what we run on our server. 

I suggest that you get the data from the data Dump to be release soon, so as we don't do duplicated work

And this is a bit hackish, so no configuration file, etc. Maybe should do it better

Files
* scrape.py : to download the html, save to output/
* extractor.py : generate an python object with data from html 
* extract_engine.py : library to process the html
* insert_to_gdoc.py : insert into google docs using gdata library

Requirement 
* Requests
* BeautifulSoup

DESCRIPTION OF CODE COMING SOON

