import os
import pandas as pd

def load_cepii_data():
    """读取CEPII距离数据，返回DataFrame。"""
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'dist_cepii', 'dist_cepii.xls'))
    df = pd.read_excel(data_path, sheet_name=0)
    return df

def construct_border_friction(df):
    """
    用等权重法构造边境摩擦指数。
    指数 = 1 - (contig + comlang_off + colony) / 3
    """
    df_border = df[['iso_o', 'iso_d', 'contig', 'comlang_off', 'colony']].copy()
    df_border['border_friction'] = 1 - (
        (df_border['contig'] + df_border['comlang_off'] + df_border['colony']) / 3
    )
    return df_border

def save_border_friction(df_border):
    """保存边境摩擦指数面板。"""
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'border_friction_panel_ew.csv'))
    df_border.to_csv(out_path, index=False)
    print(f"已保存边境摩擦面板 {out_path}")

def main():
    # 1. 读取CEPII原始数据
    df = load_cepii_data()
    # 2. 构造边境摩擦指数
    df_border = construct_border_friction(df)
    # 3. 保存结果
    save_border_friction(df_border)
    # 4. 可选：输出分布统计，便于后续分析
    print(df_border['border_friction'].describe())
    print("缺失值数量：", df_border['border_friction'].isnull().sum())

if __name__ == '__main__':
    main()