from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import requests
import os
import json

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'conaz.db')
db = SQLAlchemy(app)
db.create_all()

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    min_temp = db.Column(db.Integer, nullable=False)
    max_temp = db.Column(db.Integer, nullable=False)
    rain_prob = db.Column(db.Integer, nullable=False)
    rain_prec = db.Column(db.Integer, nullable=False)

    def __repr__(self): 
        return f'{self.date}'

@app.route('/weather/', methods=['GET'])
def weather():
    token = 'f36dfa8428907f8bcd486398fc1e2d56'
    city = request.args.get('city')
    date_begin = request.args.get('date_begin')
    date_finish = request.args.get('date_finish')
    date_begin = format_date(date_begin)
    date_finish = format_date(date_finish)
    now = datetime.now().date()
    delta_begin = now - date_begin
    delta_finish = now - date_finish
    if (abs(delta_begin.days) <= 7 and date_begin >= now 
    and abs(delta_finish.days) <=7 and date_finish >= now
    and date_begin <= date_finish):
        weather_data = []
        begin_data = Weather.query.filter_by(
            city=city, date=date_begin.strftime('%Y-%m-%d')
            ).first()
        finish_data = Weather.query.filter_by(
            city=city, date=date_finish.strftime('%Y-%m-%d')
        ).first()
        response = requests.get(
            f'http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{city}/days/15?token={token}'
            )
        data = response.json()
        city_name = data['name']
        data = data['data']
        min_temp = ''
        max_temp = ''
        rain_prob = ''
        rain_amount = ''
        for forecast in data:
            current_date = format_date(forecast['date'].replace('-', ''))
            if current_date >= date_begin and current_date <= date_finish:
                if current_date == date_begin:
                    if begin_data is None:
                        min_temp = forecast['temperature']['min']
                        min_temp_date = current_date
                        max_temp = forecast['temperature']['max']
                        max_temp_date = current_date
                        rain_prob = forecast['rain']['probability']
                        rain_amount = forecast['rain']['precipitation']
                        rain_date = current_date
                        insert_data = Weather(
                            city=city, city_name=city_name, date=date_begin,
                            min_temp=min_temp, max_temp=max_temp,
                            rain_prob=rain_prob, rain_prec=rain_amount
                            )
                        db.session.add(insert_data)
                        db.session.commit()
                    else:
                        min_temp = begin_data.min_temp
                        max_temp = begin_data.max_temp
                        rain_prob = begin_data.rain_prob
                        rain_amount = begin_data.rain_prec
                        min_temp_date = begin_data.date
                        max_temp_date = begin_data.date
                        rain_date = begin_data.date
                else:
                    current_data = Weather.query.filter_by(
                        city=city, date=current_date.strftime('%Y-%m-%d')
                    ).first()
                    if current_data is None:
                        current_min_temp = forecast['temperature']['min']
                        current_max_temp = forecast['temperature']['max']
                        current_rain_prob = forecast['rain']['probability']
                        current_rain_amount = forecast['rain']['precipitation']
                        insert_data = Weather(
                            city=city, city_name=city_name, date=current_date,
                            min_temp=current_min_temp,
                            max_temp=current_max_temp,
                            rain_prob=current_rain_prob,
                            rain_prec=current_rain_amount
                        )
                        db.session.add(insert_data)
                        db.session.commit()
                        if int(min_temp) > int(current_min_temp):
                            min_temp = current_min_temp
                            min_temp_date = current_date
                        if int(max_temp) < int(current_max_temp):
                            max_temp = current_max_temp
                            max_temp_date = current_date
                        if int(rain_prob) < int(current_rain_prob):
                            rain_prob = current_rain_prob
                            rain_amount = current_rain_amount
                            rain_date = current_date
                    else:
                        current_min_temp = current_data.min_temp
                        if int(min_temp) > int(current_min_temp):
                            min_temp = current_min_temp
                            min_temp_date = current_data.date
                        current_max_temp = current_data.max_temp
                        if int(max_temp) < int(current_max_temp):
                            max_temp = current_max_temp
                            max_temp_date = current_data.date
                        current_rain_prob = current_data.rain_prob
                        if int(rain_prob) < int(current_rain_prob):
                            rain_prob = current_rain_prob
                            rain_amount = current_data.rain_prec
                            rain_date = current_data.date
        json_dict = {
            'min_temp_date': min_temp_date.strftime('%Y-%m-%d'),
            'min_temp': min_temp,
            'max_temp_date': max_temp_date.strftime('%Y-%m-%d'),
            'max_temp': max_temp,
            'most_probable_rain_date': rain_date.strftime('%Y-%m-%d'),
            'rain_amount': rain_amount
        }
        return json.dumps(json_dict)
    else:
        return 'Error'

def format_date(date_str):
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:])
    return_date = date(year, month, day)
    return return_date
