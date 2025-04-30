import os
import json
import pandas as pd
from pathlib import Path
import shutil

# === Configuration ===
project_root = Path("/path/to/project_root")
subjects = {
    "sub-01": {
        "age": 55,
        "sex": "M",
        "group": "ALS",
        "sessions": {
            "ses-01": {"acquisition_date": "2022-01-01", "visit_age": 55},
            "ses-02": {"acquisition_date": "2022-06-01", "visit_age": 55.5},
        },
    },
    "sub-02": {
        "age": 62,
        "sex": "F",
        "group": "control",
        "sessions": {
            "ses-01": {"acquisition_date": "2022-01-01", "visit_age": 62},
        },
    },
}
dataset_info = {
    "Name": "Longitudinal MRI Study of ALS",
    "BIDSVersion": "1.8.0",
    "DatasetType": "raw",
    "Authors": ["Pedram Parnianpour"],
    "Funding": ["#XXXX"],
    "ReferencesAndLinks": ["https://example-lab-url.ca"],
    "DatasetDOI": "10.18112/openneuro.dsXXXXXX.v1.0.0"
}

# === Step 1: Create directory structure ===
project_root.mkdir(parents=True, exist_ok=True)

# === Step 2: Dataset-level metadata ===
with open(project_root / "dataset_description.json", "w") as f:
    json.dump(dataset_info, f, indent=4)

participants_df = pd.DataFrame([
    {"participant_id": sid, "age": s["age"], "sex": s["sex"], "group": s["group"]}
    for sid, s in subjects.items()
])
participants_df.to_csv(project_root / "participants.tsv", sep="\t", index=False)

participants_json = {
    "age": {"Description": "Age at baseline", "Units": "years"},
    "sex": {"Description": "Biological sex", "Levels": {"M": "Male", "F": "Female"}},
    "group": {"Description": "Group assignment", "Levels": {"ALS": "ALS patient", "control": "Healthy control"}}
}
with open(project_root / "participants.json", "w") as f:
    json.dump(participants_json, f, indent=4)

# === Step 3: Sessions metadata ===
for sid, s in subjects.items():
    subj_path = project_root / sid
    subj_path.mkdir(parents=True, exist_ok=True)

    session_rows = []
    for ses, meta in s["sessions"].items():
        ses_path = subj_path / ses / "anat"
        ses_path.mkdir(parents=True, exist_ok=True)
        (subj_path / ses / "func").mkdir(parents=True, exist_ok=True)
        session_rows.append({"session_id": ses, **meta})

    sessions_df = pd.DataFrame(session_rows)
    sessions_df.to_csv(subj_path / "sessions.tsv", sep="\t", index=False)

    sessions_json = {
        "acquisition_date": {"Description": "Date of acquisition", "Format": "YYYY-MM-DD"},
        "visit_age": {"Description": "Participant age at visit", "Units": "years"}
    }
    with open(subj_path / "sessions.json", "w") as f:
        json.dump(sessions_json, f, indent=4)

# === Step 4: Sidecar JSONs ===
example_T1w_json = {
    "Manufacturer": "Siemens",
    "MagneticFieldStrength": 3,
    "EchoTime": 0.00298,
    "RepetitionTime": 2.3,
    "InversionTime": 0.9,
    "FlipAngle": 9,
    "SequenceName": "tfl3d1"
}
example_bold_json = {
    "TaskName": "rest",
    "RepetitionTime": 2.0,
    "EchoTime": 0.03,
    "FlipAngle": 90,
    "Manufacturer": "Siemens",
    "MagneticFieldStrength": 3,
    "Instructions": "Participants were instructed to rest quietly with eyes open, fixating on a cross."
}

# Fill in example files (optional — assumes actual NIfTI files exist or will be added manually)
for sid, s in subjects.items():
    for ses in s["sessions"]:
        anat_path = project_root / sid / ses / "anat"
        func_path = project_root / sid / ses / "func"

        # Create sidecar JSONs
        T1w_json_path = anat_path / f"{sid}_{ses}_T1w.json"
        bold_json_path = func_path / f"{sid}_{ses}_task-rest_bold.json"
        with open(T1w_json_path, "w") as f:
            json.dump(example_T1w_json, f, indent=4)
        with open(bold_json_path, "w") as f:
            json.dump(example_bold_json, f, indent=4)

# === Step 5: Organize NIfTI files (manual copy or automated if source known) ===
# Example: Copy files from a raw_data_dir to correct BIDS folders (optional)
# raw_data_dir = Path("/path/to/raw_nifti")
# for sid, s in subjects.items():
#     for ses in s["sessions"]:
#         shutil.copy(raw_data_dir / f"{sid}_{ses}_T1w.nii.gz", project_root / sid / ses / "anat")
#         shutil.copy(raw_data_dir / f"{sid}_{ses}_task-rest_bold.nii.gz", project_root / sid / ses / "func")

# === Step 6: Validate the dataset (if bids-validator is installed) ===
print("✅ BIDS structure created. To validate, run:")
print(f"\n  bids-validator {project_root}")

