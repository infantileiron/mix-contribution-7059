from sqlalchemy import String,Float,Integer,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DriverReview(Base):
 __tablename__="driver_reviews"
 id:Mapped[str]=mapped_column(String,primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("decomposition_runs.id"))
 note:Mapped[str]=mapped_column(Text)
 decision:Mapped[str]=mapped_column(String)
 author:Mapped[str]=mapped_column(String)
 created_at:Mapped[str]=mapped_column(String)
