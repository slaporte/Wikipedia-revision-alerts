import peewee as pw

alert_db = pw.SqliteDatabase(None)

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

if __name__ == '__main__':
    test()