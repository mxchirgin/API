from flask import request, jsonify, make_response
from app import app, db
from app.models import Dealer, Car, Sale
from sqlalchemy import func, orm
import datetime
import json
import sqlite3

import time
import os
basedir = os.path.abspath(os.path.dirname(__file__))


import atexit

def request_to_time(string):
    return datetime.time(hour=int(string.split(":")[0]),minute=int(string.split(":")[1]))

def list_to_json(lst):
    dct ={'id'+str(i.id):i.dictorize() for i in lst}
    return json.dumps(dct)
                         
@app.route('/cars')
def findallcars():
    cars=Car.query.filter_by(**request.args.to_dict()).all()
    if cars==[]:
        return make_response(jsonify({'error': 'Not Found'}), 404)
    else:
        return list_to_json(cars)
@app.route('/cars/onsale')
def findsellingcars():
    cars=Car.query.filter_by(**request.args.to_dict(),onsale=True).all()
    if cars==[]:
        return make_response(jsonify({'error': 'Not Found'}), 404)
    else:
        return list_to_json(cars)
@app.route('/cars/sold')
def findsoldcars():
    cars=Car.query.filter_by(**request.args.to_dict(),onsale=False).all()
    if cars==[]:
        return make_response(jsonify({'error': 'Not Found'}), 404)
    else:
        return list_to_json(cars)

@app.route('/cars/add',methods=['POST'])
def add_car():
    if (not request.json or not 'brand' in request.json
    or not 'model' in request.json or not 'dealer' in request.json
    or not 'price' in request.json or not 'color' in request.json
        ):
        return make_response(jsonify({'error': 'Incorrect Request'}), 400)
    else:
        new_car=Car(brand=request.json['brand'],model=request.json['model'],
                price=int(request.json['price']), vendor_id=int(request.json['dealer']), color=request.json['color'])
        if 'year_built' in request.json:
            new_car.year_built=int(request.json['year_built'])
        if 'mileage' in request.json:
            new_car.mileage=int(request.json['mileage'])
        db.session.add(new_car)
        db.session.commit()
        sale=Sale(car=new_car.id, dealer=new_car.vendor_id,price=new_car.price)
        db.session.add(sale)
        db.session.commit()
        return make_response(jsonify({'result': 'Created Successfully'}), 201)
    
@app.route('/dealers/add', methods=['POST'])
def add_dealer():
    if (not request.json or not 'name' in request.json
    or not 'district' in request.json or not 'openingtime' in request.json or not 'closingtime' in request.json):
        return make_response(jsonify({'error': 'Incorrect Request'}), 400)
    else:
        
        new_dealer=Dealer(name=request.json['name'],district=request.json['district'],
                          openingtime=request_to_time(request.json['openingtime'])
                        , closingtime=request_to_time(request.json['closingtime']))
        db.session.add(new_dealer)
        db.session.commit()
        return make_response(jsonify({'result': 'Created Successfully'}), 201)

@app.route('/dealers/close/<int:id>',methods=['PUT'])
def close_dealer(id):
    dealer=Dealer.query.filter_by(id=id).first()
    cars=Car.query.filter_by(vendor_id=id, onsale=True).all()
    if dealer:
        dealer.operating=False
        for car in cars:
            car.onsale=False
            сar.price=0
        db.session.commit()
        return make_response(jsonify({'result': 'Dealer state changed successfully'}), 200)
    else:
        return make_response(jsonify({'error': 'Dealer Not Found'}), 404)
    

@app.route('/dealers/delete/<int:id>', methods=['DELETE'])
def del_dealer(id):
    dealer=Dealer.query.filter_by(id=id).first()
    cars=Car.query.filter_by(vendor_id=id).all()
    if dealer:
        db.session.delete(dealer)
        for car in cars:
            car.onsale=False
        db.session.commit()
        return make_response(jsonify({'result': 'Dealer deleted successfully'}), 200)
    else:
        return make_response(jsonify({'error': 'Dealer Not Found'}), 404)

