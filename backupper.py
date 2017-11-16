#!/usr/bin/env python3

import sys
import os
import shutil
import getopt
import re
import yaml
import tarfile
import datetime

configuration_file = "backupfile.yml"
backup_datetime = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

def getHelp(command_name):
    help_string = """Usage: {} [OPTIONS...]

  -h, --help\t\tDisplays the current help and exits.
  -f, --config-file\tSpecifies an alternative YAML config file (default: {}).
""".format(command_name, configuration_file)

    return help_string

def validateConfiguration(configuration):
    # No empty configuration file
    if not isinstance(configuration, dict):
        raise Exception("Empty or malformed configuration.")

    # artifacts
    if not "artifacts" in configuration:
        raise Exception("Missing \"artifacts\" node.")
    elif not isinstance(configuration["artifacts"], list):
        raise Exception("Please provide a list of paths in the \"artifacts\" node.")
    else:
        for element in configuration["artifacts"]:
            if not isinstance(element, str):
                raise Exception("In \"artifacts\": {} isn't a string.".format(element))

    # delete_old_backups
    if not "delete_old_backups" in configuration:
        configuration["delete_old_backups"] = False
    elif configuration["delete_old_backups"] and not "backup_dir" in configuration:
        raise Exception("\"delete_old_backups\" is set to true, but there is no \"backup_dir\".")
    elif not isinstance(configuration["delete_old_backups"], bool):
        raise Exception("\"delete_old_backups\" should be a boolean.")

    # cleaning_policy
    valid_cleaning_policies = ["most_recents", "first_daily", "first_weekly", "first_monthly"]
    if not "cleaning_policy" in configuration or configuration["cleaning_policy"] is None:
        configuration["cleaning_policy"] = {}
    elif not isinstance(configuration["cleaning_policy"], dict):
        raise Exception("\"cleaning_policy\" should be a list of nodes.")
    else:
        for key in configuration["cleaning_policy"]:
            if not key in valid_cleaning_policies:
                raise Exception("\"{}\" is an incorrect \"cleaning_policy\" option.".format(key))
            elif not (isinstance(configuration["cleaning_policy"][key], int) and configuration["cleaning_policy"][key] >= 0) :
                raise Exception("\"{}\" should be a positive integer.".format(key))
    for policy in valid_cleaning_policies:
        if not policy in configuration["cleaning_policy"]:
            configuration["cleaning_policy"][policy] = 0

    # backup_dir
    if not "backup_dir" in configuration:
        configuration["backup_dir"] = os.getcwd()
    if not isinstance(configuration["backup_dir"], str):
        raise Exception("\"backup_dir\" should be a string.")

