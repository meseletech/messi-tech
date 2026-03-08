import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

data = pd.DataFrame({
    "acceptance_rate": [0.9, 0.8, 0.5, 0.3],
    "cancellations": [1, 2, 10, 15],
    "reviews": [4.5, 4.0, 3.0, 2.0],
    "risk_score": [20, 30, 70, 90]
})

X = data[["acceptance_rate", "cancellations", "reviews"]]
y = data["risk_score"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "models/merchant_risk_model.pkl")

print("Merchant risk model trained")
