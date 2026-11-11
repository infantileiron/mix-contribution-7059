import math
from src.services.periods import quantities
def log_mean(a,b):
 if not math.isfinite(a) or not math.isfinite(b) or a<=0 or b<=0:raise ValueError("LMDI仅接受有限正量")
 if a==b:return a
 relative=(a-b)/b
 denominator=math.log1p(relative) if math.isfinite(relative) and relative>-1 else math.log(a)-math.log(b)
 return (a-b)/denominator
def lmdi(before,after,zones):
 q0=quantities(before);q1=quantities(after);zone_rows=[]
 for i,z in enumerate(zones):
  weight=log_mean(q1[i],q0[i])
  zone_rows.append({"zone":z,"scale":weight*math.log(after["scale"]/before["scale"]),"structure":weight*math.log(after["structure"][i]/before["structure"][i]),"intensity":weight*math.log(after["intensity"][i]/before["intensity"][i])})
 values={f:math.fsum(row[f] for row in zone_rows) for f in ("scale","structure","intensity")}
 return {"contributions":values,"residual":math.fsum(q1)-math.fsum(q0)-math.fsum(values.values()),"zones":zone_rows,"method":"按分区用水对数均值加权的加法LMDI"}
