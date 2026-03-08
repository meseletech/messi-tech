import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Example training data (replace with real DB export later)
data = pd.DataFrame({
    "cancellations": [0, 1, 5, 10, 2, 8],
    "payment_failures": [0, 0, 2, 5, 1, 4],
    "booking_count": [10, 15, 3, 2, 8, 1],
    "fraud": [0, 0, 1, 1, 0, 1]
})

X = data[["cancellations", "payment_failures", "booking_count"]]
y = data["fraud"]

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "models/fraud_model.pkl")

print("Fraud model trained successfully")
