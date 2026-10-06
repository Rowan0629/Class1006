# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas"]
# ///
"""把 data/ 的三個 CSV 整理成網頁可直接載入的 docs/data.js（file:// 也能開）。"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
rd = lambda n: pd.read_csv(ROOT / "data" / n, encoding="utf-8-sig")

enr = (rd("enrollment.csv")
       .groupby(["semester", "college", "dept", "degree", "gender"], as_index=False)["count"].sum())
leave = (rd("leave.csv")
         .groupby(["semester", "college", "dept", "degree", "gender", "reason"], as_index=False)
         [["new_leave", "on_leave_end"]].sum())
leave = leave[(leave.new_leave != 0) | (leave.on_leave_end != 0)]
dm = rd("dept_mapping.csv").fillna("")
depts = [dict(dept=r.dept, college=r.college, aliases=[a for a in r.aliases.split(";") if a])
         for r in dm.itertuples()]

def table(df):  # 欄名 + 列陣列，比物件陣列小
    return dict(columns=list(df.columns), rows=df.values.tolist())

data = dict(enrollment=table(enr), leave=table(leave), depts=depts)
out = ROOT / "docs" / "data.js"
out.write_text("window.DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":"),
               default=int) + ";\n", encoding="utf-8")

total = int(enr[enr.semester == "114-1"]["count"].sum())
print(f"114-1 在學人數合計 {total} {'OK' if total == 10035 else '不符！'}")
print(f"在學 {len(enr)} 列、休學 {len(leave)} 列、系所 {len(depts)} 筆；{out.stat().st_size/1024:.0f} KB")
