from sqlalchemy import String,Float,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DecompositionRun(Base):
 __tablename__="decomposition_runs"
 id:Mapped[str]=mapped_column(String,primary_key=True)
 comparison_id:Mapped[str]=mapped_column(ForeignKey("period_comparisons.id"))
 status:Mapped[str]=mapped_column(String)
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 error:Mapped[str]=mapped_column(String,default="")
 created_at:Mapped[str]=mapped_column(String)
