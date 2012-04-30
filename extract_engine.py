import re
import json
import types

# Extract Table for CIDB Database. Using the parser pattern
class TallTableExtractor(object):
    def __init__(self,table):
        self.table = table
        self.result = []
        self.keys = []

    def extract_value(self):
        rows = self.table.findAll('tr')
        last_key = ''
        for row in rows:
            if row.parent.parent.name == 'td':
                continue
            data = row.findAll('td')
            if len(data) == 1:
                obj = TableObject(data[0].text)
                self.result.append(obj)
                working_obj = self.result[-1]
                self.keys = []
                
            else:
                if not self.result:
                    obj = TableObject('')
                    self.result.append(obj)
                    working_obj = self.result[-1]
                key = normalize_value(data[0].text)
                
                if key == '':
                    temp = getattr(working_obj,last_key)
                    temp = temp + ' ' +data[1].text
                else:
                    last_key = key
                    temp = data[1].text
                if last_key not in self.keys:
                    self.keys.append(last_key)

                if data[1].find('table'):
                    inner_rows = data[1].find('table').findAll('tr')
                    temp = ''
                    t_list = []
                    for inner_row in inner_rows:
                        inner_data = inner_row.findAll('td')
                        t_list.append(' '.join(
                                [i_data.text for i_data in inner_data]))
                    temp = ','.join(t_list)
                setattr(working_obj,last_key,temp)
                working_obj.keys = self.keys
            assert self.result, "result list is empty"
            

class WideTableExtractor(object):
    def __init__(self,table):
        self.table = table
        self.result = []
        self.keys = []

    def extract_value(self):
        keys = []
        rows = self.table.findAll('tr')
        title = ''
        if len(rows) <= 2:
            
            return 
        for row in rows:
            data = row.findAll('td')
            if len(data) == 1:
                title = data[0].text
                keys = []
            else:
                if not keys:
                    for d in data:
                        keys.append(d.text)
                    self.keys = keys
                else:
                    obj = TableObject(title)
                    obj.keys = self.keys
                    self.result.append(obj)
                    working_obj = self.result[-1]
                    temp = dict(zip(keys,[i.text for i in data]))
                    for k in temp:
                        k_ = normalize_value(k)
                        setattr(working_obj,k_,temp[k])

        assert self.result, "result list is empty"


class StringExtractor(object):
    def __init__(self,table):
        self.table = table
        self.result = []

    def extract_value(self):
        rows = self.table.findAll('tr')
        title = rows[0].text
        self.obj = TableObject(title)
        if len(rows) > 1:
            keys = []
            for row in rows[1:]:
                data = row.text.split(':')
                key = normalize_value(data[0])
                keys.append(key)
                setattr(self.obj,key,data[1])
                self.obj.keys = keys

            self.result.append(self.obj)


class TableObject(object):
    def __init__(self,title):
        self.title = title

    def to_dict(self):
        keys=dir(self)
        temp = {}
        for key in keys:
            if not re.match('^__',key):
                if not type(getattr(self,key))==types.MethodType:
                    if key != 'title':
                        if key != 'keys':
                            temp[key] = getattr(self,key)
                    
        return temp
    
    def to_json(self):
        temp = self.to_dict()
        return json.dumps(temp)


def normalize_value(value):
    value = value.replace(' ','')
    value = value.replace('(','')
    value = value.replace(')','')
    value = value.replace(':','')
    value = value.replace('*','')
    value = value.replace('-','')
    value = value.replace('\r\n','')
    value = value.replace('/','')
    value = value.replace('.','')
    value = value.replace('&nbsp;','')
    pattern = re.compile('_+')
    value = pattern.sub('',value)
    pattern = re.compile('^((i+|v)|(v|i+))')
    value =  pattern.sub('',value)
    return value
