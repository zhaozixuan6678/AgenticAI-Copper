"""
Cu合金完整特征工程流水线 
=====================================
输入 : 原始文献数据表格 (如 Feature-Caculation.xlsx 的 Input sheet)
输出 : 与 Feature.xlsx 格式完全一致的特征表

"""

import re
import math
import warnings
import numpy as np
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")

# =========================================================
# 基础常数
# =========================================================
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

OUTPUT_COLUMNS = [
    "ID", "CR_x_ATem", "ATem_x_Atime", "STem-ATem", "One-Hot-Processing",
    "HHI", "N_eff", "Tmavg", "Family", "Si/wt.%", "δ", "VECavg", "Mg/(Ni+Si)",
    "χvar", "Smix", "Hardness/HV", "EC/%IACS", "Q3-Euclidean",
]

# =========================================================
# 工具函数
# =========================================================
def extract_number(value) -> float:
    """从 '3.3/wt.%'、'699.85/℃'、'64/%IACS' 等格式中提取数值"""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == "" or s.upper() in {"N", "NA", "N/A", "NONE", "NAN"}:
        return np.nan
    m = re.search(r"-?\d+\.?\d*", s)
    return float(m.group()) if m else np.nan


def safe_get(row, col, default=np.nan):
    """安全获取行中的列值"""
    return row[col] if col in row.index else default


# =========================================================
# 核心特征计算
# =========================================================
def calc_features(row):
    """计算单行的所有特征"""
    r = {}

    # 1. ID
    r["ID"] = safe_get(row, "ID", np.nan)

    # 2. 提取元素 wt%
    wt = {}
    for el in ELEMENTS:
        wt[el] = extract_number(safe_get(row, el, 0))
        if math.isnan(wt[el]):
            wt[el] = 0.0

    # 如果主要元素都没有，跳过
    if sum(wt.values()) <= 0:
        return None

    # 3. wt% -> 摩尔分数
    mol = {el: wt[el] / ATOMIC_MASS[el] for el in ELEMENTS}
    tot_mol = sum(mol.values())
    if tot_mol <= 0:
        return None

    xi = {el: mol[el] / tot_mol for el in ELEMENTS}

    # 4. 成分热力学 / 物理特征
    r["Tmavg"] = sum(xi[el] * MELTING_POINT[el] for el in ELEMENTS)
    r["VECavg"] = sum(xi[el] * VEC[el] for el in ELEMENTS)

    r_avg = sum(xi[el] * ATOMIC_RADIUS[el] for el in ELEMENTS)
    if r_avg > 0:
        r["δ"] = math.sqrt(sum(xi[el] * (1 - ATOMIC_RADIUS[el] / r_avg) ** 2 for el in ELEMENTS))
    else:
        r["δ"] = np.nan

    chi_avg = sum(xi[el] * ELECTRONEGATIVITY[el] for el in ELEMENTS)
    r["χvar"] = sum(xi[el] * (ELECTRONEGATIVITY[el] - chi_avg) ** 2 for el in ELEMENTS)

    r["Smix"] = -8.314 * sum(xi[el] * math.log(xi[el]) for el in ELEMENTS if xi[el] > 0)
    r["HHI"] = sum(xi[el] ** 2 for el in ELEMENTS)
    r["N_eff"] = 1.0 / r["HHI"] if r["HHI"] > 0 else np.nan

    ni_si = wt["Ni"] + wt["Si"]
    r["Mg/(Ni+Si)"] = wt["Mg"] / ni_si if ni_si > 0 else 0.0
    r["Si/wt.%"] = wt["Si"]

    # 5. 合金 Family 分类
    has_cr = wt["Cr"] > 0
    has_ni_si = (wt["Ni"] > 0) and (wt["Si"] > 0)

    if has_cr and has_ni_si:
        r["Family"] = 2
    elif has_cr:
        r["Family"] = 1
    else:
        r["Family"] = 0

    # 6. 工艺参数解析
    s_tem = extract_number(safe_get(row, "Solution_Temperature"))
    a_tem = extract_number(safe_get(row, "Aging_Temperature"))
    a_time = extract_number(safe_get(row, "Aging_Time"))
    cr_red = extract_number(safe_get(row, "CR_Reduction/%"))

    proc = str(safe_get(row, "Processing_route", "")).strip()
    sec = str(safe_get(row, "Secondary TMP", "")).strip().upper()

    has_sec = sec not in ("", "N", "NA", "N/A", "NONE", "NAN")
    r["One-Hot-Processing"] = 2 if has_sec else PROCESSING_MAP.get(proc, 0)

    cf = cr_red / 100.0 if not math.isnan(cr_red) else 0.0
    r["CR_x_ATem"] = cf * a_tem if not math.isnan(a_tem) else np.nan
    r["ATem_x_Atime"] = a_tem * a_time if not (math.isnan(a_tem) or math.isnan(a_time)) else np.nan
    r["STem-ATem"] = s_tem - a_tem if not (math.isnan(s_tem) or math.isnan(a_tem)) else np.nan

    # 7. 目标变量
    r["Hardness/HV"] = extract_number(safe_get(row, "Hardness"))
    r["EC/%IACS"] = extract_number(safe_get(row, "EC"))

    return r


