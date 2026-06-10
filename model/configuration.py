from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
from persistence.db_config import Base


# Tabella di join N:M tra configuration e optional
configuration_optional = Table(
    "configuration_optional",
    Base.metadata,
    Column("configuration_id", Integer, ForeignKey("configuration.configuration_id"), primary_key=True),
    Column("optional_id", Integer, ForeignKey("optional.optional_id"), primary_key=True),
)


class Configuration(Base):
    __tablename__ = "configuration"

    configuration_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="draft")  # "draft" | "saved" | "quoted"
    total_price = Column(Numeric(10, 2), nullable=False, default=0)

    client_id = Column(Integer, ForeignKey("client.client_id"), nullable=False)
    model_id = Column(Integer, ForeignKey("model.model_id"), nullable=False)
    engine_id = Column(Integer, ForeignKey("engine.engine_id"), nullable=False)

    client = relationship("Client",   back_populates="configurations")
    car_model = relationship("CarModel", back_populates="configurations")
    engine = relationship("Engine")
    optionals = relationship("Optional", secondary="configuration_optional")
    quote = relationship("Quote", back_populates="configuration", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "configuration_id": self.configuration_id,
            "name": self.name,
            "status": self.status,
            "total_price": float(self.total_price),
            "client_id": self.client_id,
        }

    def to_dict_full(self):
        d = self.to_dict()
        d["model"] = self.car_model.to_dict() if self.car_model else None
        d["engine"] = self.engine.to_dict() if self.engine else None
        d["optionals"] = [o.to_dict() for o in self.optionals]
        return d

    def __repr__(self):
        return f"Configuration(id={self.configuration_id}, name={self.name}, status={self.status})"

    def __str__(self):
        return f"{self.name} - {self.status} - {self.total_price}€"