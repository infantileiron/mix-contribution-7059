from sqlalchemy import String, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.config.database import Base


class ObservationRevision(Base):
    """水表复核后对已导入月度观测的一次修订留痕。"""

    __tablename__ = "observation_revisions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    dataset_id: Mapped[str] = mapped_column(ForeignKey("consumption_datasets.id"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String)
    base_version: Mapped[int] = mapped_column(Integer)
    new_version: Mapped[int] = mapped_column(Integer)
    # 逐条修订内容：[{zone, period, before:{scale,water}, after:{scale,water}}]
    changes: Mapped[list] = mapped_column(JSON, default=list)
    checksum_before: Mapped[str] = mapped_column(String)
    checksum_after: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String)