@app.route('/cars/delete/<int:id>',methods=['DELETE'])
def del_car(id):
    car=Car.query.filter_by(id=id).first()
    sales=Sale.query.filter_by(car=id).all()
    if car and sales:
        db.session.delete(car)
        for sale in sales:
            db.session.delete(sale)
        db.session.commit()
        return make_response(jsonify({'result': 'Car deleted successfully'}), 200)
    else:
        return make_response(jsonify({'error': 'Car Not Found'}), 404)


@app.route('/cars/move/<int:car_id>/<int:dealer_id>', methods=['PUT'])
def move_car(car_id, dealer_id):
    car=Car.query.filter_by(id=car_id).first()
    dealer=Dealer.query.filter_by(id=dealer_id).first()
    if car and dealer:
        car.vendor_id = dealer_id
        sale=Sale(car=car_id, dealer=dealer_id, price=car.price)
        db.session.add(sale)
        db.session.commit()
        return make_response(jsonify({'result': 'Car moved successfully'}), 200)
    elif not car:
        return make_response(jsonify({'error': 'Car Not Found'}), 404)
    else:
        return make_response(jsonify({'error': 'Dealer Not Found'}), 404)



@app.route('/cars/reprice/<int:id>/<int:new_price>', methods=['PUT'])
def reprice_car(id,new_price):
    car=Car.query.filter_by(id=id,onsale=True).first()
    if car:
        car.price=new_price
        sale=Sale(car=id,dealer=car.vendor_id,price=new_price)
        db.session.add(sale)
        db.session.commit()
        return make_response(jsonify({'result': 'Price changed successfully'}), 200)
    else:
         return make_response(jsonify({'error': 'Car Not Found or Not on Sale'}), 404)
        

@app.route('/cars/sell/<int:id>', methods=[ 'PUT'])
def sell_car(id):
    car=Car.query.filter_by(id=id,onsale=True).first()
    if car:
        car.onsale=False
        sale=Sale(car=id,dealer=car.vendor_id,price=car.price,onsale=False )
        db.session.add(sale)
        db.session.commit()
        return make_response(jsonify({'result': 'Car sold successfully'}), 200)
    else:
        return make_response(jsonify({'error': 'Car Not Found or Not on Sale'}), 404)
@app.route('/cars/buyback/<int:id>', methods=[ 'PUT'])
def buyback_car(id):
    car=Car.query.filter_by(id=id,onsale=False).first()
    if car:
        car.onsale=True
        sale=Sale(car=id,dealer=car.vendor_id,price=car.price,onsale=True )
        db.session.add(sale)
        db.session.commit()
        return make_response(jsonify({'result': 'Car is Back on Sale'}), 200)
    else:
        return make_response(jsonify({'error': 'Car Not Found or Already on sale'}), 404)

@app.route('/dealers/change_worktime/<int:id>', methods=['PUT'])
def change_time(id):
    if not request.json or( not 'openingtime' in request.json and not 'closingtime' in request.json):
        abort(400)
    else:
        dealer=Dealer.query.filter_by(id=id).first()
    if dealer and 'openingtime' in request.json and 'closingtime' in request.json:
        dealer.openingtime=request_to_time(request.json['openingtime'])
        dealer.closingtime=request_to_time(request.json['closingtime'])
        db.session.commit()
        return make_response(jsonify({'result': 'Buisness hours changed successfully'}), 200)
    if dealer and 'openingtime' in request.json:
        dealer.openingtime=request_to_time(request.json['openingtime'])
        db.session.commit()
        return make_response(jsonify({'result': 'opening time changed successfully'}), 200)
    elif dealer and 'closingtime' in request.json:
        dealer.closingtime=request_to_time(request.json['closingtime'])
        db.session.commit()
        return make_response(jsonify({'result': 'Closing time changed successfully'}), 200)
    else:
        return make_response(jsonify({'error': 'Dealer not found'}), 200)

@app.route('/dealers/change_district/<int:id>', methods=['PUT'])
def change_location(id):
    if not request.json or not 'district' in request.json :
        abort(400)
    else:
        dealer=Dealer.query.filter_by(id=id).first()
    if dealer:
        dealer.district=request.json['district']
        db.session.commit()
        return make_response(jsonify({'result': 'Location changed successfully'}), 201)

