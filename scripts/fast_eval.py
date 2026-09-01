import sys
import os
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ['DATABASE_URL'] = 'sqlite:///D:/Razorpay/merchantguard.db'
os.environ['DISABLE_LLM'] = 'true'

from app.eval.evaluator import evaluate_held_out_dataset

start = time.time()
print("Starting fast evaluation over 1,868 held-out test cases...")
report = evaluate_held_out_dataset()
elapsed = time.time() - start

print(f"\nCompleted evaluation in {elapsed:.2f} seconds.")
print("=== RAW HELD-OUT EVALUATION REPORT ===")
print(json.dumps(report, indent=2))
