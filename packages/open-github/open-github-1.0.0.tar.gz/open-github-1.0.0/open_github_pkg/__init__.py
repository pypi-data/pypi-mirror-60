#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import webbrowser
import argparse

# Grab working directory from argument
parser = argparse.ArgumentParser(description="Working git directory")
parser.add_argument("directory", metavar="D", help="Directory", nargs='?', default=".")
args = parser.parse_args()
dir_path = os.getcwd()

# If no argument is passed then set working directory
working_directory = args.directory if len(args.directory) > 1 else dir_path

# Open github config from working directory
github_config = open(working_directory + "/.git/config", "r")
gc_lines = github_config.readlines()
url = ''

# Extract url from config file
for x in range(0, len(gc_lines)):
  if x == 8:
    url = gc_lines[x]

# Extract url from string
parsed_url = url.strip().split('@')[1].replace(":", "/").replace(".git", "")
final_url = "https://" + parsed_url

# Open url in a new page (“tab”) of the default browser, if possible
webbrowser.open_new_tab(final_url)