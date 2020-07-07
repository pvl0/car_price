from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, RadioField, SubmitField
from wtforms.validators import InputRequired
import os
import pickle
import pandas as pd
import numpy as np
SECRET_KEY = os.urandom(32)

# load df with cars' manufacturers and models
cars = pd.read_csv('cars')

# Initialise the Flask app and set the secret key; без ключа не запрацює хоч для цього мікро проекту це якийсь оверкіл
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

class Form(FlaskForm):
    manufacturer = SelectField('manufacturer', [InputRequired()], render_kw={"class": 'manufacturer',})
    model = SelectField('model', [InputRequired()], render_kw={"class": 'model'})
    year = SelectField('year', [InputRequired()], render_kw={"class": 'year'})
    submit = SubmitField('Submit', render_kw={"class": 'submit'})
    
@app.route('/', methods=['GET', 'POST'])
def main():
    form = Form()
    form.manufacturer.choices = [("","")] + list(zip(cars.manufacturer.drop_duplicates().sort_values(), cars.manufacturer.drop_duplicates().sort_values().str.capitalize()))
    form.year.choices = [("","")] + [(i,i) for i in range(2020,1930,-1)] #лишив поле з роком випуску для прикладу як повинно бути

    if request.method=="POST":
        # Extract the input
        manufacturer = form.manufacturer.data
        model = cars.iloc[int(form.model.data)].model
        year = form.year.data
        return render_template('main.html', form = form, result = 'PRYVIT DIMON')

    return render_template('main.html', form = form)

# create json with car models for given manufacturer taken from "cars" file
@app.route('/models/<manufacturer>')
def model(manufacturer):
    models = cars.loc[cars.manufacturer == manufacturer]
    models = pd.Series(models.iloc[:,1].values, models.iloc[:,1].index,).to_dict() # same as dict(zip(key, value)) but faster
    car_array = []
    for k,v in models.items():
        car_obj = {}
        car_obj['id'] = k
        car_obj['name'] = v
        car_array.append(car_obj)

    return jsonify({'models': car_array})

if __name__ == '__main__':        
    app.run(debug=True)
    