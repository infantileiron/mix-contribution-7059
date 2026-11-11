from pydantic import BaseModel,Field,model_validator
class ComparisonInput(BaseModel):
 name:str=Field(min_length=2,max_length=120)
 dataset_id:str
 period_before:str=Field(pattern=r"^20\d{2}-(0[1-9]|1[0-2])$")
 period_after:str=Field(pattern=r"^20\d{2}-(0[1-9]|1[0-2])$")
 @model_validator(mode="after")
 def periods(self):
  if self.period_before==self.period_after:raise ValueError("请选择两个不同月份；若观测数值相同将得到零贡献")
  return self
