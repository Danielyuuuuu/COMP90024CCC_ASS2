from couchdb import Server

class tweetsDB():
    dbname = "tweets"
    db = None
    count = None
    def __init__(self,url='http://pyf:123456@172.26.128.229:5984/'):
        s = Server(url)
        if self.dbname in s:
            self.db = s[self.dbname]
        else:
            self.db = s.create(self.dbname)
        
    def add_record(self,json_record):
        hash_string = str(hash(json_record['id']))
        json_record['_id'] = hash_string
        record = json_record
        if(self.db.get(record["_id"]) is None):
            self.db.save(record)
            if(self.count is None):
                self.count = 0
            else:
                self.count += 1
    
    def view_db(self,n=10):
        i=0
        for row in self.db.view("_all_docs"):
            print(self.db[row["id"]])
            i+=1
            if(i>n and n!=-1):
                break
    
    def get_data(self,from_index=0,to_index=10,get_all=False):
        result = []
        i=0
        for row in self.db.view("_all_docs"):
            if(i>=from_index or get_all):
                result.append(self.db[row["id"]])
            i+=1
            if(i>=to_index and not get_all):
                break
        return result

    def del_db(self):
        for row in self.db:
            self.db.delete(self.db[row])
            
    def get_num_record(self):
        if(self.count is None):
            return len(self.db.view("_all_docs"))
        else:
            return self.count

