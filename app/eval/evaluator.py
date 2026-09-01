from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import EvaluationGroundTruth
from app.rules.pipeline import run_verification

CONTRADICTION_TYPES = [
    "address_mismatch",
    "date_impossibility",
    "amount_mismatch",
    "comms_contradiction",
]


def _map_finding_to_type(finding_name: str) -> str:
    if "address" in finding_name:
        return "address_mismatch"
    elif "date" in finding_name:
        return "date_impossibility"
    elif "amount" in finding_name:
        return "amount_mismatch"
    elif "comms" in finding_name:
        return "comms_contradiction"
    return "other"


def evaluate_held_out_dataset(db: Session = None) -> dict:
    close_session = False
    if db is None:
        from pathlib import Path
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        eval_db_file = Path(__file__).resolve().parent.parent.parent / "merchantguard.db"
        if eval_db_file.exists():
            eval_engine = create_engine(f"sqlite:///{eval_db_file.as_posix()}", connect_args={"check_same_thread": False})
            EvalSession = sessionmaker(autocommit=False, autoflush=False, bind=eval_engine)
            db = EvalSession()
            close_session = True
        else:
            db = SessionLocal()
            close_session = True

    try:
        test_records = db.query(EvaluationGroundTruth).filter(EvaluationGroundTruth.dataset_split == "held_out_test").all()
        total_test_cases = len(test_records)

        counts = {
            t: {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
            for t in CONTRADICTION_TYPES
        }

        clean_cases_count = 0
        clean_false_positives = 0

        for gt in test_records:
            is_clean = (
                gt.has_address_mismatch == 0 and
                gt.has_date_impossibility == 0 and
                gt.has_amount_mismatch == 0 and
                gt.has_comms_contradiction == 0
            )

            if is_clean:
                clean_cases_count += 1

            res = run_verification(gt.dispute_id, db=db)
            findings = res.get("findings", [])

            detected_types = set()
            for f in findings:
                if f.get("status") == "FOUND_CONFLICTING":
                    ctype = _map_finding_to_type(f.get("check_name", ""))
                    if ctype in counts:
                        detected_types.add(ctype)

            if is_clean and len(detected_types) > 0:
                clean_false_positives += 1

            gt_map = {
                "address_mismatch": gt.has_address_mismatch == 1,
                "date_impossibility": gt.has_date_impossibility == 1,
                "amount_mismatch": gt.has_amount_mismatch == 1,
                "comms_contradiction": gt.has_comms_contradiction == 1,
            }

            for ctype in CONTRADICTION_TYPES:
                actual_has = gt_map[ctype]
                pred_has = ctype in detected_types

                if actual_has and pred_has:
                    counts[ctype]["TP"] += 1
                elif not actual_has and pred_has:
                    counts[ctype]["FP"] += 1
                elif actual_has and not pred_has:
                    counts[ctype]["FN"] += 1
                else:
                    counts[ctype]["TN"] += 1

        results_per_type = {}
        total_TP = sum(counts[t]["TP"] for t in CONTRADICTION_TYPES)
        total_FP = sum(counts[t]["FP"] for t in CONTRADICTION_TYPES)
        total_FN = sum(counts[t]["FN"] for t in CONTRADICTION_TYPES)

        for ctype in CONTRADICTION_TYPES:
            tp = counts[ctype]["TP"]
            fp = counts[ctype]["FP"]
            fn = counts[ctype]["FN"]
            tn = counts[ctype]["TN"]

            prec = tp / (tp + fp) if (tp + fp) > 0 else 1.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 1.0
            f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            results_per_type[ctype] = {
                "TP": tp, "FP": fp, "FN": fn, "TN": tn,
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
            }

        agg_prec = total_TP / (total_TP + total_FP) if (total_TP + total_FP) > 0 else 1.0
        agg_rec = total_TP / (total_TP + total_FN) if (total_TP + total_FN) > 0 else 1.0
        agg_f1 = 2 * (agg_prec * agg_rec) / (agg_prec + agg_rec) if (agg_prec + agg_rec) > 0 else 0.0

        fp_rate = (clean_false_positives / clean_cases_count * 100) if clean_cases_count > 0 else 0.0
        fp_statement = (
            f"{clean_false_positives} clean cases were incorrectly flagged out of {clean_cases_count} clean test cases "
            f"({fp_rate:.2f}% false-positive rate), which would have caused a merchant to needlessly delay or block submission of a valid case."
        )

        report_data = {
            "total_test_cases": total_test_cases,
            "clean_cases_count": clean_cases_count,
            "clean_false_positives": clean_false_positives,
            "false_positive_cost_statement": fp_statement,
            "aggregate_metrics": {
                "total_TP": total_TP,
                "total_FP": total_FP,
                "total_FN": total_FN,
                "precision": round(agg_prec, 4),
                "recall": round(agg_rec, 4),
                "f1_score": round(agg_f1, 4),
            },
            "per_type_metrics": results_per_type,
        }

        try:
            import json
            from pathlib import Path
            json_path = Path(__file__).resolve().parent.parent.parent / "eval_report.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to persist eval_report.json: {e}")

        return report_data

    finally:
        if close_session:
            db.close()


def load_persisted_eval_report() -> dict:
    import json
    from pathlib import Path
    json_path = Path(__file__).resolve().parent.parent.parent / "eval_report.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return evaluate_held_out_dataset()
