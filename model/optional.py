from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from persistence.db_config import Base
 
 
class Optional(Base):
    __tablename__ = "optional"
 
    optional_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    price = Column(Numeric(10, 2), nullable=False, default=0)
 
    car_models = relationship("CarModel", secondary="model_optional", back_populates="optionals")
 
    def to_dict(self):
        return {
            "optional_id": self.optional_id,
            "name": self.name,
            "category": self.category,
            "price": float(self.price),
        }
    
    def __repr__(self):
        return f"Optional(optional_id={self.optional_id}, name={self.name}, category={self.category}, price={self.price})"
 
    def __str__(self):
        return f"{self.name} [{self.category}] - {self.price}€"