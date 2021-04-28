from couchdb import Server


s = Server('http://comp90024_db:123456@localhost:5984/')

dbname = "tweets"
db = None
if dbname in s:
    db = s[dbname]
else:
    db = s.create(dbname)
record1 = {"text":"adsfasdf","place":"adsf","_id":str(hash("adsfasdf"))}
record2 = {"text":"ads123","place":"aadsff","_id":str(hash("abs123"))}
if db.get(record1["_id"]) is None:
    db.save(record1)
if db.get(record2["_id"]) is None:
    db.save(record2)

for row in db.view('_all_docs'):
    print(row["id"])

#for _id in db:
#    db.delete(db[_id])
