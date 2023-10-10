import os
import pandas as pd
import dask.dataframe as dd
from hydra import compose, initialize
from omegaconf import OmegaConf
from argparse import ArgumentParser

class baseSearch:
    def __init__(self, patientData_path:str,
                 codelist_path:str):
        self.patientData_path = patientData_path
        self.codelist_path = codelist_path

    def read_data(self):
        self.patientData = pd.read_excel(self.patientData_path,
                                         sheet_name="Patient",
                                         dtype={"patid":str, "gender":str},
                                         parse_dates=["yob"])

        self.observations = pd.read_excel(self.patientData_path,
                                          sheet_name="Observation",
                                          dtype={"patid": str, "medcodeid": str, "value": str},
                                          parse_dates=["obsdate"])

        self.medDict = pd.read_excel(self.patientData_path,
                                     sheet_name="Medical dictionary",
                                     dtype={"medcodeid": str, "term": str, "snomedctconceptid": str, "snomedctdescriptionid": str})

        # Create dictionary mapping SNOMED to CPRD Medcode and vice-versa
        self.snomed2medcode = dict(self.medDict.snomedctconceptid, self.medDict.medcodeid)
        self.medcode2snomed = dict(self.medDict.medcodeid, self.medDict.snomedctconceptid)

        self.codelist = pd.read_csv(self.codelist_path,
                                         encoding="utf-8",
                                         engine="python",
                                         dtype={"SnomedCTConceptId": str, "Term": str, "Disease": str, "Otherinstructions": str, "origin":str})

    
    # snomed_finder: Function to find SNOMED codes associated with a given disease
    # Input:
    # disease_name: Name of the disease to return codes for
    #
    # Output:
    # disease_codes: List of SNOMED codes for the given disease
    def snomed_finder(self, disease_name):
        disease = list(self.codelist[self.codelist['Disease'] == disease_name].SnomedCTConceptId)
        return diseases
    
    # base_snomed_finder: Function to find presence of SNOMED codes within dataframe of patient medcodes
    # Input:
    # patient_df: Dataframe of patient record taken from CPRD primary care
    # disease_codes: List of SNOMED codes indicating presence of a disease (use snomed_finder helper function)
    #
    # Output:
    # disease_active: True if SNOMED codes present, otherwise False
    def base_snomed_finder(self, patient_df, disease_codes):
        patient_snomed_codes = list(map(self.medcode2snomed, patient_df.medcode))
        disease_active = any(patient_snomed_codes in disease_codes)
        return disease_active

    #########################################################################
    # Disease functions
    #########################################################################

    # alcohol_problems
    # Complex logic for numerical values
    # Input:
    # patientdf: Dataframe of patient medcode ids
    # Output:
    # disease_active: True if disease is present, otherwise False
    def alcohol_problems(self, patientdf):
        snomed_codes = self.snomed_finder('Alcohol Problem')
        # This includes 4 codes that need extra logic, remove these for now
        snomed_codes.remove('10800000000000000') # Units per week
        snomed_codes.remove('228958009') # Units per week
        snomed_codes.remove('10800000000000000') # Units per day
        snomed_codes.remove('228957004') # Units per day

        # snomed_codes is now an "easy" search
        disease_active = self.base_snomed_finder(patient_df, snomed_codes)

        # If alcohol now active can skip the numerical checks
        if disease_active:
            return True
        # Otherwise check the numerical values
        # Units per day
        # Convert to medcode and check if weekly units > 20
        day_codes = map(self.snomed2medcode, ['10800000000000000', '228957004'])
        if (patient_df[patient_df.medcodeid.isin(day_codes)].numeric * 7 > 20):
            return True
        # Units per week
        # Convert to medcode and check if weekly units > 20
        week_codes = map(self.snomed2medcode, ['10800000000000000', '228958009'])
        if (patient_df[patient_df.medcodeid.isin(week_codes)].numeric > 20):
            return True
        # If still here then no alcohol problems and can return False
        return False

        # alcohol_related_brain_injury
        # Simple check
        # Input:
        # patientdf: Dataframe of patient medcode ids
        # Output:
        # disease_active: True if disease is present, otherwise False
        def alcohol_related_brain_injury(self, patientdf):
            snomed_codes = self.snomed_finder('Alcohol-related Brain Injury')
            disease_active = self.base_snomed_finder(patient_df, snomed_codes)
            return disease_active

        # alcoholic_liver_disease
        # Simple check
        # Input:
        # patientdf: Dataframe of patient medcode ids
        # Output:
        # disease_active: True if disease is present, otherwise False
        def alcoholic_liver_disease(self, patientdf):
            snomed_codes = self.snomed_finder('Alcoholic Liver Disease')
            disease_active = self.base_snomed_finder(patient_df, snomed_codes)
            return disease_active

def main(args):
    with initialize(version_base=None, config_path=args.configs):
        cfg = compose(config_name="searchargs")
        print("Current working directory: ", os.getcwd())
        print(OmegaConf.to_yaml(cfg),"\n")

    # SR Comment:
    # Something like this I'm thinking?
    # To calculate diseases for a single patient
    # 
    # disease_functions = [self.alcohol_problemns, self.alcoholic_liver_disease, .......]
    # disease_active = list()
    # for f in disease_functions:
    #     disease_active.append(f(patient_df))
    #
    

    bs = baseSearch(cfg.data.patient_data_path, cfg.Codelists.dynairx_codelist_path)
    bs.read_data()
    patient_snomed_codes = bs.base_snomed_finder(bs.observations, bs.medDict, args.patient_id)
    patient_diseases = bs.snomed_finder(patient_snomed_codes, bs.codelist)
    print("Patient {} has these diseases below".format(args.patient_id))
    for i,dis in enumerate(patient_diseases):
        print("\t", i+1,  dis)

if __name__ == "__main__":
    par = ArgumentParser()
    par.add_argument("--configs", default="configs", help="file with search arguments")
    par.add_argument("--patient_id", default='None', help="specify patient whose disease list you would like to fetch")
    args = par.parse_args()
    main(args)
