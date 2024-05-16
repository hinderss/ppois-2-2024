import json

from flask import render_template, redirect, url_for, request
from flask_socketio import emit

from src.police import Police
from src.model import PrepareDutyData
from webapp import app, socketio
from webapp.forms import WelcomeForm
from webapp import model


@app.route('/result')
def result():
    template = 'result.html'
    police: Police = model.police
    if police is None:
        return redirect(url_for('welcome'))
    elif model.duty is None:
        return redirect(url_for('prepare'))
    else:
        score = model.score
        return render_template(template, score=score)


@app.route('/')
@app.route('/index')
def index():
    template = 'index.html'
    police: Police = model.police
    if police is None:
        return redirect(url_for('welcome'))
    else:
        return render_template(template, name=police.chief_officer)


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    template = 'welcome.html'
    form: WelcomeForm = WelcomeForm()
    officers = model.officer_list
    if form.validate_on_submit():
        city = form.city.data
        name = form.name.data
        model.create_police(city, name)
        return redirect(url_for('index'))
    return render_template(template, form=form, officers=officers)


@app.route('/prepare', methods=['GET', 'POST'])
def prepare():
    template = 'prepare.html'
    police: Police = model.police

    if police is None:
        return redirect(url_for('index'))
    else:
        data: PrepareDutyData = model.pre_prepare_duty()

        if request.method == 'POST':
            officers = model.officer_list
            patrol = []
            detective = []
            public_security = []
            for i, form in request.form.items():
                print(f"{i}: {form}")
                if form == 'patrol_form':
                    for officer in officers:
                        if officer.name == i:
                            patrol.append(officer)
                if form == 'detective_form':
                    for officer in officers:
                        if officer.name == i:
                            detective.append(officer)
                if form == 'public_security_form':
                    for officer in officers:
                        if officer.name == i:
                            public_security.append(officer)
            print(patrol)
            print(detective)
            print(public_security)
            model.prepare_duty(patrol, detective, public_security)

        return render_template(template,
                               date=data.date,
                               cases=data.cases,
                               patrol_event=data.patrol_event,
                               patrol_officers=data.patrol_list,
                               detective_officers=data.detective_list
                               )


@app.route('/call')
def call():
    template = 'call.html'
    police: Police = model.police
    if police is None:
        return redirect(url_for('welcome'))
    elif model.duty is None:
        return redirect(url_for('prepare'))
    return render_template(template,
                           name=police.chief_officer,
                           date=model.duty.timenow.strftime("%d.%m.%Y %H:%M"),
                           score=model.score
                           )


@socketio.on('connect')
def handle_connect():
    police: Police = model.police
    if police is None:
        return redirect(url_for('welcome'))
    elif model.duty is None:
        return redirect(url_for('prepare'))
    event = model.request_call()
    if event is not None:
        print(type(event))

        if event.type == 'call':
            officers = model.duty.public_security_team
        else:
            officers = model.duty.detective

        officers_dicts = []
        for officer in officers:
            d: dict = officer.to_dict()
            print(type(d))
            if officer.unavailable_until > model.duty.timenow:
                d['status'] = 'unavailable'
            else:
                d['status'] = 'available'
            officers_dicts.append(d)

        message = {
            'duty': 'on',
            'timenow': model.duty.timenow.strftime("%d.%m.%Y %H:%M"),
            'event': event.to_dict(),
            'officers': officers_dicts
        }

        emit('message_from_server', json.dumps(message))
    else:
        print('redirect result')
        print(model.duty.timenow)

        message = {
            'duty': 'off'
        }
        emit('message_from_server', json.dumps(message))


@socketio.on('message_from_client')
def handle_message_from_client(message):
    message = json.loads(message)
    print('Received message from client:')
    print(message)
    print(type(message))
    print(type(message))
    officers = model.officer_list
    assigned = []
    for i in message:
        for officer in officers:
            if officer.name == i:
                assigned.append(officer)

    print(assigned)
    score_type = model.handle_event(assigned)
    scoring(score_type)
    handle_connect()


def scoring(score_type: str):
    police: Police = model.police
    if police is None:
        return redirect(url_for('welcome'))
    elif model.duty is None:
        return redirect(url_for('prepare'))
    message = {
        'score': {
            'value': model.score,
            'type': score_type
        }
    }
    emit('score', json.dumps(message))



