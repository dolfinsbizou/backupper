#!/usr/bin/env python3

import sys
import os
import getopt
import yaml
import tarfile
from datetime import datetime

configuration_file = "backupfile.yml"
backup_datetime = datetime.utcnow().strftime('%Y%m%d%H%M%S')

def getHelp(command_name):
    help_string = """Usage: {} [OPTIONS...]

  -h\t\t\tDisplays the current help and exits.
  -f, --config-file\tSpecifies an alternative YAML config file (default: {}).
""".format(command_name, configuration_file)

    return help_string

def validateConfiguration(configuration):
    if configuration is None:
        raise Exception("Empty configuration.")

    if not "artifacts" in configuration:
        raise Exception("Missing \"artifact\" node.")
    if not isinstance(configuration["artifacts"], list):
        raise Exception("Please provide a list of paths in the \"artifact\" node.")

    if not "delete_old_backups" in configuration:
        configuration["delete_old_backups"] = False
    elif configuration["delete_old_backups"] and not "backup_dir" in configuration:
        raise Exception("\"delete_old_backups\" is set to true, but there is no \"backup_dir\".")

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
        opts, args = getopt.getopt(argv[1:], "hf:", ["config-file="])
    except getopt.GetoptError as e:
        sys.stderr.write("Error: command line arguments: {}\n".format(e))
        sys.stderr.write("Try {} -h for help.\n".format(command_name))
        sys.exit(1)

    for opt, arg in opts:
        if opt == "-h":
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
    configuration["backup_dir"] = os.path.join(configuration["backup_dir"], "backup_{}".format(backup_datetime))

    # We create our backup dir
    try:
        os.makedirs(configuration["backup_dir"])
    except OSError as e:
        sys.stderr.write("Error: backup dir creation: {}\n".format(e))
        sys.exit(4)

    # We need to know the common path for artifacts to remove it from the backup output structure
    common_artifact_path = os.path.commonpath(configuration["artifacts"])

    # Backup each artifact
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
        output_tar = "{}.{}.tar.gz".format(os.path.join(configuration["backup_dir"], os.path.relpath(artifact, common_artifact_path)), backup_datetime)

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

    #TODO delete old backups

    if configuration["delete_old_backups"]:
        pass
    else:
        print("no")


if __name__ == "__main__":
    main(sys.argv)
