from dataqualityprofiler.profiling import profile_csv
from dataqualityprofiler.reporting import export_json

report = profile_csv("sales.csv")
output = export_json(report, "sales-profile.json")

print(f"Report written to: {output}")