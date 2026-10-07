from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(20), primary_key=True)
    gender = Column(String(10))
    senior_citizen = Column(Integer)
    partner = Column(Integer)
    dependents = Column(Integer)

    # --------------------------------------------------------
    # Relationships — enables customer.contract, customer.billing,
    # customer.service, customer.status instead of manual joins.
    # uselist=False because each customer has exactly one row
    # in each of these tables (one-to-one in this schema).
    # --------------------------------------------------------
    contract = relationship(
        "Contract", back_populates="customer", uselist=False
    )
    billing = relationship(
        "Billing", back_populates="customer", uselist=False
    )
    service = relationship(
        "Service", back_populates="customer", uselist=False
    )
    status = relationship(
        "CustomerStatus", back_populates="customer", uselist=False
    )


class Contract(Base):
    __tablename__ = "contracts"

    contract_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        String(20), ForeignKey("customers.customer_id"), nullable=False
    )
    contract_type = Column(String(30))

    customer = relationship("Customer", back_populates="contract")


class Billing(Base):
    __tablename__ = "billing"

    billing_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        String(20), ForeignKey("customers.customer_id"), nullable=False
    )
    tenure = Column(Integer)
    paperless_billing = Column(String(10))
    payment_method = Column(String(50))
    monthly_charges = Column(DECIMAL(10, 2))
    total_charges = Column(DECIMAL(10, 2))

    customer = relationship("Customer", back_populates="billing")


class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        String(20), ForeignKey("customers.customer_id"), nullable=False
    )
    phone_service = Column(String(10))
    multiple_lines = Column(String(30))
    internet_service = Column(String(30))
    online_security = Column(String(30))
    online_backup = Column(String(30))
    device_protection = Column(String(30))
    tech_support = Column(String(30))
    streaming_tv = Column(String(30))
    streaming_movies = Column(String(30))

    customer = relationship("Customer", back_populates="service")


class CustomerStatus(Base):
    __tablename__ = "customer_status"

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        String(20), ForeignKey("customers.customer_id"), nullable=False
    )
    churn = Column(Integer)

    customer = relationship("Customer", back_populates="status")