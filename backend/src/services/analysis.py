import math,hashlib,json
from src.services.periods import prepare,quantities
from src.services.shapley import shapley
from src.services.lmdi import lmdi
def analyze(rows,before,after):
 zones,a,b=prepare(rows,before,after);q0=quantities(a);q1=quantities(b)
 return {"period_before":before,"period_after":after,"water_before":math.fsum(q0),"water_after":math.fsum(q1),"delta":math.fsum(q1)-math.fsum(q0),"scale_before":a["scale"],"scale_after":b["scale"],"share_sum_before":math.fsum(a["structure"]),"share_sum_after":math.fsum(b["structure"]),"shapley":shapley(a,b,zones),"lmdi":lmdi(a,b,zones),"observations":[{"zone":z,"scale_before":a["scale"]*a["structure"][i],"scale_after":b["scale"]*b["structure"][i],"share_before":a["structure"][i],"share_after":b["structure"][i],"intensity_before":a["intensity"][i],"intensity_after":b["intensity"][i],"water_before":q0[i],"water_after":q1[i]} for i,z in enumerate(zones)],"checksum":hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),"assumptions":["规模为各分区有效作业人日之和，占比=分区规模/总规模，强度=分区用水量/分区规模。","两期分区严格对齐，规模与水量必须为正；零值或负值一律拒绝，不加epsilon、不静默补零。","Shapley与LMDI采用不同的交互分摊口径，各自对同一总变化闭合；因子数值可以不同。","分解是会计恒等式归因，不代表节水措施的因果效果。口径变更和天气等未建模因素需人工复核。"]}
