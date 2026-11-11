from sqlalchemy import String,Float,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class PeriodComparison(Base):
 __tablename__="period_comparisons"
 id:Mapped[str]=mapped_column(String,primary_key=True)
 name:Mapped[str]=mapped_column(String,unique=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey("consumption_datasets.id"))
 period_before:Mapped[str]=mapped_column(String)
 period_after:Mapped[str]=mapped_column(String)
 created_at:Mapped[str]=mapped_column(String)
