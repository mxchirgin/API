from flask import  flash, url_for, request,g, jsonify, make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import Dealer, Car, Sale
from sqlalchemy import func, orm
import datetime
import json
import sqlite3

import time
import os
basedir = os.path.abspath(os.path.dirname(__file__))
from apscheduler.schedulers.background import BackgroundScheduler

import atexit


"""@app.route('/cars/onsale/<int:dealer>')
def findcars(dealer):
    cars=Car.query.filter_by(**request.args.to_dict(),vendor_id=int(dealer), status=1).all()
    if cars==[]:
        return make_response(jsonify({'error': 'Not Found'}), 404)
    else:
            
        return jsonify({'cars':[car.dictorize() for car in cars]})
@app.route('/cars/sold/<int:dealer>')
def findsales(dealer):
    cars=Car.query.filter_by(**request.args.to_dict(),vendor_id=dealer, status=0).all()
    if cars==[]:
        return make_response(jsonify({'error': 'Not Found'}), 404)
    else:
        
       # for i in cars:
        #    car=cars[i].dictorize()
         #   cars[i
        return json.dumps({'cars':[car.dictorize() for car in cars]})"""
@app.route('/cars/onsale')
def findallcars():
   
    
    #cars=Car.query.SmartFilter(**request.args.to_dict()).all()
    cars=Car.query.filter_by(**request.args.to_dict()).all()
    if cars==[]:
        return make_response(jsonify({'error': 'Not Found'}), 404)
    else:
        
        return json.dumps({'cars':[car.dictorize() for car in cars]})

"""@app.route('/cars/sold')
def findsoldcars():
    cars=Car.query.filter_by(**request.args.to_dict(),status=0).all()
    if cars==[]:
        return make_response(jsonify({'error': 'Not Found'}), 404)
    else:
        l =lambda x:{'car'+str(car.id):car.dictorize() for car in x}
        return json.dumps({'cars':[car.dictorize() for car in cars]})"""
