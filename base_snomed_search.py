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

        self.codelist = pd.read_csv(self.codelist_path,
                                         encoding="utf-8",
                                         engine="python",
                                         dtype={"SnomedCTConceptId": str, "Term": str, "Disease": str, "Otherinstructions": str, "origin":str})

    def base_snomed_finder(self, patient_obs, med_dict, patient_id:str=None):
        patientframe = patient_obs.loc[patient_obs['patid'] == patient_id]
        medcodeid = patientframe.medcodeid.tolist()
        snomedcui = med_dict[med_dict['medcodeid'].isin(medcodeid)]['snomedctconceptid'].tolist()
        return snomedcui

    def disease_finder(self, snomedcui:list, codelist):
        diseases = codelist[codelist['SnomedCTConceptId'].isin(snomedcui)].Disease.tolist()
        return diseases

def main(args):
    with initialize(version_base=None, config_path=args.configs):
        cfg = compose(config_name="searchargs")
        print("Current working directory: ", os.getcwd())
        print(OmegaConf.to_yaml(cfg),"\n")


    bs = baseSearch(cfg.data.patient_data_path, cfg.Codelists.dynairx_codelist_path)
    bs.read_data()
    patient_snomed_codes = bs.base_snomed_finder(bs.observations, bs.medDict, args.patient_id)
    patient_diseases = bs.disease_finder(patient_snomed_codes, bs.codelist)
    print("Patient {} has these diseases below".format(args.patient_id))
    for i,dis in enumerate(patient_diseases):
        print("\t", i+1,  dis)

if __name__ == "__main__":
    par = ArgumentParser()
    par.add_argument("--configs", default="configs", help="file with search arguments")
    par.add_argument("--patient_id", default='None', help="specify patient whose disease list you would like to fetch")
    args = par.parse_args()
    main(args)