from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from persistence.db_config import Base


class CompatibilityRule(Base):
    __tablename__ = "compatibility_rule"

    rule_id = Column(Integer, primary_key=True, autoincrement=True)
    rule_type = Column(String(50), nullable=False)  # "incompatible" | "requires"

    compatibilities = relationship("Compatibility", back_populates="rule", cascade="all, delete-orphan")

    def to_dict(self):
        return {"rule_id": self.rule_id, "rule_type": self.rule_type}

    def __repr__(self):
        return f"CompatibilityRule(rule_id={self.rule_id}, rule_type={self.rule_type})"

    def __str__(self):
        return f"Regola: {self.rule_type}"


class Compatibility(Base):
    __tablename__ = "compatibility"

    compatibility_id = Column(Integer, primary_key=True, autoincrement=True)
    optional_id = Column(Integer, ForeignKey("optional.optional_id"), nullable=False)
    optional_with_id = Column(Integer, ForeignKey("optional.optional_id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("compatibility_rule.rule_id"), nullable=False)

    # foreign_keys esplicite perché ci sono due FK verso la stessa tabella
    optional = relationship("Optional", foreign_keys=[optional_id])
    optional_with = relationship("Optional", foreign_keys=[optional_with_id])
    rule = relationship("CompatibilityRule", back_populates="compatibilities")

    def to_dict(self):
        return {
            "compatibility_id": self.compatibility_id,
            "optional_id": self.optional_id,
            "optional_with_id": self.optional_with_id,
            "rule_type": self.rule.rule_type if self.rule else None,
        }

    def __repr__(self):
        return f"Compatibility(id={self.compatibility_id}, opt_a={self.optional_id}, opt_b={self.optional_with_id})"

    def __str__(self):
        return f"Optional {self.optional_id} <-> Optional {self.optional_with_id} [{self.rule.rule_type if self.rule else '?'}]"