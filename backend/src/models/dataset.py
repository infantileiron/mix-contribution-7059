from sqlalchemy import String, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.config.database import Base


class ConsumptionDataset(Base):
    __tablename__ = "consumption_datasets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    source: Mapped[str] = mapped_column(String)
    rows: Mapped[list] = mapped_column(JSON)
    # 当前观测版本号，每次修订 +1；rows 始终保存当前版本的数据
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String)
