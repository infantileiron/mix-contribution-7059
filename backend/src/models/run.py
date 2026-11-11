from sqlalchemy import String, JSON, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.config.database import Base


class DecompositionRun(Base):
    __tablename__ = "decomposition_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    comparison_id: Mapped[str] = mapped_column(ForeignKey("period_comparisons.id"))
    status: Mapped[str] = mapped_column(String)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str] = mapped_column(String, default="")
    # 排队时刻锁定的观测版本，worker 只按该版本快照计算
    dataset_version: Mapped[int] = mapped_column(Integer, default=1)
    # 排队时刻冻结的观测行快照，保证修订后旧运行仍可追溯旧数据
    dataset_snapshot: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[str] = mapped_column(String)
