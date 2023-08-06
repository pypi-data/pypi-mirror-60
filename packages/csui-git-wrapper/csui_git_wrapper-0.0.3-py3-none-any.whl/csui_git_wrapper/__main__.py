#!/bin/bash
'''csui_git_wrapper is Git submission wrapper for Fasilkom UI usage.'''

import argparse
import os
from string import punctuation
from csui_git_wrapper import Configuration, GitAPI, GitMergeStrategy


def __read_config():
    '''Reads configuration or creates new configuration if not exist.'''
    config = Configuration()
    if not config.exists():
        configure()
        config = Configuration()
    return config


def pull():
    '''Submits current changes to Git repository.'''
    config = __read_config()
    api = GitAPI(config)
    api.init()
    api.config_repo()
    api.pull(strategy=GitMergeStrategy.THEIRS)


def submit():
    '''Submits current changes to Git repository.'''
    config = __read_config()
    api = GitAPI(config)
    api.init()
    api.config_repo()
    api.add()
    message = input("Enter commit message (usually defined by the problem): ")
    message = message.strip()
    api.commit(message)
    api.pull()
    api.push()


def configure():
    '''Rewrites JSON configuration based on user input.'''
    config = Configuration()
    config["student_name"] = input("Input your full name: ").strip()
    config["student_num"] = input("Input your student number (NPM): ").strip()
    student_user = input("Input your UI or GitLab CSUI account user name: ")
    config["student_user"] = student_user.strip().replace("@ui.ac.id", "")
    course_name = input("Imput your course short name " +
                        "(no whitespace allowed, e.g. DDP1): ")
    course_name = course_name.strip()
    for char in punctuation + " \t\r\n":
        course_name = course_name.replace(char, "")
    config["course_name"] = course_name
    work_path = input("What is your folder address? ").strip()
    while not os.path.exists(work_path):
        print("The folder you tell me doesn't exist.")
        work_path = input("What is your folder address? ").strip()
    config["work_path"] = work_path
    config.write()


def main():
    '''Main function.'''
    parser = argparse.ArgumentParser(prog="csuisubmit")
    parser.add_argument("command",
                        default="submit",
                        choices=["submit", "pull", "configure"],
                        help='"submit" to submit your work, ' +
                        '"pull" to get your previous work, ' +
                        '"configure" to configure your identity. ' +
                        'Default is "submit"')
    args = parser.parse_args()
    if args.command.lower() == "configure":
        configure()
    elif args.command.lower() == "pull":
        pull()
    else:
        submit()


if __name__ == "__main__":
    main()
