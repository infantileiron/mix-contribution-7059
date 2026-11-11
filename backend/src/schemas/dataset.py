from pydantic import BaseModel,Field,model_validator
class Observation(BaseModel):
 zone:str=Field(min_length=1,max_length=60)
 period:str=Field(pattern=r"^20\d{2}-(0[1-9]|1[0-2])$")
 scale:float=Field(gt=0,le=1000000000,allow_inf_nan=False)
 water:float=Field(gt=0,le=1000000000,allow_inf_nan=False)
class DatasetInput(BaseModel):
 name:str=Field(min_length=2,max_length=120)
 source:str=Field(default="water_observations.json",max_length=120)
 rows:list[Observation]=Field(min_length=2,max_length=5000)
 @model_validator(mode="after")
 def unique(self):
  keys=[(r.zone,r.period) for r in self.rows]
  if len(keys)!=len(set(keys)):raise ValueError("分区与月份不能重复")
  return self
