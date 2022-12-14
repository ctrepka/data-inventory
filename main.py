import csv
import os
from pathlib import Path

import arcpy


class DataInventory:
    def __init__(self):
        self.config_defaults = {
            "input_directory": str(os.path.join(Path.cwd(), "input/")),
            "output_directory": str(os.path.join(Path.cwd(), "output/")),
            "output_name": "data_inventory.csv",
            "regex": ".*\.gdb$|.*\.shp$"
        }
        self.input_method = None
        self.output_directory = self.config_defaults["output_directory"]
        self.input_directory = self.config_defaults["input_directory"]
        self.output_name = self.config_defaults["output_name"]
        self.regex = self.config_defaults["regex"]
        self.file_paths = []
        self.feature_class_data = []

    def configure_input_method(self):
        method = input(
            "Will you be providing a .csv of files to inventory, or would you like to search a directory for files? Enter one of options [csv|directory]\n")
        input_method = self.validate_input_method(method)
        return method

    def validate_input_method(self, method):
        if method == "csv" or method == "directory":
            return method
        else:
            print(
                "INPUT ERROR: Input '{}' does not match any of valid options [csv|directory]\n".format(method))
            self.configure_input_method()

    def runWizard(self):
        self.input_method = self.configure_input_method()
        input_dir_txt = 'Please enter the absolute path to the csv to create the inventory from\n' if self.input_method == 'csv' else 'Please enter the absolute path to the directory you would like to inventory\n'
        self.input_directory = input(input_dir_txt)
        self.output_directory = input(
            'Please enter the absolute path of the directory where you would like your inventory .csv file to be saved.\n')

        # reset defaults for values equal to ""
        if self.output_directory == "":
            self.output_directory = self.config_defaults[
                "output_directory"]
        if self.input_directory == "":
            self.input_directory = self.config_defaults[
                "input_directory"]
        if self.regex == "":
            self.regex = self.config_defaults["regex"]

        return self

    def getPathsFromCSV(self):
        file_paths = None

        with open(self.input_directory) as csvInput:
            reader = csv.reader(csvInput)
            readerList = list(reader)
            file_paths = [p[0] for p in readerList[1:]]

        self.file_paths = self.file_paths + file_paths
        print('@@@ CSV PATHS @@@')
        print(self.file_paths)

        return self

    def getPathsFromDirectory(self):
        print("@@@ GETTING PATHS FROM DIRECTORY {} @@@".format(self.input_directory))
        patterns = ("*.gdb", "*.shp")
        file_paths = [file for file in Path(self.input_directory).iterdir() if any(
            file.match(p) for p in patterns)]

        self.file_paths = [*self.file_paths, *file_paths]

        return self

    def getPaths(self):
        if(self.input_method == 'csv'):
            self.getPathsFromCSV()
        elif(self.input_method == 'directory'):
            self.getPathsFromDirectory()
        else:
            print("@@@ CANNOT GET PATHS OF FILES, NO METHOD SELECTED. @@@")
            self.configure_input_method()

        print('@@ DONE. {} PATHS FOUND.'.format(len(self.file_paths)))

        return self

    def getGdbFeatureClassMeta(self, fileGDBPath):
        print("@@@ GETTING .GDB INFO FROM .GDB FILE AT: {} @@@".format(fileGDBPath))

        if not os.path.isfile(fileGDBPath) and not os.path.isdir(fileGDBPath):
            arcpy.env.workspace = fileGDBPath
            props = {
                "path": fileGDBPath,
                "spatialReference": 'ERROR: PATH NOT FOUND',
                "shapeType": 'ERROR: PATH NOT FOUND',
            }
            nopaths = [props]
            print("@@ WARNING: FAILED TO FIND PATH {} @@".format(fileGDBPath))
            
            self.feature_class_data = self.feature_class_data + nopaths
            
            for fc in nopaths:
                print(fc)

            return self

        arcpy.env.workspace = fileGDBPath

        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [""] + datasets if datasets is not None else []

        fcs = []

        for ds in datasets:
            for featureClass in arcpy.ListFeatureClasses(feature_dataset=ds):
                fcPath = os.path.join(arcpy.env.workspace, ds, featureClass)
                props = {
                    "path": 'NONE',
                    "spatialReference": 'NONE',
                    "shapeType": 'NONE',
                }
                desc = arcpy.Describe(r'{}'.format(fcPath))
                props["path"] = fcPath
                if hasattr(desc, "spatialReference"):
                    props["spatialReference"] = desc.spatialReference.name
                if hasattr(desc, "shapeType"):
                    props["shapeType"] = desc.shapeType

                fcs.append(props)

        for fc in fcs:
            print(fc)

        self.feature_class_data = self.feature_class_data + fcs

        return self

    def getShpFeatureClassMeta(self, fileSHPPath):
        print("@@@ GETTING .SHP INFO FROM .SHP FILE AT: {} @@@".format(fileSHPPath))

        if not os.path.isfile(fileSHPPath) and not os.path.isdir(fileSHPPath):
            arcpy.env.workspace = fileSHPPath
            props = {
                "path": fileSHPPath,
                "spatialReference": 'ERROR: PATH NOT FOUND',
                "shapeType": 'ERROR: PATH NOT FOUND',
            }
            nopaths = [props]
            print("@@ WARNING: FAILED TO FIND PATH {} @@".format(fileSHPPath))
            
            self.feature_class_data = self.feature_class_data + nopaths
            
            for fc in nopaths:
                print(fc)

            return self

        fcs = []

        fcPath = fileSHPPath
        props = {
            "path": 'NONE',
            "spatialReference": 'NONE',
            "shapeType": 'NONE',
        }
        desc = arcpy.Describe(r'{}'.format(fcPath))
        props["path"] = fcPath
        if hasattr(desc, "spatialReference"):
            props["spatialReference"] = desc.spatialReference.name
        if hasattr(desc, 'shapeType'):
            props["shapeType"] = desc.shapeType

        fcs.append(props)

        for fc in fcs:
            print(fc)

        self.feature_class_data = self.feature_class_data + fcs

        return self

    def writeFeatureClassMeta(self, featureClass):
        print("@@@ WRITING FEATURE CLASS INFO FOR FEATURE CLASS NAMED {} FROM FILE: {} @@@".format(
            featureClass, featureClass.name))
        with open(self.output_directory + "/output/" + self.output_name):
            writer = csv.writer(self.output_directory +
                                "/output/" + self.output_name)

        print('@@ DONE @@')
        return self

    def getFeatureClassMeta(self):
        print('@@@ GETTING FEATURE CLASS METADATA FOR {} FILE PATHS'.format(len(self.file_paths)))
        for i in self.file_paths:
            if "gdb" in str(i):
                self.getGdbFeatureClassMeta(r'{}'.format(str(i)))
            elif "shp" in str(i):
                self.getShpFeatureClassMeta(r'{}'.format(str(i)))

        return self

    def outputCsv(self):
        props = {
            "path": None,
            "spatialReference": None,
            "shapeType": None,
        }
        headers = props.keys()

        if not os.path.exists(self.output_directory):
            print('{} did not exist. Creating directory...'.format(
                self.output_directory))
            os.makedirs(self.output_directory)

        with open(str(os.path.join(self.output_directory, self.output_name)), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.feature_class_data)

        print('\n\n@@@@ CSV OUTPUT COMPLETE. STORED IN {} @@@@'.format(r'{}'.format(self.output_directory)))


di = DataInventory()
di.runWizard().getPaths().getFeatureClassMeta().outputCsv()
