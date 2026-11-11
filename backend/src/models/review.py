from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.config.database import Base


class DriverReview(Base):
    __tablename__ = "driver_reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String)
    note: Mapped[str] = mapped_column(Text)
    decision: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    # 复核时分解运行锁定的观测版本；旧版本复核不能批准新版本报告
    dataset_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String)
