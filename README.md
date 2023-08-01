# dynairxSnomedFinder
Custom function to search for diseases of patients given their structured patient records such as CPRD 

### Required
- Python 3.7+
- hydra-core (tested with version 1.3.2)
- pandas
- Omegaconf (tested with version 2.3.0)

## Tasks
Problem addressed: Given a patient record with contents in a strctured format (e.g. coded CPRD data), determine whether certain conditions (mapped to snomed codes) in a predefined codelist (dynairx) exist or not. If conditions do indeed exist, retrieve a list of conditions for a patient.

## Run
> python base_snomed_search.py --patient_id 827631782
