"""
Auto-Seeding Helper for TRUSTMARK.
Fires on startup if the database is empty (ephemeral cold-start safety for cloud deployments like Render/Vercel).
"""

import time
from app.db.models import (
    Dispute,
    DisputeEvidence,
    OrderRecord,
    ShipmentRecord,
    CustomerCommunicationLog,
)
from app.rules.pipeline import run_verification


def seed_demo_data_if_empty(db):
    """Inserts 5 curated demo disputes if Dispute table is empty."""
    NOW = int(time.time())
    DAY = 86400

    try:
        # CASE 1: READY (Reason Code 13.1)
        disp_1 = Dispute(
            id="disp_N7xK2pQmZ4vL1",
            payment_id="pay_N7xK2pQmZ4vL1",
            amount=1500000,
            currency="INR",
            reason_code="13.1",
            respond_by=NOW + (7 * DAY),
            status="open",
            phase="chargeback",
        )
        ord_1 = OrderRecord(
            order_id="ord_N7xK2pQmZ4vL1",
            payment_id="pay_N7xK2pQmZ4vL1",
            customer_id="cust_N7xK2pQmZ4vL1",
            user_id="usr_N7xK2pQmZ4vL1",
            amount=1500000,
            currency="INR",
            order_date=NOW - (10 * DAY),
            shipping_address="42 MG Road, Indiranagar, Bengaluru, KA 560038",
            ip_address="203.0.113.10",
            device_id="dev_N7xK2pQmZ4vL1",
        )
        ship_1 = ShipmentRecord(
            shipment_id="ship_N7xK2pQmZ4vL1",
            order_id="ord_N7xK2pQmZ4vL1",
            tracking_number="BD1001IN",
            carrier="Bluedart",
            shipped_date=NOW - (8 * DAY),
            delivery_date=NOW - (5 * DAY),
            delivery_address="42 MG Road, Indiranagar, Bengaluru, KA 560038",
            carrier_status="delivered",
            proof_doc_id="doc_ship_N7xK1",
        )
        comm_1 = CustomerCommunicationLog(
            id="comm_N7xK2pQmZ4vL1",
            order_id="ord_N7xK2pQmZ4vL1",
            customer_id="cust_N7xK2pQmZ4vL1",
            timestamp=NOW - (5 * DAY),
            channel="email",
            message_text="Received the shipment today in good condition, thank you!",
        )
        ev_1 = DisputeEvidence(
            dispute_id="disp_N7xK2pQmZ4vL1",
            amount=1500000,
            summary="Clean dispute evidence for Merchandise Not Received.",
            shipping_proof={"doc_id": "doc_ship_N7xK1"},
            customer_communication={"doc_id": "doc_comm_N7xK1"},
            explanation_letter={"doc_id": "doc_expl_N7xK1"},
        )

        # CASE 2: NEEDS REVIEW (Reason Code 13.1 - Missing Explanation Letter)
        disp_2 = Dispute(
            id="disp_R8yL3qRnA5wM2",
            payment_id="pay_R8yL3qRnA5wM2",
            amount=2500000,
            currency="INR",
            reason_code="13.1",
            respond_by=NOW + (3 * DAY),
            status="open",
            phase="chargeback",
        )
        ord_2 = OrderRecord(
            order_id="ord_R8yL3qRnA5wM2",
            payment_id="pay_R8yL3qRnA5wM2",
            customer_id="cust_R8yL3qRnA5wM2",
            user_id="usr_R8yL3qRnA5wM2",
            amount=2500000,
            currency="INR",
            order_date=NOW - (12 * DAY),
            shipping_address="15 Park Street, Kolkata, WB 700016",
            ip_address="203.0.113.20",
            device_id="dev_R8yL3qRnA5wM2",
        )
        ship_2 = ShipmentRecord(
            shipment_id="ship_R8yL3qRnA5wM2",
            order_id="ord_R8yL3qRnA5wM2",
            tracking_number="DLH9900IN",
            carrier="Delhivery",
            shipped_date=NOW - (10 * DAY),
            delivery_date=NOW - (7 * DAY),
            delivery_address="15 Park Street, Kolkata, WB 700016",
            carrier_status="delivered",
            proof_doc_id="doc_ship_R8yL2",
        )
        comm_2 = CustomerCommunicationLog(
            id="comm_R8yL3qRnA5wM2",
            order_id="ord_R8yL3qRnA5wM2",
            customer_id="cust_R8yL3qRnA5wM2",
            timestamp=NOW - (7 * DAY),
            channel="email",
            message_text="Inquiring about delivery status. Thank you for confirming delivery.",
        )
        ev_2 = DisputeEvidence(
            dispute_id="disp_R8yL3qRnA5wM2",
            amount=2500000,
            summary="Missing required explanation letter.",
            shipping_proof={"doc_id": "doc_ship_R8yL2"},
            customer_communication={"doc_id": "doc_comm_R8yL2"},
            explanation_letter=None,
        )

        # CASE 3: DO NOT SUBMIT — CONFLICT (Mumbai vs Hyderabad)
        disp_3 = Dispute(
            id="disp_P9zM4rSoB6xN3",
            payment_id="pay_P9zM4rSoB6xN3",
            amount=4000000,
            currency="INR",
            reason_code="13.1",
            respond_by=NOW + (1 * DAY),
            status="open",
            phase="chargeback",
        )
        ord_3 = OrderRecord(
            order_id="ord_P9zM4rSoB6xN3",
            payment_id="pay_P9zM4rSoB6xN3",
            customer_id="cust_P9zM4rSoB6xN3",
            user_id="usr_P9zM4rSoB6xN3",
            amount=4000000,
            currency="INR",
            order_date=NOW - (15 * DAY),
            shipping_address="100 Jubilee Hills, Hyderabad, TS 500033",
            ip_address="203.0.113.30",
            device_id="dev_P9zM4rSoB6xN3",
        )
        ship_3 = ShipmentRecord(
            shipment_id="ship_P9zM4rSoB6xN3",
            order_id="ord_P9zM4rSoB6xN3",
            tracking_number="EXP4411IN",
            carrier="FedEx",
            shipped_date=NOW - (13 * DAY),
            delivery_date=NOW - (9 * DAY),
            delivery_address="999 Marine Drive, Mumbai, MH 400002",
            carrier_status="delivered",
            proof_doc_id="doc_ship_P9zM3",
        )
        comm_3 = CustomerCommunicationLog(
            id="comm_P9zM4rSoB6xN3",
            order_id="ord_P9zM4rSoB6xN3",
            customer_id="cust_P9zM4rSoB6xN3",
            timestamp=NOW - (8 * DAY),
            channel="email",
            message_text="Where is my package? The tracking shows delivered to Mumbai but I live in Hyderabad.",
        )
        ev_3 = DisputeEvidence(
            dispute_id="disp_P9zM4rSoB6xN3",
            amount=4000000,
            summary="Hard address contradiction: order shipping address (Hyderabad) vs carrier delivery address (Mumbai).",
            shipping_proof={"doc_id": "doc_ship_P9zM3"},
            billing_proof={"doc_id": "doc_bill_P9zM3"},
            customer_communication={"doc_id": "doc_comm_P9zM3"},
        )

        # CASE 4: READY — Visa CE3.0 Qualified
        disp_4 = Dispute(
            id="disp_Q0aN5sTpC7yO4",
            payment_id="pay_Q0aN5sTpC7yO4",
            amount=1200000,
            currency="INR",
            reason_code="10.4",
            respond_by=NOW + (6 * DAY),
            status="open",
            phase="chargeback",
        )
        ord_4 = OrderRecord(
            order_id="ord_Q0aN5sTpC7yO4",
            payment_id="pay_Q0aN5sTpC7yO4",
            customer_id="cust_ce3_valid_04",
            user_id="usr_ce3_valid_04",
            amount=1200000,
            currency="INR",
            order_date=NOW - (7 * DAY),
            shipping_address="88 Connaught Place, New Delhi, DL 110001",
            ip_address="203.0.113.45",
            device_id="dev_mac_ce3_04",
        )
        ship_4 = ShipmentRecord(
            shipment_id="ship_Q0aN5sTpC7yO4",
            order_id="ord_Q0aN5sTpC7yO4",
            tracking_number="BLU7788IN",
            carrier="Bluedart",
            shipped_date=NOW - (5 * DAY),
            delivery_date=NOW - (3 * DAY),
            delivery_address="88 Connaught Place, New Delhi, DL 110001",
            carrier_status="delivered",
            proof_doc_id="doc_ship_Q0aN4",
        )
        ev_4 = DisputeEvidence(
            dispute_id="disp_Q0aN5sTpC7yO4",
            amount=1200000,
            summary="Visa CE3.0 Qualified dispute evidence.",
            shipping_proof={"doc_id": "doc_ship_Q0aN4"},
            billing_proof={"doc_id": "doc_bill_Q0aN4"},
        )
        ord_4_prior1 = OrderRecord(
            order_id="ord_Q0aN5sTpC7yO4_prior1",
            payment_id="pay_Q0aN5sTpC7yO4_prior1",
            customer_id="cust_ce3_valid_04",
            user_id="usr_ce3_valid_04",
            amount=950000,
            currency="INR",
            order_date=NOW - (180 * DAY),
            shipping_address="88 Connaught Place, New Delhi, DL 110001",
            ip_address="203.0.113.45",
            device_id="dev_mac_ce3_04",
        )
        ord_4_prior2 = OrderRecord(
            order_id="ord_Q0aN5sTpC7yO4_prior2",
            payment_id="pay_Q0aN5sTpC7yO4_prior2",
            customer_id="cust_ce3_valid_04",
            user_id="usr_ce3_valid_04",
            amount=1100000,
            currency="INR",
            order_date=NOW - (240 * DAY),
            shipping_address="88 Connaught Place, New Delhi, DL 110001",
            ip_address="203.0.113.45",
            device_id="dev_mac_ce3_04",
        )

        # CASE 5: NEEDS REVIEW — Visa CE3.0 Ineligible
        disp_5 = Dispute(
            id="disp_S1bO6tUqD8zP5",
            payment_id="pay_S1bO6tUqD8zP5",
            amount=1800000,
            currency="INR",
            reason_code="10.4",
            respond_by=NOW + (5 * DAY),
            status="open",
            phase="chargeback",
        )
        ord_5 = OrderRecord(
            order_id="ord_S1bO6tUqD8zP5",
            payment_id="pay_S1bO6tUqD8zP5",
            customer_id="cust_ce3_invalid_05",
            user_id="usr_ce3_invalid_05",
            amount=1800000,
            currency="INR",
            order_date=NOW - (8 * DAY),
            shipping_address="55 Anna Salai, Chennai, TN 600002",
            ip_address="203.0.113.55",
            device_id="dev_mac_ce3_05",
        )
        ship_5 = ShipmentRecord(
            shipment_id="ship_S1bO6tUqD8zP5",
            order_id="ord_S1bO6tUqD8zP5",
            tracking_number="IND9988TN",
            carrier="IndiaPost",
            shipped_date=NOW - (6 * DAY),
            delivery_date=NOW - (4 * DAY),
            delivery_address="55 Anna Salai, Chennai, TN 600002",
            carrier_status="delivered",
            proof_doc_id="doc_ship_S1bO5",
        )
        ev_5 = DisputeEvidence(
            dispute_id="disp_S1bO6tUqD8zP5",
            amount=1800000,
            summary="Ineligible for Visa CE3.0 liability shift (0 prior transactions found).",
            shipping_proof={"doc_id": "doc_ship_S1bO5"},
        )

        db.add_all([
            disp_1, ord_1, ship_1, comm_1, ev_1,
            disp_2, ord_2, ship_2, comm_2, ev_2,
            disp_3, ord_3, ship_3, comm_3, ev_3,
            disp_4, ord_4, ship_4, ev_4, ord_4_prior1, ord_4_prior2,
            disp_5, ord_5, ship_5, ev_5,
        ])
        db.commit()

        print("[+] Auto-seeded 5 demo dispute cases on cold-start boot.")

        # Run verification pipeline for each dispute to populate findings cache
        demo_ids = ["disp_N7xK2pQmZ4vL1", "disp_R8yL3qRnA5wM2", "disp_P9zM4rSoB6xN3", "disp_Q0aN5sTpC7yO4", "disp_S1bO6tUqD8zP5"]
        for did in demo_ids:
            run_verification(did, db=db)

    except Exception as e:
        db.rollback()
        print(f"[!] Error auto-seeding database: {e}")
