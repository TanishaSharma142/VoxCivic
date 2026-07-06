import csv
import random
import uuid
from datetime import datetime, timedelta

CATEGORIES = [
    "pothole",
    "garbage",
    "water leakage",
    "streetlight",
    "flooding",
    "public safety",
    "other",
]
WARDS = [
    "Ward 1",
    "Ward 2",
    "Ward 3",
    "Ward 4",
    "Ward 5",
    "Ward 6",
    "Ward 7",
]
DEPARTMENTS = [
    "Roads",
    "Sanitation",
    "Water",
    "Public Safety",
    "Facilities",
]

DESCRIPTION_TEMPLATES = {
    "pothole": [
        "Large pothole on the main road causing traffic slowdown.",
        "Pothole near the bus stop getting worse every day.",
    ],
    "garbage": [
        "Garbage heap overflowing in the lane.",
        "Dumped trash attracting animals near the park.",
    ],
    "water leakage": [
        "Water leak from the municipal pipe flooding the street.",
        "Sewage leak causing odor and health concerns.",
    ],
    "streetlight": [
        "Streetlight has been out for several nights.",
        "Flickering streetlamp creating a safety hazard.",
    ],
    "flooding": [
        "Low-lying road is flooded after the last rains.",
        "Drainage is blocked and water is pooling on the street.",
    ],
    "public safety": [
        "Broken railing near school crossing.",
        "Speeding vehicle risk on narrow street.",
    ],
    "other": [
        "General concern about municipal cleanliness.",
        "Request for better signage in the area.",
    ],
}


def generate_complaint(index: int):
    category = random.choices(
        CATEGORIES,
        weights=[15, 20, 15, 10, 10, 15, 15],
        k=1,
    )[0]
    ward = random.choices(WARDS, weights=[12, 12, 10, 10, 14, 16, 26], k=1)[0]
    severity = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 30, 25, 15], k=1)[0]
    description = random.choice(DESCRIPTION_TEMPLATES[category])
    submitted_at = datetime.utcnow() - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
    return {
        "complaint_id": str(uuid.uuid4()),
        "citizen_id": str(uuid.uuid4()) if random.random() > 0.2 else None,
        "category": category,
        "severity": severity,
        "description": description,
        "image_url": None,
        "embedding": None,
        "ward": ward,
        "latitude": round(12.90 + random.random() * 0.12, 6),
        "longitude": round(77.58 + random.random() * 0.12, 6),
        "submitted_at": submitted_at.isoformat() + "Z",
        "status": random.choice(["new", "triaged", "in_progress"]),
    }


def write_csv(rows, path="data/sample_output/complaints_synthetic.csv"):
    with open(path, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    rows = [generate_complaint(i) for i in range(5000)]
    write_csv(rows)
    print(f"Generated {len(rows)} synthetic complaints to data/sample_output/complaints_synthetic.csv")
