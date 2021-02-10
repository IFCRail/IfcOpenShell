import os
import sys
import shutil
import bimtester.reports
import bimtester.run

from behave.__main__ import main as behave_main

from PySide2 import QtCore
from PySide2.QtCore import QUrl

# FIXME: could be improved
def get_resource_path(relative_path):
    # for pyinstaller
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", relative_path)


class BIMTesterWrapper:
    file = None
    bookmarks = {}

    def run_bimtester(
        self, path, ifc_file, schema_file, feature_file, report_output_path, continue_after_failed_step=False
    ):
        print("BIMTester: Starting...")
        args = {
            "path": path,
            "ifc": ifc_file,
            "schema_file": schema_file,
            "feature": feature_file,
            "steps": "",
            "lang": "",
            "console": "",
            "advanced_arguments": "-D runner.continue_after_failed_step=" + str(continue_after_failed_step),
        }

        # run behave
        in_schema_file = None
        if schema_file and os.path.isfile(schema_file):
            in_schema_file = schema_file
        report_json = bimtester.run.TestRunner(args["ifc"], in_schema_file).run(args)

        report_file_name = "{}.{}".format(os.path.basename(ifc_file), os.path.basename(feature_file))
        report_full_path = os.path.join(report_output_path, report_file_name + ".html")

        # copy report file to output
        shutil.copy(report_json, os.path.join(report_output_path, report_file_name + ".json"))

        # create html report
        print("BIMTester: Generating reports...")
        bimtester.reports.ReportGenerator().generate(report_json, report_full_path)

        # get the report files
        report_files = []
        if os.path.exists(report_output_path):
            for report_file in os.listdir(report_output_path):
                if report_file == report_file_name + ".html":
                    report_files.append(
                        QUrl.fromLocalFile(os.path.abspath(os.path.join(report_output_path, report_file)))
                    )
        print("BIMTester: Done.")
        return report_files