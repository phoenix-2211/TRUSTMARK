from sqlalchemy import Column, String, Integer, Text, JSON
from app.db.database import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(String, primary_key=True, index=True)
    payment_id = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # in paise
    currency = Column(String, default="INR")
    reason_code = Column(String, nullable=False)
    respond_by = Column(Integer, nullable=False)  # Unix timestamp
    status = Column(String, default="open")
    phase = Column(String, default="chargeback")


class OrderRecord(Base):
    __tablename__ = "order_records"

    order_id = Column(String, primary_key=True, index=True)
    payment_id = Column(String, nullable=False, index=True)
    customer_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")
    order_date = Column(Integer, nullable=False)
    shipping_address = Column(Text, nullable=False)
    ip_address = Column(String, nullable=False)
    device_id = Column(String, nullable=False)


class ShipmentRecord(Base):
    __tablename__ = "shipment_records"

    shipment_id = Column(String, primary_key=True, index=True)
    order_id = Column(String, nullable=False, index=True)
    tracking_number = Column(String, nullable=False)
    carrier = Column(String, nullable=False)
    shipped_date = Column(Integer, nullable=False)
    delivery_date = Column(Integer, nullable=True)
    delivery_address = Column(Text, nullable=False)
    carrier_status = Column(String, nullable=False)
    proof_doc_id = Column(String, nullable=True)


class DisputeEvidence(Base):
    __tablename__ = "dispute_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dispute_id = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    shipping_proof = Column(JSON, nullable=True)
    billing_proof = Column(JSON, nullable=True)
    cancellation_proof = Column(JSON, nullable=True)
    customer_communication = Column(JSON, nullable=True)
    proof_of_service = Column(JSON, nullable=True)
    explanation_letter = Column(JSON, nullable=True)
    refund_confirmation = Column(JSON, nullable=True)
    access_activity_log = Column(JSON, nullable=True)
    refund_cancellation_policy = Column(JSON, nullable=True)
    term_and_conditions = Column(JSON, nullable=True)
    others = Column(JSON, nullable=True)
    submitted_at = Column(Integer, nullable=True)


class CustomerCommunicationLog(Base):
    __tablename__ = "customer_communication_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False, index=True)
    log_text = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)


class EvaluationGroundTruth(Base):
    __tablename__ = "evaluation_ground_truth"

    dispute_id = Column(String, primary_key=True, index=True)
    has_address_mismatch = Column(Integer, default=0)
    has_date_impossibility = Column(Integer, default=0)
    has_amount_mismatch = Column(Integer, default=0)
    has_comms_contradiction = Column(Integer, default=0)
    expected_verdict = Column(String, nullable=False)
    dataset_split = Column(String, default="train_dev")
