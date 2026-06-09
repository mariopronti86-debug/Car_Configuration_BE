from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from persistence.db_config import Base
 
 
class User(Base):
    __tablename__ = "app_user"
 
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), nullable=False)   # discriminante: "client" | "admin"
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
 
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "user",
    }
 
    def to_dict(self):
        return {"user_id": self.user_id, "type": self.type, "email": self.email}
    
    def __repr__(self):
        return f"User(user_id={self.user_id}, email={self.email}, type={self.type})"
 
    def __str__(self):
        return f"{self.email} [{self.type}]"
 
 
class Client(User):
    __tablename__ = "client"
 
    client_id = Column(Integer, ForeignKey("app_user.user_id"), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(30))
 
    configurations = relationship("Configuration", back_populates="client", cascade="all, delete-orphan")
 
    __mapper_args__ = {"polymorphic_identity": "client"}
 
    def to_dict(self):
        d = super().to_dict()
        d.update({"first_name": self.first_name, "last_name": self.last_name, "phone": self.phone})
        return d
    
    def __repr__(self):
        return f"Client(client_id={self.client_id}, nome={self.first_name} {self.last_name}, email={self.email})"
 
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
 
 
class Admin(User):
    __tablename__ = "admin"
 
    admin_id = Column(Integer, ForeignKey("app_user.user_id"), primary_key=True)
 
    __mapper_args__ = {"polymorphic_identity": "admin"}

    def __repr__(self):
        return f"Admin(admin_id={self.admin_id}, email={self.email})"
 
    def __str__(self):
        return f"[ADMIN] {self.email}"