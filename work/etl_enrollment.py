# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "xlrd"]
# ///
"""把 114-1 在學人數統計表（.xls 第一個工作表）轉成整齊的 CSV。"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / "東華大學統計資料" / "在學人數統計表").glob("114-1*.xls"))
OUT = ROOT / "work" / "enrollment_114-1.csv"

SECTIONS = {"博士班": "博士班", "碩士班": "碩士班", "碩專班": "碩士在職專班", "學士班": "學士班"}
strip_note = lambda s: re.sub(r"[（(].*?[)）]", "", s).strip()

df = pd.read_excel(SRC, sheet_name=0, header=None)  # 只讀第一個工作表

rows, program, college, dept = [], None, None, None
for _, r in df.iloc[3:].iterrows():
    c0 = r[0].strip() if isinstance(r[0], str) else ""
    if c0.startswith("備註"):
        break
    m = re.match(r"(博士班|碩士班|碩專班|學士班)\s*合計", c0)
    if m:                                   # 區段標題列（合計）：切換學制，不輸出
        program, college, dept = SECTIONS[m.group(1)], None, None
        continue
    if program is None or pd.isna(r[4]):    # 總計列等
        continue
    # 合併儲存格：名稱只在第一格，向下沿用
    if isinstance(r[1], str): college = strip_note(r[1])
    if isinstance(r[2], str): dept = r[2].strip()
    # 報表合併範圍有誤：博士班「應用物理博士班一般組」被併進上一列的材料系，實屬物理學系
    d = "物理學系" if isinstance(r[3], str) and r[3].startswith("應用物理") else dept
    for gender, col in (("女", 5), ("男", 6)):
        n = r[col]
        rows.append(dict(college=college, dept_raw=d, program_raw=program,
                         gender=gender, count=0 if pd.isna(n) else int(n)))

out = (pd.DataFrame(rows)
       .groupby(["college", "dept_raw", "program_raw", "gender"], sort=False, as_index=False)["count"].sum())
out.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"{len(out)} 列，總人數 {out['count'].sum()} → {OUT}")
