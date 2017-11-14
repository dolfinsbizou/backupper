#!/usr/bin/env python3

import sys
import os
import getopt
import yaml
import tarfile
from datetime import datetime

configuration_file = "backupfile.yml"

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

    if not "backup_dir" in configuration:
        # TODO use instead a new folder in the current working directory with a unique name (timestamp) to avoid collisions
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
        sys.stderr.write("Error: {}\n".format(e))
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
        sys.stderr.write("Error: {}\n".format(e))
        sys.exit(2)

    # Validate the configuration file
    try:
        validateConfiguration(configuration)
    except Exception as e:
        sys.stderr.write("Error: {}\n".format(e))
        sys.exit(3)

    # The configuration file directory sets the backup context, so if it's not in the current directory, let's change the working directory
    if os.path.dirname(configuration_file) != "":
        os.chdir(os.path.dirname(configuration_file))

    ## Actual backups ##

    try:
        os.makedirs(configuration["backup_dir"])
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            sys.stderr.write("Error: {}\n".format(e))
            sys.exit(4)
        else:
            sys.stderr.write("Info: {} already exists.\n".format(configuration["backup_dir"]))

    # We need to know the common path for artifacts to remove it from the backup output structure
    common_artifact_path = os.path.commonpath(configuration["artifacts"])

    # Backup each artifact
    for artifact in configuration["artifacts"]:
        if not os.path.exists(artifact):
            sys.stderr.write("Warning: {} doesn't exist (skipping).\n".format(artifact))
            continue

        #TODO skip files outside of working directory (as a Dockerfile can't copy file outside of its build context (ie directory of the Dockerfile))

        # If our artifact is a directory we must remove the trailing slash so that os.path.basename can properly work
        elif os.path.isdir(artifact):
            if artifact.endswith('/'):
                artifact = artifact[:-1]

        # Build the output tar path
        output_tar = "{}.{}.tar.gz".format(os.path.join(configuration["backup_dir"], os.path.relpath(artifact, common_artifact_path)), datetime.utcnow().strftime('%Y%m%d%H%M%S'))

        # Create subdirectories
        try:
            os.makedirs(os.path.dirname(output_tar))
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                sys.stderr.write("Error: {}\n".format(e))
                sys.exit(4)

        # Write the actual tar file
        with tarfile.open(output_tar, "w:gz") as tar:
            tar.add(artifact, arcname=os.path.basename(artifact))

        sys.stdout.write("{} done.\n".format(output_tar))

    #TODO delete old backups


if __name__ == "__main__":
    main(sys.argv)
