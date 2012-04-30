import gdata.spreadsheet.service
import gdata.service
import gdata.spreadsheet
import gdata.spreadsheet.text_db
import settings
import extractor
import os
import signal
import pickle

class CIDBToGDocsDB(object):
    def __init__(self,username,password,db_name):
        self.client = gdata.spreadsheet.text_db.DatabaseClient(
                username=username,password=password)
        database = self.client.GetDatabases(name=db_name)
        if database:
            self.database = database[0]
        else:
            self.database = self.client.CreateDatabase(db_name)

    def insert_row(self,cidb_obj):
        datas = cidb_obj.get_data()
        tables = cidb_obj.get_worksheet()
        keys = cidb_obj.get_keys()
        for index in range(len(datas)):
            table_name = tables[index]
            table = self.database.GetTables(name=table_name)
            if not table:
                key = keys[index]
                table = self.database.CreateTable(table_name,key)
            else:
                table = table[0]
            if type(datas[index]) == list: 
                for item in datas[index]:
                    record = table.AddRecord(item)
                    record.Push()
            else:
                record = table.AddRecord(datas[index])
                record.Push() 


def main(filename,db_name):
    db = CIDBToGDocsDB(settings.USERNAME,settings.PASSWORD,db_name)
    cidb_entry = extractor.CIDBEntry(filename)
    cidb_entry.process()
    db.insert_row(cidb_entry)

if __name__ == "__main__":
    db_name = "CIDB DUMP %s V2"
    batch_no = 1
    batch_amt = 10000
    current_amt = 0
    current_read = 0

    if os.path.exists("saved_data"):
        saved_data = open("saved_data",'rb')
        state = pickle.load(saved_data)
        saved_data.close()
        current_read = state['current_read']
        batch_no = state['batch_no']
        current_amt = state['current_amt']
    else:
        state = {}
        state['current_read'] = current_read
        state['bad_record'] = []
        state['batch_no'] = batch_no
        state['current_amt'] = current_amt

    output_content = os.listdir('output/')

    for input_file in output_content[current_read:]:
        current_read = output_content.index(input_file)
        state['current_read'] = current_read

        try:
            if batch_amt < current_amt:
                batch_no = batch_no + 1
                state['batch_no'] = batch_no
                current_amt = 0
                state['current_amt'] = current_amt
                
            current_db = db_name % str(batch_no)
            current_file = "output/%s" % input_file
            cidb_entry = extractor.CIDBEntry(current_file)
            cidb_entry.process()
            print current_file
            db = CIDBToGDocsDB(settings.USERNAME,settings.PASSWORD,current_db)
            if cidb_entry.is_good_record():
                db.insert_row(cidb_entry)
                current_amt = current_amt + 1
                state['current_amt'] = current_amt
            else:
                state['bad_record'].append(input_file)
            saved_data = open("saved_data","wb")
            pickle.dump(state,saved_data)
            saved_data.close()

        except Exception as e:
            print e
            saved_data = open("saved_data","wb")
            pickle.dump(state,saved_data)
            saved_data.close()
            break
