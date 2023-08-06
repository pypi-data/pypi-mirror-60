# csui-git-wrapper

Wraps Git commands for submission. Similiar to `submit50` (https://github.com/cs50/submit50.git), but this is much simpler and cross-platform.
Intended for specific Fasilkom UI usage.
This package is intended to use with Python 3.6 or newer.

## Installation
To install this package, run:
```bash
python -m pip install csui-git-wrapper
```

## Usage
To submit your work:
```bash
csuisubmit submit
```
When you are submitting for the first time, you will be asked for your full name, your student number (NPM), your UI or GitLab CSUI account, your course's short name (without any spaces or punctuations), and your working directory (where you put your tutorials/assignments).
After that, in every submission, you will be required to put a message. The message usually defined by your lecturer on the assignment problem set.

To get your latest work from other computer:
```bash
csuisubmit pull
```

## Need to reconfigure?
You can reconfigure your `csuisubmit` by using this command:
```bash
csuisubmit configure
```
Then, you will be asked for things just like the first time you are using `csui-git-wrapper`.

## Changelog
1. 0.0.1: Initial version.
2. 0.0.2: Add option to pull latest work available from remote repository.
3. 0.0.3: Add Git configuration step to accomodate users with Git installed for the first time.
