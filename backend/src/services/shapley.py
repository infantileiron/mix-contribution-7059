from itertools import permutations
import math
from src.services.periods import quantities
FACTORS=("scale","structure","intensity")
def shapley(before,after,zones):
 contributions={f:[0.0]*len(zones) for f in FACTORS}
 for order in permutations(FACTORS):
  state=dict(before);last=quantities(state)
  for factor in order:
   state[factor]=after[factor];current=quantities(state)
   for i,(new,old) in enumerate(zip(current,last)):contributions[factor][i]+=(new-old)/6
   last=current
 values={f:math.fsum(v) for f,v in contributions.items()};q0=math.fsum(quantities(before));q1=math.fsum(quantities(after))
 return {"contributions":values,"residual":q1-q0-math.fsum(values.values()),"zones":[{"zone":z,**{f:contributions[f][i] for f in FACTORS}} for i,z in enumerate(zones)],"method":"六排列平均边际贡献，交互项公平分摊"}
