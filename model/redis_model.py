import redis  

class Database:  
    def __init__(self):  
        self.host = '10.9.23.219'  
        self.port = 6379  
        self.write_pool = {}  

    def add_write(self,key,value):  
        try:  
            r = redis.StrictRedis(host=self.host,port=self.port)  
            r.sadd(key, value)  
        except Exception, exception:  
            print exception
  
def add_data(adddata):  
    db = Database()  
    db.add_write('push2app1',adddata) 


