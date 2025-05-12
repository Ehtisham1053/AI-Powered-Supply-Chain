import joblib

model = joblib.load("ml_models/models_30/1_1_target_30_day_sales.pkl")
print(type(model))
print(hasattr(model, 'predict'))
