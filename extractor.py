import re
from BeautifulSoup import BeautifulSoup
from extract_engine import TallTableExtractor
from extract_engine import WideTableExtractor
from extract_engine import StringExtractor

class CIDBEntry(object):
    def __init__(self,page):
        self.page = open(page)
        self.reference = page.split('.')[0].split('/')[-1]
        self.soup = BeautifulSoup(self.page)
        self.target = self.soup.find('div',{'id':'todaysoftware'})
        self.result = []
        self.url = "http://202.190.73.10/directory/local_contractor_details.php?cont_id=%s"

    def process(self):
        tables = self.target.findAll('table')
        extend_table = ['A','B','F','G']
        append_table = ['C','D','E','H','I','J']
        for table in tables:
            check = table.find('tr')
            if not check:
                continue
            check = check.text
            if re.match('\S\.',check):
                if check[0] in extend_table:
                    self.result.extend(self.process_table(table))
                elif check[0] in append_table:
                    self.result.append(self.process_table(table))
            elif re.match('^Status',check):
                self.result.extend(self.process_table(table))
            

    def process_table(self,table):
        tall_table = ['A','B']
        wide_table = ['C','D','E','H','I','J']
        string_table = ['F','G']
        
        check = table.find('tr').text
        if check[0] in tall_table:
            extractor = TallTableExtractor(table)

        elif check[0] in wide_table:
            extractor = WideTableExtractor(table)

        elif check[0] in string_table:
            extractor = StringExtractor(table)

        elif re.match('^Status',check):
            extractor = TallTableExtractor(table)
        else:
            return []

        extractor.extract_value()
        return extractor.result
    
    def get_keys(self):
        keys = []
        for item in self.result:
            if type(item) == list:
                if not item:
                    continue
                obj = item[0]
            else:
                obj = item
            temp = obj.to_dict()
            if not temp:
                continue
            keys.append([k.lower() for k in obj.keys])
        for k in keys:
            k.append('reference')
            k.append('source')
        keys.pop(4)
        return keys
    
    def get_worksheet(self):
        sheet_list = []
        for item in self.result:
            if type(item) == list:
                if not item:
                    continue
                obj = item[0]
            else:
                obj = item
            if not obj.to_dict():
                continue
            temp = obj.title
            sheet_list.append(temp)
        sheet_list = [normalize_value(i) for i in sheet_list]
        sheet_list.pop(4)
        return sheet_list

    def is_good_record(self):
        company_info = self.result[0]
        status = False
        company_dict = company_info.to_dict()
        for key in company_dict:
            if company_dict[key]:
                if re.match('^\S+$',company_dict[key]):
                    status = True
        return status

    def get_data(self):
        datas = self.result
        result = []
        for data in datas:
            if type(data) == list:
                if not data:
                    continue
                temp = []
                for d in data:
                    tdata = d.to_dict()
                    if not tdata:
                        continue
                    t = {}
                    for td in tdata:
                        t[td.lower()] = tdata[td]
                    temp.append(t)
                    temp[-1]['reference'] = self.reference
                    temp[-1]['source'] = self.url % self.reference
            else:
                temp = {}
                tdata = data.to_dict()
                if not tdata:
                    continue
                for t in tdata:
                    temp[t.lower()] = tdata[t]
                temp['reference'] = self.reference
                temp['source'] = self.url % self.reference
            result.append(temp)
        result[0].update(result[4])
        result.pop(4)
        return result

def normalize_value(value):
    value = value.replace('\r\n','')
    value = value.replace('&nbsp;','')
    value = value.replace('/','')

    pattern = re.compile(':$')
    value = pattern.sub('',value)
    pattern = re.compile('^\s+')
    value = pattern.sub('',value)
    pattern = re.compile('\s+$')
    value = pattern.sub('',value)
    pattern = re.compile('\s\s+')
    value = pattern.sub(' ',value)
    pattern = re.compile('\.\s')
    value = pattern.sub('.',value)
    pattern = re.compile('\S\.')
    value = pattern.sub('',value)
    pattern = re.compile(':$')
    value = pattern.sub('',value)
    value = value.replace(' ','_')
    return value.lower()   


