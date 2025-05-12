from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load model, encoders, and scaler
model = pickle.load(open('best_model.pkl', 'rb'))
encoder = pickle.load(open('encoder.pkl', 'rb'))  # Dictionary of LabelEncoders
scaler = pickle.load(open('scaler.pkl', 'rb'))    # StandardScaler

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_data = {
            "gender": request.form['gender'],
            "SeniorCitizen": int(request.form['SeniorCitizen']),
            "Partner": request.form['Partner'],
            "Dependents": request.form['Dependents'],
            "tenure": float(request.form['tenure']),
            "PhoneService": request.form['PhoneService'],
            "MultipleLines": request.form['MultipleLines'],
            "InternetService": request.form['InternetService'],
            "OnlineSecurity": request.form['OnlineSecurity'],
            "OnlineBackup": request.form['OnlineBackup'],
            "DeviceProtection": request.form['DeviceProtection'],
            "TechSupport": request.form['TechSupport'],
            "StreamingTV": request.form['StreamingTV'],
            "StreamingMovies": request.form['StreamingMovies'],
            "Contract": request.form['Contract'],
            "PaperlessBilling": request.form['PaperlessBilling'],
            "PaymentMethod": request.form['PaymentMethod'],
            "MonthlyCharges": float(request.form['MonthlyCharges']),
            "TotalCharges": float(request.form['TotalCharges']),
        }

        encoded_data = []
        numeric_features = []

        for col, val in input_data.items():
            if col in encoder:
                try:
                    val_encoded = encoder[col].transform([val])[0]
                except Exception:
                    return render_template('index.html', prediction_text=f"Unknown value '{val}' for '{col}'")
                encoded_data.append(val_encoded)
            elif col in ['tenure', 'MonthlyCharges', 'TotalCharges']:
                numeric_features.append(val)  # Save to scale later
            else:
                encoded_data.append(val)

        # Scale numeric features
        scaled_nums = scaler.transform([numeric_features])[0]
        final_input = []

        i = 0  # Index for numeric features
        for col in input_data:
            if col in ['tenure', 'MonthlyCharges', 'TotalCharges']:
                final_input.append(scaled_nums[i])
                i += 1
            elif col in encoder:
                final_input.append(encoder[col].transform([input_data[col]])[0])
            else:
                final_input.append(input_data[col])

        prediction = model.predict([final_input])[0]
        result = "Customer is likely to <strong>Churn</strong> ❌" if prediction == 1 else "Customer is likely to <strong>Stay</strong> ✅"

        return render_template('index.html', prediction_text=result)

    except Exception as e:
        return render_template('index.html', prediction_text=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