# =========================================================
# 计算 Q3-Euclidean
# =========================================================
def add_q3(df):
    """计算 Q3-Euclidean 综合评价指标"""
    df = df.copy()

    mask = df["Hardness/HV"].notna() & df["EC/%IACS"].notna()
    if mask.sum() < 2:
        df["Q3-Euclidean"] = np.nan
        return df

    hv = df.loc[mask, "Hardness/HV"].astype(float)
    ec = df.loc[mask, "EC/%IACS"].astype(float)

    hv_std = hv.std(ddof=1)
    ec_inv = 100 - ec
    ec_std = ec_inv.std(ddof=1)

    if hv_std == 0 or ec_std == 0:
        df["Q3-Euclidean"] = np.nan
        return df

    z_hv = (hv - hv.mean()) / hv_std
    z_ec = (ec_inv - ec_inv.mean()) / ec_std

    df["Q3-Euclidean"] = np.nan
    df.loc[mask, "Q3-Euclidean"] = np.sqrt(z_hv.values ** 2 + z_ec.values ** 2)
    return df


# =========================================================
# 主流程
# =========================================================
def run(input_path, output_path, sheet="Input"):
    """主运行函数"""
    input_path = Path(input_path)
    output_path = Path(output_path)

    # 读取原始数据
    df_raw = pd.read_excel(input_path, sheet_name=sheet, dtype=object)
    print(f"读取: {df_raw.shape[0]} 行 × {df_raw.shape[1]} 列  <-  {input_path.name} [{sheet}]")

    # 计算特征
    records = []
    for _, row in df_raw.iterrows():
        feat = calc_features(row)
        if feat is not None:
            records.append(feat)

    if len(records) == 0:
        raise ValueError("没有成功提取任何特征，请检查输入表列名和内容。")

    df_feat = pd.DataFrame(records)

    # 筛选有效数据行（至少 Hardness 或 EC 之一非空）
    valid = df_feat["Hardness/HV"].notna() | df_feat["EC/%IACS"].notna()
    df_feat = df_feat[valid].reset_index(drop=True)
    print(f"筛选后: {df_feat.shape[0]} 行（有 Hardness 或 EC 值）")

    # 计算 Q3-Euclidean
    df_feat = add_q3(df_feat)

    # 补齐缺失列并按固定顺序输出
    for c in OUTPUT_COLUMNS:
        if c not in df_feat.columns:
            df_feat[c] = np.nan

    df_out = df_feat[OUTPUT_COLUMNS].reset_index(drop=True)

    # 保存输出
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_out.to_excel(writer, sheet_name="Feature", index=False)

    print(f"输出: {df_out.shape[0]} 行 × {df_out.shape[1]} 列  ->  {output_path.name}")

    # 统计汇报
    print("\n" + "=" * 60)
    print("  输出列统计:")
    for i, col in enumerate(OUTPUT_COLUMNS, 1):
        non_null = df_out[col].notna().sum()
        print(f"  {i:2d}. {col:<22s}  非空行: {non_null}")

    print(f"\n  ✓ 总行数      : {len(df_out)}")
    print(f"  ✓ Hardness 行 : {df_out['Hardness/HV'].notna().sum()}")
    print(f"  ✓ EC 行       : {df_out['EC/%IACS'].notna().sum()}")
    print(f"  ✓ Q3 行       : {df_out['Q3-Euclidean'].notna().sum()}")
    print("=" * 60)

    return df_out


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cu合金完整特征工程流水线")
    parser.add_argument("--input", default="Agent/Feature-Caculation.xlsx", help="原始输入表格路径")
    parser.add_argument("--output", default="Agent/Feature_Output_Fixed.xlsx", help="特征输出表格路径")
    parser.add_argument("--sheet", default="Input", help="输入 sheet 名，默认 Input")

    args = parser.parse_args()
    run(args.input, args.output, args.sheet)
