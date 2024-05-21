from flask import Flask, render_template, request,render_template_string
import geopy.distance
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
import folium
app = Flask(__name__)

model = joblib.load('model.pkl')

label_mappings = {
    'NightTime': {'No': 0, 'Yes': 1},
}
@app.errorhandler(ValueError)
def handle_value_error(e):
    return render_template('404.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    def check(m):
                latitude,longitude=m.split(',')
                if 'N' in latitude:
                    latitude=float(latitude[:-3])
                elif 'S' in latitude:
                    latitude=-float(latitude[:-3])
                if 'E' in longitude:
                    longitude=float(longitude[:-3])
                elif 'W' in longitude:
                    longitude=-float(longitude[:-3])
                return [latitude,longitude]
    if request.method == 'POST':
        try:
            location1_array = request.form.get('location1')
            location2_array = request.form.get('location2')
            NightTime = request.form.get('NightTime')
            passenger_count = int(request.form.get('passenger_count'))
            start_point=check(location1_array)
            dest_point=check(location2_array)

            label_encoders = {}
            categorical_features = list(label_mappings.keys())

            for feature in categorical_features:
                le = LabelEncoder()
                le.classes_ = np.array(list(label_mappings[feature].keys()))
                label_encoders[feature] = le

            encoded_features = []
            for feature_name in categorical_features:
                feature_value = locals()[feature_name] 
                le = label_encoders[feature_name]
                encoded_feature = le.transform([feature_value])
                encoded_features.append(encoded_feature[0])


            encoded_features.insert(0,start_point[0])
            encoded_features.insert(1,start_point[1])
            encoded_features.insert(2,dest_point[0])
            encoded_features.insert(3,dest_point[1])
            encoded_features.insert(4,passenger_count)
            

            val = [np.array(encoded_features)]

            prediction = model.predict(val)[0]
            result = prediction
            distance=geopy.distance.geodesic(location1_array, location2_array).km
            return render_template('input_form.html',result_message=result,distance=distance)
        except ValueError:
            error_message = "Invalid input. Please make sure all fields are filled correctly."
            return render_template('404.html')
    else:
        return render_template('input_form.html', result_message=None)
 

if __name__ == '__main__':
    app.run(debug=True)
