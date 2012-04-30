import extractor
import os
import json

if __name__ == "__main__":
    for f in os.listdir('output/'):
        print 'processing %s' % f
        id = f.split('.')[0]
        json_file = "json_output/"+id+".json"
        entry = extractor.CIDBEntry("output/%s"% f)
        entry.process()
        data = entry.get_data()
        jf = open(json_file,'wb')
        json.dump(data,jf)
        jf.close()
        print 'done %s' % f
