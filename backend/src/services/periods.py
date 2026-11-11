import math
def prepare(rows,before,after):
 def period(name):
  selected=[r for r in rows if r["period"]==name]
  if not selected:raise ValueError("月份没有观测："+name)
  zones=[r["zone"] for r in selected]
  if len(zones)!=len(set(zones)):raise ValueError("月份内分区重复")
  for row in selected:
   if any(not math.isfinite(row[k]) or row[k]<=0 for k in ("scale","water")):raise ValueError("规模与用水必须为有限正值；零值不能用epsilon替换")
  return {r["zone"]:r for r in selected}
 a=period(before);b=period(after)
 if set(a)!=set(b):raise ValueError("两期分区不一致，禁止补零或静默丢弃分区")
 zones=sorted(a)
 def factors(data):
  total=math.fsum(r["scale"] for r in data.values())
  shares=[data[z]["scale"]/total for z in zones];intensities=[data[z]["water"]/data[z]["scale"] for z in zones]
  if not math.isfinite(total) or any(not math.isfinite(x) for x in shares+intensities):raise ValueError("量纲超出有限数值范围，请核查输入")
  return {"scale":total,"structure":shares,"intensity":intensities}
 return zones,factors(a),factors(b)
def quantities(factors):return [factors["scale"]*w*i for w,i in zip(factors["structure"],factors["intensity"])]