@app.route('/cars/add',methods=['POST'])
def create_car():
    if (not request.json or not 'brand' in request.json
    or not 'model' in request.json or not 'dealer' in request.json
    or not 'price' in request.json or not 'color' in request.json):
        abort(400)
    else:
        new_car=Car(brand=request.json['brand'],model=request.json['model'],
                price=request.json['price'], vendor_id=request.json['dealer'], color=request.json['color'])
        sale=Sale(
        if 'year_built' in request.json:
            new_car.year_built=request.json['year_built']
        if 'mileage' in requests.json:
            new_car.mileage=request.json['mileage']
        db.session.add(new_car)
        sale=Sale(car=new_car.id, dealer=new_car.vendor_id,price=new_car.price)
        db.session.add(sale)
        db.session.commit()
        return make_response(jsonify({'result': 'Created Successfully'}), 201)
    
@app.route('/dealers/add', methods=['POST'])
def add_dealer():
    if (not request.json or not 'name' in request.json
    or not 'district' in request.json or not 'openingtime' in request.json or not 'closingtime' in request.json):
        abort(400)
    else:
        new_dealer=Dealer(name=request.json['name'],district=request.json['district'],
                          openingtime=request.json['openingtime'], closingtime=request.json['closingtime'])
        db.session.add(new_dealer)
        db.session.commit()
        return make_response(jsonify({'result': 'Created Successfully'}), 201)

@app.route('/dealers/close/<int:id>', methods=['PUT'])
def close_dealer(id):
    dealer=Dealer.query.filter_by(id=id).first()
    if dealer:
        dealer.operating=False
        db.session.add(dealer)
        db.session.commit()
        return make_response(jsonify({'result': 'Dealer state changed successfully'}), 201)
    else:
        return make_response(jsonify({'error': 'Dealer Not Found'}), 404)
    

@app.route('/dealers/delete/<int:id>', methods=['DELETE'])
def del_dealer(id):
    dealer=Dealer.query.filter_by(id=id).first()
    if dealer:
        db.session.delete(dealer)
        db.session.commit()
        return make_response(jsonify({'result': 'Dealer deleted successfully'}), 201)
    else:
        return make_response(jsonify({'error': 'Dealer Not Found'}), 404)

@app.route('/cars/delete/<int:id>', methods=['DELETE'])
def del_car(id):
    car=Car.query.filter_by(id=id).first()
    if car:
        db.session.delete(car)
        db.session.commit()
        return make_response(jsonify({'result': 'Car deleted successfully'}), 201)
    else:
        return make_response(jsonify({'error': 'Car Not Found'}), 404)


@app.route('/cars/move/<car_id>/<dealer_id>', methods=['PUT'])
"""
@app.route('/cars/reprice/<id>/<price>', methods=['PUT'])

@app.route('/cars/sell/<id>', methods=['POST', 'PUT'])

@app.route('/cars/edit/<id>', methods=['POST', 'PUT'])
#add/dealer/car
#close/dealer/car

#update/dealer/car

#add/sale
#delete/sale

@app.before_request
def before_request():
    g.user = current_user


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first()
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    return render_template('index.html',
        user = user)

@app.route('/register_problem', methods=['GET', 'POST'])
@login_required
def register_problem():
    form = RegisterProblem()
    if form.validate_on_submit():
        alarm=Alarm.query.filter_by(status=1).filter_by(category=form.category.data).first()
        if alarm == None:
            problem = Post(user_id=g.user.id,name=form.name.data, region=form.region.data,
                       number= form.number.data,body=form.body.data,
                       category=form.category.data)
            db.session.add(problem)
            db.session.commit()
            return redirect(url_for('register_alarm'))
        else:
            problem = Post(user_id=g.user.id,name=form.name.data, region=form.region.data,
                           number= form.number.data,body=form.body.data,
                           category=form.category.data,alarm_id=alarm.id)
        
        
            db.session.add(problem)
            db.session.commit()
            flash('Обращение сформировано')
            return redirect(url_for('index'))
    return render_template('problem.html', title='Register Problem', form=form)

@app.route('/active_problems')
@login_required
def active_problems():
    qry=Post.query.filter_by(status=1).all()
    for i in qry:
        i.timestamp = i.timestamp.strftime("%Y-%m-%d %H:%M")

    table=MyProblems(qry)
    table.border = True
    return render_template('mystuff.html',table=table)

@app.route('/active_alarms')
@login_required
def active_alarms():
    qry=Alarm.query.filter_by(status=1).all()
    for i in qry:
        i.timestamp = i.timestamp.strftime("%Y-%m-%d %H:%M")

    table=MyAlarms(qry)
    table.border = True
    return render_template('mystuff.html',table=table)

@app.route('/register_alarm', methods=['GET', 'POST'])
@login_required
def register_alarm():
    form = RegisterAlarm()
    num=db.session.query(func.max(Alarm.id)).scalar()
    num+=1
    if form.validate_on_submit():
        
        alarm = Alarm(id=num,body=form.body.data, category=form.category.data)
        
       
        problem=Post.query.filter_by(alarm_id=None).first()
        new_problem = Post(id=problem.id,user_id=problem.user_id,
                               name=problem.name, region=problem.region,
                           number= problem.number,body=problem.body,
                           category=problem.category,
                               alarm_id=num, timestamp=problem.timestamp)
        db.session.delete(problem)
        
        db.session.add(new_problem)
        db.session.add(alarm)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('alarm.html',
                           title='зарегистрировать аварию номер %d' %num, 
                           form=form)

@app.route('/edit_problem/<id>', methods=['GET', 'POST'])
@login_required
def edit_problem(id):
    problem=Post.query.filter_by(id=id).first()
    if problem:
        form = RegisterProblem(formdata=request.form, obj=problem)
        if request.method == 'POST' and form.validate():
            new_problem = Post(id=problem.id,user_id=g.user.id,
                               name=form.name.data, region=form.region.data,
                           number= form.number.data,body=form.body.data,
                           category=form.category.data,
                               alarm_id=problem.alarm_id, timestamp=problem.timestamp)
            db.session.delete(problem)
            db.session.add(new_problem)
            db.session.commit()
            flash('Информация успешно обновлена')
            return redirect('/active_problems')
        return render_template('problem.html', form=form)
    else:
        return 'Error loading #{id}'.format(id=id)

@app.route('/finish_problem/<id>', methods=['GET', 'POST'])
@login_required
def finish_problem(id):
    problem=Post.query.filter_by(id=id).first()
    if problem:
        new_problem = Post(id=problem.id,user_id=problem.user_id,name=problem.name,
                           region=problem.region,
                           number= problem.number,body=problem.body,
                           category=problem.category,
                           alarm_id=problem.alarm_id, status=0)
        db.session.delete(problem)
        db.session.add(new_problem)
        db.session.commit()   
        flash('Обращение успешно закрыто')
        return redirect('/active_problems')
    else:
        return 'Error loading #{id}'.format(id=id)

@app.route('/finish_alarm/<id>', methods=['GET', 'POST'])
@login_required
def finish_alarm(id):
    alarm=Alarm.query.filter_by(id=id).first()
    problems=Post.query.filter_by(alarm_id=id).all()
    if alarm:
        alarm.status=0
        for p in problems:
            p.status=0
        db.session.commit()   
        flash('Авария успешно закрыта')
        return redirect('/active_alarms')
    else:
        return 'Error loading #{id}'.format(id=id)
    



scheduler = BackgroundScheduler()
scheduler.add_job(func=save_logs, trigger="interval", seconds=20)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
   
 """   
