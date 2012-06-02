from bottle import route, run, post, request
import alert_db as db


def select_by_email(r_email, database='alerts'):
    ret = {}
    db.init(database)
    alerts = db.Alert.select().where(email=r_email)
    for alert in alerts:
        ret.update({
                str(alert.term):
                    {'email': str(alert.email),
                    'wait': str(alert.wait),
                    'id': str(alert.id),}
            })
    return ret


@route('/list/:email')
def list(email='stephen.laporte@gmail.com'):
    ret = '<ul>'
    terms = select_by_email(email)
    for a in terms:
        ret += '<li>' + terms[a]['email'] + ' : ' + a + ' -- <form <form method="post" action="http://localhost:8080/remove"><input type="hidden" name="remove_id" value="' +  terms[a]['id'] + '"><button type="Submit">Delete</botton></form></li>'
    ret += '</ul>'
    return ret

@post('/add')
def add_term():
    p_term    = request.forms.term
    p_email   = request.forms.email
    p_wait    = request.forms.wait #todo: not implemented

    if p_term and p_email and p_wait:
        db.init()
        new_alert = db.Alert(email=p_email, term=p_term, wait=p_wait)
        new_alert.save()
        return 'Worked! Added ' + p_term + ' for you.'
    return 'Missed something'


@post('/remove')
def remove_term():
    p_id    = request.forms.remove_id

    if p_id:
        db.init()
        db.pw.DeleteQuery(db.Alert).where(id=p_id).execute()
        return 'Worked! Removed ' + p_id + ' for you.'
    return 'Missed something'

@route('/')
def index():
    return '''
<html>
<form method='post' action='http://localhost:8080/add'>
name: <input name='term'>
email: <input name='email'>
wait: <input name='wait'>
<button type='submit' value='Submit' name='submit'>Submit</botton>
</form>
</html>
'''
if __name__ == '__main__':
    run(host='localhost', port=8080)