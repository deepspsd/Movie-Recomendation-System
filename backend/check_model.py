import pickle
import os

path = 'saved_models/collaborative_filtering_trained.pkl'
print(f'File size: {os.path.getsize(path) / 1024 / 1024:.1f} MB')

with open(path, 'rb') as f:
    data = pickle.load(f)
    
print(f'Users in model: {len(data.get("user_ids", []))}')
print(f'Movies in model: {len(data.get("movie_ids", []))}')
print(f'Model has user_factors: {data.get("user_factors") is not None}')
print(f'Model has item_factors: {data.get("item_factors") is not None}')
print(f'RMSE: {data.get("rmse")}')
print(f'MAE: {data.get("mae")}')
