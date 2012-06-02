import peewee as pw
from datetime import datetime

alert_db = pw.SqliteDatabase(None) #deferred initialization

def init(db_name='alerts', **kwargs):
    alert_db.init(str(db_name) + '.db', **kwargs)
    alert_db.connect()
    Alert.create_table(fail_silently=True)

class dbModel(pw.Model):
    class Meta:
        database = alert_db


class Alert(dbModel):
    
    email   = pw.CharField()
    term    = pw.CharField()
    wait    = pw.CharField()

    def term_dict(self):
        return {
            str(self.term): [str(self.email), str(self.wait)],
        }

def test():
    init()
    test = Alert(email='stephen.laporte@gmail.com', term='slaporte', wait='False');
    test.save()

if __name__ == '__main__':
    test()