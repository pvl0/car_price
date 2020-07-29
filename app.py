from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DecimalField, SubmitField
from wtforms.validators import InputRequired, NumberRange
import pandas as pd
import numpy as np
import xgboost as xgb
import pickle

# load xgboost regression model
reg_model = xgb.Booster({'nthread': 8})
reg_model.load_model('model/car_price_xgb_mean.json')

# load df with cars' parameters
cars = pd.read_csv('model/cars')

# initialise the Flask app and set parameters from config file
app = Flask(__name__,)
app.config.from_pyfile('config.py')

# create input form
class Form(FlaskForm):
    manufacturer = SelectField('manufacturer', [InputRequired()], render_kw={"class": 'manufacturer',})
    model = SelectField('model', [InputRequired()], render_kw={"class": 'model'})
    year = SelectField('year', [InputRequired()], render_kw={"class": 'year'})
    fuel_type = SelectField('fuel_type', [InputRequired()], render_kw={"class": 'fuel_type'},)
    engine_capacity = SelectField('engine_capacity', [InputRequired()], render_kw={"class": 'capacity'})
    mileage = SelectField('mileage', [InputRequired()], render_kw={"class": 'mileage',})
    automatic = SelectField('automatic', [InputRequired()], choices = [("",""), (1, 'Automatyczna'), (0, 'Manualna')], render_kw={"class": 'automatic'})
    wheel = SelectField('wheel', [InputRequired()], choices=[("",""), (0,'Po lewej'), (1, 'Po prawej (Anglik)')], render_kw={"class": 'wheel'})
    damaged = SelectField('damaged', [InputRequired()], choices=[("",""), ('perfect', 'Bezwypadkowy'), ('slightly', 'Lekko uszkodzony'), ('damaged', 'Mocno uszkodzony')], render_kw={"class": 'damaged'})
    submit = SubmitField('Submit', render_kw={"class": 'submit'})

@app.route('/', methods=['GET', 'POST'])
def main():
    form = Form()
    form.manufacturer.choices = [("","")] + list(zip(cars.manufacturer.drop_duplicates().sort_values(), cars.manufacturer.drop_duplicates().sort_values()))
    form.year.choices = [("","")] + list(zip( cars.year.drop_duplicates().sort_values(ascending = False), cars.year.drop_duplicates().sort_values(ascending = False) ))
    form.fuel_type.choices = [("","")] + list(zip( cars.fuel_type.value_counts().index, cars.fuel_type.value_counts().index ))
    
    eng_cap_ind = cars.engine_capacity.drop_duplicates().sort_values().values
    eng_cap_vals = [str(e) + ' cm3' for e in eng_cap_ind]
    form.engine_capacity.choices = [("","")] + list(zip(eng_cap_ind, eng_cap_vals))

    # loading mileage options from file to speed up loading (options come from range(1,10**6))
    with open("model/mileage_options.pkl", "rb") as file:
        form.mileage.choices = [("","")] + pickle.load(file)

    if request.method=="POST":
        # Extract the input
        manufacturer = form.manufacturer.data
        model = cars.iloc[int(form.model.data)].model
        year = form.year.data
        mileage = int(float(form.mileage.data))
        engine_capacity = int(form.engine_capacity.data)
        fuel_type = form.fuel_type.data
        automatic = form.automatic.data
        damaged_form = form.damaged.data
        damaged = {'perfect': 0, 'slightly': 0, 'damaged': 1}[damaged_form]
        slightly_damaged = {'perfect': 0, 'slightly': 1, 'damaged': 0}[damaged_form]        
        right_wheel = form.wheel.data
        # populating options for car model field
        form.model.choices = [(model['id'], model['name']) for model in retrieve_models(manufacturer)]

        # making DataFrame which will be fed to the regression models
        df = pd.DataFrame([[manufacturer, model, year, mileage, engine_capacity, fuel_type, automatic, damaged,  
                                        right_wheel, slightly_damaged,]],
                                       columns=['manufacturer', 'model', 'year', 'mileage', 'engine_capacity', 'fuel_type',
                                                'automatic', 'damaged', 'right_wheel', 'slightly_damaged',],)
    
        df = df.assign(combined = df.manufacturer + ' ' + df.model + ' ' + df.year.astype(str) + ' ' + \
                       round(df.engine_capacity/1000, 1).astype(str) + ' ' + df.fuel_type + ' ' + df.automatic.astype(str) + \
                       df.damaged.astype(str) + df.right_wheel.astype(str) + df.slightly_damaged.astype(str)) 
        
        # Transform dataframe into required form for xgb
        df_xgb = df.copy()
        for col in df.columns:
            if col not in ['mileage', 'combined']:
                df_xgb[f'{col}_mean'] = cars.query(f"{col} == '{df[f'{col}'].iloc[0]}'")[f'{col}_mean'].iloc[0]
                df_xgb = df_xgb.drop([f'{col}'], axis = 1)
        df_xgb = df_xgb.drop(['combined'], axis = 1)
        df_xgb = df_xgb.astype('int32')        
        columns_xgb = ['manufacturer_mean', 'model_mean', 'year_mean', 'mileage', 'engine_capacity_mean', 'fuel_type_mean',
                        'automatic_mean', 'damaged_mean', 'right_wheel_mean', 'slightly_damaged_mean']
        df_xgb = df_xgb.reindex(columns = columns_xgb)
        df_xgb = xgb.DMatrix(df_xgb)
        
        # Get the xgb model's prediction
        prediction = np.round(reg_model.predict(df_xgb), -2)
        prediction = f'{prediction[0].astype(int):,} PLN'.replace(',', ' ')
        
        # Simple mean prediction
        try:
            df_mean = cars.query(f"combined == '{df.combined.iloc[0]}' and mileage <= {mileage + 25000} \
                                    and mileage >= {mileage - 25000}")
            mean_price = str(f'{df_mean.price.mean():,}').replace(',',' ')
            price_range = str(f'{df_mean.price.min():,} PLN - {df_mean.price.max():,} PLN').replace(',',' ')
            median_price = df_mean.price.median()            
            car_count = df_mean['combined_count'].iloc[0]         
            
            result=[prediction, mean_price, price_range, median_price, car_count]
            return render_template('main.html', form = form, result=result)

        except:
            result = prediction
            return render_template('main_no_result.html', form = form, result=result)

    return render_template('main.html', form = form)

# create json with car models for given manufacturer taken from "cars" file
@app.route('/models/<manufacturer>')
def fetch_models(manufacturer):
    car_array = retrieve_models(manufacturer)
    return jsonify({'models': car_array})


def retrieve_models(manufacturer):
    models = cars.loc[cars.manufacturer == manufacturer].model.drop_duplicates().sort_values()
    models = pd.Series(models.values, models.index,).to_dict() # same as dict(zip(key, value)) but faster
    car_array = []
    for k,v in models.items():
        car_obj = {}
        car_obj['id'] = k
        car_obj['name'] = v
        car_array.append(car_obj)
    return car_array


if __name__ == '__main__':        
    app.run(debug=True)