"""
特征转换模块
负责从原始输入转换为模型所需的特征
"""

import math
import numpy as np
import pandas as pd

# 基础常数
ELEMENTS = ["Cu", "Al", "Cr", "Mg", "Ni", "Si", "Zr"]

ATOMIC_MASS = {
    "Cu": 63.546, "Al": 26.982, "Cr": 51.996,
    "Mg": 24.305, "Ni": 58.693, "Si": 28.085, "Zr": 91.224,
}

ATOMIC_RADIUS = {
    "Cu": 1.28, "Al": 1.43, "Cr": 1.28,
    "Mg": 1.60, "Ni": 1.24, "Si": 1.11, "Zr": 1.60,
}

ELECTRONEGATIVITY = {
    "Cu": 1.90, "Al": 1.61, "Cr": 1.66,
    "Mg": 1.31, "Ni": 1.91, "Si": 1.90, "Zr": 1.33,
}

VEC = {
    "Cu": 11, "Al": 3, "Cr": 6,
    "Mg": 2, "Ni": 10, "Si": 4, "Zr": 4,
}

MELTING_POINT = {
    "Cu": 1084.62, "Al": 660.32, "Cr": 1907.0,
    "Mg": 650.0, "Ni": 1455.0, "Si": 1414.0, "Zr": 1855.0,
}

PROCESSING_MAP = {
    "Solution ==> Quenching ==> Aging": 0,
    "Solution ==> Quenching ==> Deformation ==> Aging": 1,
    "Solution ==> Quenching ==> Deformation ==> Aging ==> Secondary TMP ==> Secondary Aging": 2,
}

def extract_number(value) -> float:
    """
    从值中提取数值
    """
    if value is None:
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == "" or s.upper() in {"N", "NA", "N/A", "NONE", "NAN"}:
        return np.nan
    try:
        return float(s)
    except:
        return np.nan

def wt_to_mole_fraction(wt: dict) -> dict:
    """
    重量百分比转换为摩尔分数
    """
    moles = {el: wt.get(el, 0) / ATOMIC_MASS[el] for el in ELEMENTS}
    total = sum(moles.values())
    if total <= 0:
        return {el: 0.0 for el in ELEMENTS}
    return {el: moles[el] / total for el in ELEMENTS}

def calc_composition_features(xi: dict) -> dict:
    """
    计算成分特征
    """
    feats = {}
    
    # 平均熔点 Tmavg (℃)
    feats["Tmavg"] = sum(xi[el] * MELTING_POINT[el] for el in ELEMENTS)
    
    # 平均价电子浓度 VECavg
    feats["VECavg"] = sum(xi[el] * VEC[el] for el in ELEMENTS)
    
    # 原子尺寸错配 δ
    R_avg = sum(xi[el] * ATOMIC_RADIUS[el] for el in ELEMENTS)
    feats["δ"] = math.sqrt(
        sum(xi[el] * (1 - ATOMIC_RADIUS[el] / R_avg) ** 2 for el in ELEMENTS)
    ) if R_avg > 0 else 0.0
    
    # 电负性方差 χvar
    chi_avg = sum(xi[el] * ELECTRONEGATIVITY[el] for el in ELEMENTS)
    feats["χvar"] = sum(
        xi[el] * (ELECTRONEGATIVITY[el] - chi_avg) ** 2 for el in ELEMENTS
    )
    
    # 混合熵 Smix (J/mol·K)
    feats["Smix"] = -8.314 * sum(
        xi[el] * math.log(xi[el]) for el in ELEMENTS if xi[el] > 0
    )
    
    # HHI（成分集中度）
    feats["HHI"] = sum(xi[el] ** 2 for el in ELEMENTS)
    
    # N_eff（等效参与元素数）
    feats["N_eff"] = 1.0 / feats["HHI"] if feats["HHI"] > 0 else np.nan
    
    return feats

def classify_family(cr_wt: float, ni_wt: float, si_wt: float) -> int:
    """
    合金体系分类
    """
    has_cr = cr_wt > 0
    has_ni_si = (ni_wt > 0) and (si_wt > 0)
    
    if has_cr and has_ni_si:
        return 2
    elif has_cr:
        return 1
    else:
        return 0

def calc_process_features(processing_params: dict, processing_route: str) -> dict:
    """
    计算工艺特征
    """
    feats = {}
    
    # 提取工艺参数
    s_tem = extract_number(processing_params.get("Solution_Temperature", np.nan))
    a_tem = extract_number(processing_params.get("Aging_Temperature", np.nan))
    a_time = extract_number(processing_params.get("Aging_Time", np.nan))
    cr_red = extract_number(processing_params.get("CR_Reduction/%", 0))
    
    # One-Hot-Processing
    has_secondary = "Secondary" in processing_route
    if has_secondary:
        feats["One-Hot-Processing"] = 2
    else:
        feats["One-Hot-Processing"] = PROCESSING_MAP.get(processing_route, 0)
    
    # 计算工艺衍生特征
    cr_frac = cr_red / 100.0 if not math.isnan(cr_red) else 0.0
    
    feats["CR_x_ATem"] = cr_frac * a_tem if not math.isnan(a_tem) else np.nan
    feats["ATem_x_Atime"] = a_tem * a_time if not (math.isnan(a_tem) or math.isnan(a_time)) else np.nan
    feats["STem-ATem"] = s_tem - a_tem if not (math.isnan(s_tem) or math.isnan(a_tem)) else np.nan
    
    return feats

def transform_input(alloy_composition: dict, processing_params: dict, processing_route: str) -> pd.DataFrame:
    """
    将原始输入转换为模型所需的特征
    """
    try:
        # 验证输入参数
        if not isinstance(alloy_composition, dict):
            alloy_composition = {}
        
        if not isinstance(processing_params, dict):
            processing_params = {}
        
        if not isinstance(processing_route, str):
            processing_route = ""
        
        # 提取元素重量百分比
        wt = {el: extract_number(alloy_composition.get(el, 0)) for el in ELEMENTS}
        
        # 转换为摩尔分数
        xi = wt_to_mole_fraction(wt)
        
        # 计算成分特征
        comp_feats = calc_composition_features(xi)
        
        # 计算工艺特征
        proc_feats = calc_process_features(processing_params, processing_route)
        
        # 计算其他特征
        ni_si_wt = wt.get("Ni", 0) + wt.get("Si", 0)
        family = classify_family(wt.get("Cr", 0), wt.get("Ni", 0), wt.get("Si", 0))
        
        # 构建特征字典
        features = {
            **comp_feats,
            **proc_feats,
            "Si/wt.%": wt.get("Si", 0),
            "Mg/(Ni+Si)": wt.get("Mg", 0) / ni_si_wt if ni_si_wt > 0 else 0.0,
            "Family": family
        }
        
        # 处理缺失值
        for key, value in features.items():
            if pd.isna(value) or (isinstance(value, float) and math.isnan(value)):
                features[key] = 0.0 if key in ["Family"] else np.nan
        
        # 转换为DataFrame
        return pd.DataFrame([features])
    except Exception as e:
        # 返回默认特征值
        default_features = {
            "HHI": 0.0,
            "N_eff": 0.0,
            "Tmavg": 0.0,
            "δ": 0.0,
            "VECavg": 0.0,
            "χvar": 0.0,
            "Smix": 0.0,
            "CR_x_ATem": 0.0,
            "ATem_x_Atime": 0.0,
            "STem-ATem": 0.0,
            "One-Hot-Processing": 0,
            "Si/wt.%": 0.0,
            "Mg/(Ni+Si)": 0.0,
            "Family": 0
        }
        return pd.DataFrame([default_features])
