import csv

WARD_DEPARTMENTS = [
    {"ward": "Ward 1", "department": "Roads"},
    {"ward": "Ward 2", "department": "Sanitation"},
    {"ward": "Ward 3", "department": "Water"},
    {"ward": "Ward 4", "department": "Public Safety"},
    {"ward": "Ward 5", "department": "Facilities"},
    {"ward": "Ward 6", "department": "Sanitation"},
    {"ward": "Ward 7", "department": "Water"},
]


def write_seed(path="data/sample_output/wards_departments.csv"):
    with open(path, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["ward", "department"])
        writer.writeheader()
        writer.writerows(WARD_DEPARTMENTS)


if __name__ == "__main__":
    write_seed()
    print("Wrote ward/department seed data to data/sample_output/wards_departments.csv")