def main(argv):

    # Configuration variables
    global configuration_file
    configuration = None
    command_name = os.path.basename(argv[0])

    ## Initialisation ##

    # Fetch command line arguments
    try:
        opts, args = getopt.getopt(argv[1:], "hf:", ["config-file=", "help"])
    except getopt.GetoptError as e:
        sys.stderr.write("Error: command line arguments: {}\n".format(e))
        sys.stderr.write("Try {} -h for help.\n".format(command_name))
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            sys.stdout.write(getHelp(command_name))
            sys.exit(0)
        if opt in ("-f", "--config-file"):
            configuration_file = str(arg)

    # Parse the configuration file
    print("Loading {}.".format(configuration_file))
    try:
        with open(configuration_file, "r") as f:
            configuration = yaml.load(f)
    except Exception as e:
        sys.stderr.write("Error: yaml parsing: {}\n".format(e))
        sys.exit(2)

    # Validate the configuration file
    try:
        validateConfiguration(configuration)
    except Exception as e:
        sys.stderr.write("Error: configuration validation: {}\n".format(e))
        sys.exit(3)

    # The configuration file directory sets the backup context, so if it's not in the current directory, let's change the working directory
    if os.path.dirname(configuration_file) != "":
        os.chdir(os.path.dirname(configuration_file))

    ## Actual backups ##

    # Our actual backup will take place in a timestampped subdir
    actual_backup_dir = os.path.join(configuration["backup_dir"], "backup_{}".format(backup_datetime))

    # We create our backup dir
    try:
        os.makedirs(actual_backup_dir)
    except OSError as e:
        sys.stderr.write("Error: backup dir creation: {}\n".format(e))
        sys.exit(4)

    # We need to know the common path for artifacts to remove it from the backup output structure
    common_artifact_path = os.path.commonpath(configuration["artifacts"])

    # Backup each artifact
    print("Backupping artifacts.")
    for artifact in configuration["artifacts"]:
        if not os.path.exists(artifact):
            sys.stderr.write("Warning: backup: {} doesn't exist (skipping).\n".format(artifact))
            continue

        # Not sure if we should allow to backup files from outside the backup context or not.

        # If our artifact is a directory we must remove the trailing slash so that os.path.basename can properly work
        elif os.path.isdir(artifact):
            if artifact.endswith('/'):
                artifact = artifact[:-1]

        # Build the output tar path
        output_tar = "{}.{}.tar.gz".format(os.path.join(actual_backup_dir, os.path.relpath(artifact, common_artifact_path)), backup_datetime)

        # Create subdirectories
        try:
            os.makedirs(os.path.dirname(output_tar))
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                sys.stderr.write("Error: backup: {}\n".format(e))
                sys.exit(4)

        # Write the actual tar file
        with tarfile.open(output_tar, "w:gz") as tar:
            tar.add(artifact, arcname=os.path.basename(artifact))

        sys.stdout.write("{} done.\n".format(output_tar))

    ## Old backups cleaning ##

    if configuration["delete_old_backups"]:
        print("Cleaning old backups. Strategy: all.")

        # Backup pattern: a backup created by this script should look like this
        backup_pattern = re.compile(r'backup_(?P<datetime_str>[0-9]{14})$')

        # We discard regular files and directories that don't match the expected backup pattern
        directories = [os.path.join(configuration["backup_dir"], f) for f in os.listdir(configuration["backup_dir"]) if os.path.isdir(os.path.join(configuration["backup_dir"], f))]
        backups_list = list(filter(backup_pattern.search, directories))

        # We always keep the current backup so we remove it from this list
        backups_list.remove(actual_backup_dir)

        # We can terminate the program if we have no old backup
        if len(backups_list) == 0:
            sys.exit(0)

        backups_to_keep = []

        # Skip some calculation if all cleaning policies are equal to 0
        if not (all(configuration["cleaning_policy"][key] == 0 for key in configuration["cleaning_policy"])):
            # We associate to each backup its corresponding datetime
            backups_datetime = [datetime.datetime.strptime(backup_pattern.search(elem).group("datetime_str"), '%Y%m%d%H%M%S') for elem in backups_list]

            # We sort files_datetime and selected_files accordingly
            backups_datetime, backups_list = (list(t) for t in zip(*sorted(zip(backups_datetime, backups_list))))

            # We also need the date of our current backup
            curr_backup_date = datetime.datetime.strptime(backup_pattern.search(actual_backup_dir).group("datetime_str"), '%Y%m%d%H%M%S').date()

            # Most recent backups
            most_recent_backups = backups_list[-configuration["cleaning_policy"]["most_recents"]:]
            backups_to_keep.extend(most_recent_backups)

            # First daily files
            backups_of_the_day = [backups_list[i] for i in range(0, len(backups_list)) if backups_datetime[i].date() == curr_backup_date][0:configuration["cleaning_policy"]["first_daily"]]
            backups_to_keep.extend(backups_of_the_day)

        for backup in backups_list:
            if backup not in backups_to_keep:
                shutil.rmtree(backup)
                sys.stdout.write("{} deleted.\n".format(backup))

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
