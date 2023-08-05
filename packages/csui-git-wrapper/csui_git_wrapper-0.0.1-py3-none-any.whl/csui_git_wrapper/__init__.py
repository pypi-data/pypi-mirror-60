'''csui_git_wrapper is Git submission wrapper for Fasilkom UI usage.'''

import json
import os
import subprocess
from enum import Enum
from collections.abc import MutableMapping


class Configuration(MutableMapping):
    '''JSON Configuration wrapper (reader and writer), dictionary-alike.'''
    def __init__(self, config_path: str = None):
        self.__config: dict = {}
        if config_path is not None:
            self.config_path: str = config_path
        else:
            self.config_path: str = os.path.expanduser(
                os.path.join("~", "csui-git-wrapper-config.json"))
        self.read()

    def exists(self):
        '''Checks whether the configuration file exists or not.'''
        return os.path.exists(self.config_path)

    def read(self):
        '''Read the configuration file.'''
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as _file:
                self.__config = json.loads(_file.read())

    def write(self):
        '''Write (or replace) the configuration file.'''
        if os.path.exists(self.config_path):
            confirm = input("Are you sure to replace config? (y/N) ")
            if confirm.strip().lower()[0] == "y":
                with open(self.config_path, "w") as _file:
                    self.__config = _file.write(json.dumps(self.__config))
        else:
            with open(self.config_path, "a") as _file:
                self.__config = _file.write(json.dumps(self.__config))

    def __getitem__(self, key: str):
        return self.__config[key]

    def __setitem__(self, key: str, value):
        Configuration.__validate_value(value)
        self.__config[key] = value

    def __delitem__(self, key):
        del self.__config[key]

    @staticmethod
    def __validate_value(value):
        type_compatible = False
        allowed_types = [str, float, dict, list]
        for _type in allowed_types:
            type_compatible |= isinstance(value, _type)
        if not type_compatible:
            raise ValueError(repr(_type) + " can't be converted to JSON.")
        if isinstance(value, dict):
            for child in value.values():
                Configuration.__validate_value(child)

    def __iter__(self):
        for key in self.__config.__iter__():
            yield "%s" % (key)

    def __len__(self):
        return len(self.__config)


class GitMergeStrategy(Enum):
    '''
    Enum for Git merge strategies. Three options available:
    DEFAULT = let Git automatically choose the strategy.
    OURS = if there's conflict, prefer our current changes.
    THEIRS = if there's conflict, prefer changes from the repository.
    '''
    DEFAULT = []
    OURS = ["-s", "ours", "-X", "ours"]
    THEIRS = ["-s", "theirs", "-X", "theirs"]


class GitAPI:
    '''Git wrapper. Basically runs Git via subprocess module.'''
    def __init__(self, config: Configuration):
        self.config = config

    def get_address(self):
        '''Get repository address.'''
        return "https://gitlab.cs.ui.ac.id/%s/%s-%s.git" % (
            self.config["student_user"], self.config["student_num"],
            self.config["course_name"])

    def __run_command(self, command: list, cwd: str = None):
        '''Runs command with defined working directory.'''
        if not cwd:
            cwd = self.config["work_path"]
        subprocess.call(command, cwd=cwd)

    def init(self):
        '''Initiate new Git local repository in current working directory.'''
        self.__run_command(["git", "init"])

    def add(self):
        '''Add all changed files to staging.'''
        self.__run_command(["git", "add", "."])

    def commit(self, message: str = "Latest work."):
        '''Commit staged changes to current branch.'''
        self.__run_command(["git", "commit", "-m", message])

    def checkout(self, branch: str = "master"):
        '''Checkout to another branch.'''
        self.__run_command(["git", "checkout", branch])

    def pull(self, strategy: GitMergeStrategy = GitMergeStrategy.OURS):
        '''Pull and merge latest changes to local.'''
        command = [
            "git", "pull",
            self.get_address(), "master", "--allow-unrelated-histories"
        ]
        command += strategy.value
        self.__run_command(command)

    def push(self):
        '''Push latest local changes to Git repository.'''
        self.__run_command(["git", "push", "-u", self.get_address(), "master"])

    def reset(self):
        '''Erase uncommited changes.'''
        self.__run_command(["git", "reset", "--hard", "HEAD"])
