from bottle import route, run, post, request, view, redirect
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

@route('/edit_rate')
def get_rate():
    elog = open('edits', 'r')
    return elog.read()

@route('/l')
def reroute():
    redirect('/list/' + request.query.email)

@route('/list/:email')
@view('list')
def list(email='stephen.laporte@gmail.com'):
    terms = select_by_email(email)
    return dict(terms=terms, email=email, new_form=new)

@route('/list/')
def reroute():
    redirect('/')

@post('/add')
@view('add')
def add_term():
    p_term    = request.forms.term
    p_email   = request.forms.email
    p_wait    = request.forms.wait #todo: not implemented

    if p_term and p_email and p_wait:
        db.init()
        new_alert = db.Alert(email=p_email, term=p_term, wait=p_wait)
        new_alert.save()
        return dict(alert='Worked! Added an alert for "' + p_term + '"', type='success')
    return dict(alert='Missed something', type='error')


@post('/remove')
@view('remove')
def remove_term():
    p_id    = request.forms.remove_id
    if p_id:
        db.init()
        db.pw.DeleteQuery(db.Alert).where(id=p_id).execute()
        return dict(alert='Alert removed.', type='success')
    return dict(alert='Oops, something did not work.', type='error')

@route('/')
@view('index')
def index():
    return dict(new_form=new, manage_form=manage)

new = '''
<form class='well form-inline' method='post' action='http://localhost:8080/add'>
<fieldset>
<legend>Add an alert</legend>
<div class="input-prepend">
<span class="add-on"><i class="icon-tag"></i></span><input type='text' class='input-xlarge' id='term' name='term' placeholder='term'>
</div>
<div class="input-prepend">
<span class="add-on"><i class="icon-envelope"></i></span><input type='text' class='input-xlarge' id='email' name='email' placeholder='email'>
</div>
<input type='hidden' id='wait' name='wait' value='False'>
<button type='submit' value='Submit' name='submit' class='btn'>Submit</botton>
</fieldset>
</form>'''

manage = '''
<form class='well form-inline' method='get' action='http://localhost:8080/l'>
<fieldset>
<legend>Manage alerts</legend>
<div class="input-prepend">
<span class="add-on"><i class="icon-envelope"></i></span><input type='text' class='input-xlarge' id='email' name='email' placeholder='email'>
</div>
<button type='submit' class='btn blue'>Submit</botton>
</fieldset>
</form>
'''

if __name__ == '__main__':
    run(host='localhost', port=8080)