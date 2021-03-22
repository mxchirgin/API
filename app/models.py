from datetime import datetime
from app import db, login
import json
SOLD=CLOSED=0
STOCK=OPEN=1

class Car(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    brand=db.Column(db.String(64))
    model=db.Column(db.String(64))
    year_built=db.Column(db.Integer, default=2021)
    mileage=db.Column(db.Integer, default=0)
    price=db.Column(db.Integer)
    onsale = db.Column(db.Boolean, default = True)
    color=db.Column(db.String(64))
    vendor_id= db.Column(db.Integer, db.ForeignKey('dealer.id'))
    sales=db.relationship('Sale', backref='transactions history', lazy='dynamic')
    def __repr__(self):
        
        return '<Car {}>'.format(self.model)
    def dictorize(self):
        return {'brand':self.brand, 'id':self.id, 'model':self.model, 'year_built':self.year_built,
                           'mileage':self.mileage,'price':self.price, 'status':self.status, 'dealer':self.vendor_id}

class Dealer(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    name=db.Column(db.String(64))
    district=db.Column(db.String(64))
    operating= db.Column(db.Boolean, default = True)
    cars=db.relationship('Car', backref='cars bought', lazy='dynamic')
    sales=db.relationship('Sale', backref='cars sold', lazy='dynamic')
    openingtime=db.Column(db.Time)
    closingtime=db.Column(db.Time)
    def __repr__(self):
        return '<Dealer {}>'.format(self.name)
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class Sale(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    dealer=db.Column(db.Integer, db.ForeignKey('dealer.id'))
    car=db.Column(db.Integer, db.ForeignKey('car.id'))
    date=db.Column(db.Date(),default=datetime.today().strftime('%Y-%m-%d'))
    price=db.Column(db.Integer)
    onsale = db.Column(db.Boolean, default = True)
    def __repr__(self):
        return '<Sale {}>'.format(self.name)
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
