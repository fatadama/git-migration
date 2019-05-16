#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 14 09:50:40 2019

@author: tim
@brief: batch migrate git repositories to a different remote

- Supports SSH to SSH migration.
- Does not handle large files. If your new destination does not support large files, any repo with large files will fail to transfer.
- Original and new remotes are specified in settings.ini
- settings.ini has a list of repositories at each remote server to copy. The variable names are ignored, and each item is read.
- If the filepaths of the original and new repos will differ (likely), AND the destination path will be a constant format such as <username>/<repo>.git, then set copy_new_folder to True under [settings], and set new_folder_name = <username>
- The remote repos at the destination must already exist. I don't know how to get around this.

"""

import os
from configparser import ConfigParser

parser = ConfigParser()
parser.read('settings.ini')

# server identification for the original and new remotes
original = parser['settings']['original']
new = parser['settings']['new']

# boolean: if True, then all migrated repositories will be placed in NEW_FOLDER_NAME/*.git
#   Otherwise, the original filepaths are used
COPY_NEW_FOLDER = parser.getboolean('settings','copy_new_folder')
NEW_FOLDER_NAME = parser.get('settings','new_folder_name')

# working directory
pwd = os.getcwd()

def processRemote(line):
    # check if the line includes the remote name; if so, find the ':' and trim
    if not(line.find(original) == -1):
        idx = line.rfind(':')
        line = line[idx+1:]
    # append line
    source = original + ':' + line
    # parse line for the .git name
    ix = line.find('.git')
    if ix == -1:
        print("Warning: .git not in line: %s" % line)
        return
    else:
        tok = line[:ix]
        # parse tok for last backslash
        idx = tok.rfind('/')
        gitname = tok[idx+1:]
    # create the destination string
    dest = new + ':'
    if COPY_NEW_FOLDER:
        dest += NEW_FOLDER_NAME
        # check if backslash is needed
        if not (dest[-1] == '/') and not (dest[-1] == '\\'):
            dest += '/'
        dest += gitname + '.git'
    else:
        dest += line
    print("Source: %s" % (source))
    print("Dest  : %s" % (dest))
    
    # check if source repository already exists; if yes, then cd to it and pull
    gitdir = "./" + gitname
    if os.path.isdir(gitdir):
        # cd to the directory
        os.chdir(gitdir)
        # pull
        os.system("git pull")
    else:
        # clone source
        os.system("git clone %s" % source)
        # cd to the directory
        os.chdir(gitdir)
        # now pull all remote branches
        os.system("git branch -r | grep -v '\->' | while read remote; do git branch --track \"${remote#origin/}\" \"$remote\"; done")
        os.system("git fetch --all")
        os.system("git pull --all")
    # remove origin
    os.system("git remote rm origin")
    # set destination
    os.system("git remote add origin %s" % dest)
    # push to destination
    #os.system("git push -u origin master")
    os.system("git push --all origin")
    # now cd back to the PWD
    os.chdir(pwd)
    # remove directory
    os.system("rm -rf %s" % gitname)
    return

# read all repositories in the section 'repositories'
for (itemname,line) in parser.items('repositories'):
    if itemname == 'file':
        # read file
        fid = open(line)
        print("Read from file %s" % line)
        for line2 in fid:
            processRemote(line2)
        print("Closed file %s" % line)
        fid.close()
    else:
        processRemote(line)

