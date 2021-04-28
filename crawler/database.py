from couchdb import Server

class tweetsDB():
    dbname = "tweets"
    db = None
    def __init__(self,url='http://comp90024_db:123456@localhost:5984/'):
        s = Server(url)
        if self.dbname in s:
            self.db = s[self.dbname]
        else:
            self.db = s.create(self.dbname)
        
    def add_record(self,text, place):
        hash_string = str(hash(text+place))
        record = {"text":text,"place":place,"_id":hash_string}
        if(self.db.get(record["_id"]) is None):
            self.db.save(record)
    
    def view_db(self,n=10):
        i=0
        for row in self.db.view("_all_docs"):
            print(self.db[row["id"]])
            i+=1
            if(i>n):
                break

    def del_db(self):
        for row in self.db:
            self.db.delete(self.db[row])

