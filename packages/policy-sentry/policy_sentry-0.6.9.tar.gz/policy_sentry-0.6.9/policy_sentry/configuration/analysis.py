"""Report configuration for the analysis"""
import os
import shutil
from pathlib import Path
from policy_sentry.shared.constants import AUDIT_DIRECTORY_PATH


def create_default_report_config_file():
    """
    Copies over the default report config file to the config directory

    Essentially:
    cp $MODULE_DIR/policy_sentry/shared/data/audit/report-config.yml ~/policy_sentry/audit/report-config.yml
    """
    existing_report_config_file = 'report-config.yml'
    target_report_config_file_path = AUDIT_DIRECTORY_PATH + existing_report_config_file
    existing_report_config_file_path = os.path.join(
        str(Path(os.path.dirname(__file__)).parent) + '/shared/data/audit/' + existing_report_config_file)
    shutil.copy(existing_report_config_file_path,
                target_report_config_file_path)
    print(
        f"Copying overrides file {existing_report_config_file} to {target_report_config_file_path}")
