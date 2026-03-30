"""
模型管理模块
负责模型的训练、保存、加载和预测
"""

import os
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.svm import SVR
from catboost import CatBoostRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

# 模型保存路径
MODEL_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "models"
MODEL_DIR.mkdir(exist_ok=True)

# 模型文件名
MODEL_FILES = {
    "hardness": MODEL_DIR / "hardness_model.pkl",
    "ec": MODEL_DIR / "ec_model.pkl",
    "q3": MODEL_DIR / "q3_model.pkl"
}

# 特征列定义
FEATURE_COLS = {
    "hardness": ["STem-ATem", "One-Hot-Processing", "CR_x_ATem", "HHI", "N_eff", "Tmavg", "Family", "Si/wt.%", "δ", "VECavg", "Mg/(Ni+Si)", "χvar", "Smix"],
    "ec": ["ATem_x_Atime", "STem-ATem", "CR_x_ATem", "Si/wt.%", "δ", "VECavg", "Mg/(Ni+Si)", "χvar", "Smix"],
    "q3": ["ATem_x_Atime", "STem-ATem", "CR_x_ATem", "Mg/(Ni+Si)", "χvar", "Smix"]
}

# 最优参数
BEST_PARAMS = {
    "hardness": {
        "model": "SVR",
        "params": {
            "C": 100,
            "gamma": "scale",
            "kernel": "rbf"
        }
    },
    "ec": {
        "model": "CAT",
        "params": {
            "depth": 6,
            "learning_rate": 0.1,
            "iterations": 1000
        }
    },
    "q3": {
        "model": "SVR",
        "params": {
            "C": 100,
            "gamma": "scale",
            "kernel": "rbf"
        }
    }
}

def build_preprocessor(X: pd.DataFrame):
    """
    构建数据预处理器
    """
    cat_cols = [c for c in X.columns if X[c].dtype == "object"]
    num_cols = [c for c in X.columns if c not in cat_cols]
    
    num_pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sc", StandardScaler()),
    ])
    cat_pipe = Pipeline([
        ("imp", SimpleImputer(strategy="most_frequent")),
        ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    
    return ColumnTransformer(
        transformers=[
            ("num", num_pipe, num_cols),
            ("cat", cat_pipe, cat_cols)
        ],
        remainder="drop",
        sparse_threshold=0.0
    )

def train_model(X: pd.DataFrame, y: pd.Series, model_type: str):
    """
    训练模型
    """
    try:
        # 验证模型类型
        if model_type not in BEST_PARAMS:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # 验证输入数据
        if X is None or X.empty:
            raise ValueError("Input features cannot be empty")
        
        if y is None or y.empty:
            raise ValueError("Target values cannot be empty")
        
        # 验证特征列
        if model_type in FEATURE_COLS:
            required_cols = FEATURE_COLS[model_type]
            missing_cols = [col for col in required_cols if col not in X.columns]
            if missing_cols:
                raise ValueError(f"Missing required features: {missing_cols}")
        
        params = BEST_PARAMS[model_type]
        model_name = params["model"]
        model_params = params["params"]
        
        preprocessor = build_preprocessor(X)
        preprocessor.fit(X)
        X_transformed = preprocessor.transform(X)
        
        if model_name == "SVR":
            model = SVR(**model_params)
        elif model_name == "CAT":
            model = CatBoostRegressor(**model_params, verbose=False, random_seed=42, allow_writing_files=False)
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        
        model.fit(X_transformed, y)
        
        # 保存模型
        model_data = {
            "model": model,
            "preprocessor": preprocessor,
            "feature_cols": FEATURE_COLS[model_type],
            "model_type": model_type
        }
        
        # 确保模型目录存在
        MODEL_DIR.mkdir(exist_ok=True)
        
        with open(MODEL_FILES[model_type], "wb") as f:
            pickle.dump(model_data, f)
        
        return model, preprocessor
    except Exception as e:
        raise ValueError(f"Error training model: {str(e)}")

def load_model(model_type: str):
    """
    加载模型
    """
    model_file = MODEL_FILES[model_type]
    if not model_file.exists():
        return None, None
    
    with open(model_file, "rb") as f:
        model_data = pickle.load(f)
    
    return model_data["model"], model_data["preprocessor"]

def predict_with_model(model, preprocessor, X: pd.DataFrame):
    """
    使用模型进行预测
    """
    X_transformed = preprocessor.transform(X)
    return model.predict(X_transformed)

def is_model_available(model_type: str):
    """
    检查模型是否可用
    """
    return MODEL_FILES[model_type].exists()
