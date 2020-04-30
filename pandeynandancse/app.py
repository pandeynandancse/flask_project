from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy
#from send_mail import send_mail

app = Flask(__name__)

ENV = 'prod'
#ENV ='dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://rwubbqztpeiglt:d09a302527e0ee1813c56c1bf0f64bc793729b369075867715f5cca58305dc0e@ec2-54-147-209-121.compute-1.amazonaws.com:5432/dcs9p1u9sgsckp'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments





class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)



@app.route('/')
def index():
    return render_template('overview.html')





@app.route('/login')
def login():
    return render_template('login.html')




@app.route('/overview')
def overview():
    return render_template('overview.html')



@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        dealer = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']
        # print(customer, dealer, rating, comments)
        if customer == '' or dealer == '':
            return render_template('index.html', message='Please enter required fields')
        if db.session.query(Feedback).filter(Feedback.customer == customer).count() == 0:
            data = Feedback(customer, dealer, rating, comments)
            db.session.add(data)
            db.session.commit()
           # send_mail(customer, dealer, rating, comments)
            return render_template('success.html')
        return render_template('index.html', message='You have already submitted feedback')






@app.route('/portfolio')
def portfolio():
    return render_template('index2.html')






@app.route('/weather', methods = ['GET','POST'])
def weather():
    if request.method == 'POST':
        new_city = request.form.get('city')
        
        if new_city:
            new_city_obj = City(name=new_city)

            db.session.add(new_city_obj)
            db.session.commit()

    cities = City.query.all()

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=352318b0096c90c8b3a94a031f4ee602'

    weather_data = []

    for city in cities:

        r = requests.get(url.format(city.name)).json()

        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)


if __name__ == '__main__':
    app.run()
