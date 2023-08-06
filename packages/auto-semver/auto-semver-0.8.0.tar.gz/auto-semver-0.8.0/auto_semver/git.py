import subprocess
import sys

from auto_semver.semver import Semver


class GitTagger(object):
    def __init__(self, semver_tag):
        self.semver_tag = semver_tag

    def tag_local(self):
        tag_command = "git tag {}".format(self.semver_tag)

        command_output = subprocess.run(
            tag_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # Checking to make sure our command succeeded. The stdout() function
        # returns None if the command fails and there is no output.
        if "already exists" in command_output.stderr:
            sys.exit(
                "Git tag: {} already exists locally. Doing nothing...".format(
                    self.semver_tag
                )
            )

        elif command_output.stderr != "":
            sys.exit("Error creating git tags locally...")

        print("Created {} git tag locally".format(self.semver_tag))


class GitTagSource(object):
    # Class that grabs tags from a git remote
    def __init__(self, use_local, custom_remote=""):
        self.custom_remote = custom_remote
        self.use_local = use_local

    def _get_remote_tags(self):
        # Git command to list remote tags, only grabbing tags and not the
        # commit hashes.
        tag_command = "git ls-remote --tags --refs -q {} | awk '{{print $2}}'".format(
            self.custom_remote
        )

        command_output = subprocess.run(
            tag_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # Checking to make sure our command succeeded. The stdout() function
        # returns None if the command fails and there is no output.
        if command_output.stderr != "":
            sys.exit("Error getting tags from remote")
        elif command_output.stdout == "":
            # There are no returned tags, writing a message to stdout and exiting.
            print("No tags found. Nothing to do.")
            sys.exit(0)

        return command_output.stdout

    def _get_local_tags(self):
        # Git command to list remote tags, only grabbing tags and not the
        # commit hashes.
        tag_command = "git show-ref --tags -d | awk '{{print $2}}'"

        command_output = subprocess.run(
            tag_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # Checking to make sure our command succeeded. The stdout() function
        # returns None if the command fails and there is no output.
        if command_output.stderr != "":
            sys.exit("Error getting tags from remote")
        elif command_output.stdout == "":
            # There are no returned tags, writing a message to stdout and exiting.
            print("No tags found. Nothing to do.")
            sys.exit(0)

        return command_output.stdout

    def _parse_git_tag_output_string(self, raw_semver_text):
        semver_result_output = []

        for line in raw_semver_text.splitlines():
            # Removing the fixed part of the git tag output we won't need.
            line_cleaned = line.replace("refs/tags/", "")
            try:
                semver = Semver(line_cleaned)
            except ValueError:
                # It is just an invalid semver, and we will continue
                # along without using it.
                continue

            if semver is not None:
                semver_result_output.append(semver)

        return semver_result_output

    def get_semver_list(self):
        if self.use_local:
            raw_semver_tag_output = self._get_local_tags()
        else:
            raw_semver_tag_output = self._get_remote_tags()
        return self._parse_git_tag_output_string(raw_semver_tag_output)