@app.route('/cars/in_district/<district>')
def findcars_loc(district):
    cars=db.session.query(Car).filter_by(**request.args.to_dict(),onsale=True).join(Dealer,Car.vendor_id==Dealer.id).filter_by(district=district).all()
    if cars==[]:
        return make_response(jsonify({'error': ' Cars Not Found'}), 404)
    else:
        return list_to_json(cars)

@app.route('/cars/now')
def findcars_now():
    cars=db.session.query(Car).filter_by(**request.args.to_dict(), onsale=True).join(Dealer,Car.vendor_id==Dealer.id).filter(func.TIME(Dealer.openingtime)<datetime.datetime.now().time(),func.TIME(Dealer.closingtime)>datetime.datetime.now().time()).filter_by(operating=True)
    cars=cars.all()
    if cars==[]:
        return make_response(jsonify({'error': 'Cars Not Found'}), 404)
    else:
        return list_to_json(cars)

@app.route('/cars/now/<district>')
def findcars_nowloc(district):
    cars=db.session.query(Car).filter_by(**request.args.to_dict(), onsale=True).join(Dealer,Car.vendor_id==Dealer.id).filter(func.TIME(Dealer.openingtime)<datetime.datetime.now().time(),func.TIME(Dealer.closingtime)>datetime.datetime.now().time()).filter_by(district=district).all()
    if cars==[]:
        return make_response(jsonify({'error': 'Cars Not Found'}), 404)
    else:
        return list_to_json(cars)
    

@app.route('/dealers/operating/opennow')
def opennow_dealers():
    dealers=Dealer.query.filter(func.TIME(Dealer.openingtime)<datetime.datetime.now().time(),func.TIME(Dealer.closingtime)>datetime.datetime.now().time()).filter_by(operating=True)
    if dealers:
        return list_to_json(dealers)
    else:
        return make_response(jsonify({'error': 'Dealers Not Found'}), 404)

@app.route('/dealers/operating')
def open_dealers():
    dealers=Dealer.query.filter_by(**request.args.to_dict(),operating=True)
    if dealers:
        return list_to_json(dealers)
    else:
        return make_response(jsonify({'error': 'Dealers Not Found'}), 404)
    
@app.route('/dealers')
def find_dealers():
    dealers=Dealer.query.filter_by(**request.args.to_dict())
    if dealers:
        return list_to_json(dealers)
    else:
        return make_response(jsonify({'error': 'Dealers Not Found'}), 404)

@app.route('/dealers/open/<int:id>')
def open_dealer(id):
    dealers=Dealer.query.filter_by(id=id,operating=False).first()
    cars=Car.query.filter_by(vendor_id=id,onsale=False, price=0).all()
    if dealers:
        dealers.operating=True
        for car in cars:
            sale=Sale.query.filter_by(car=car.id).last()
            car.onsale=True
            car.price=sale.price
        db.session.commit()
        return make_response(jsonify({'result': 'Dealer opened successfully'}), 201)
    else:
        return make_response(jsonify({'error': 'Dealers Not Found or Already Open'}), 404)
@app.route('/car_history/<int:car_id>')
def get_car_history(car_id):
    if request.args.get('onsale',None):
        records=Sale.query.filter_by(car=car_id, onsale=False).all()
    else:
        records=Sale.query.filter_by(car=car_id).all()
    if records:
        return list_to_json(records)
    else:
        return make_response(jsonify({'error': 'Car history Not Found'}), 404)
@app.route('/dealer_history/<int:dealer_id>')
def get_dealer_history(dealer_id):
    if request.args.get('onsale',None):
        records=Sale.query.filter_by(dealer=dealer_id, onsale=False).all()
    else:
        records=Sale.query.filter_by(dealer=dealer_id).all()
    if records:
        return list_to_json(records)
    else:
        return make_response(jsonify({'error': 'Dealer history Not Found'}), 404)

@app.route('/all_history')
def get_dealer_history():
    if request.args.get('onsale',None):
        records=Sale.query.filter_by(onsale=False).all()
    else:
        records=Sale.query.all()
    if records:
        return list_to_json(records)
    else:
        return make_response(jsonify({'error': 'No History Yet'}), 404)

