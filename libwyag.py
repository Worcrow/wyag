#!/user/bin/env python3

import argparse
import collections
import configparser
from datetime import datetime
import grp
import pwd
from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import sys
import zlib
from pprint import pprint

# parser = argparse.ArgumentParser(description="this description")
# parser.add_argument("-v", "--verbose", help="increase verbosity", action="store_true")
# args = parser.parse_args()
# print(pprint(args))

def repo_path(repo, *path):
	"""join path with the gitdir path"""
	return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
	"""get the path to the file, if it is valid"""
	if repo_dir(repo, *path[:-1], mkdir=mkdir):
		return repo_path(repo, *path)

def repo_dir(repo, *path, mkdir=False):
	""" check if the path is valid or created by setting true to mkdir"""
	path = repo_path(repo, *path)

	if os.path.exists(path):
		if os.path.isdir(path):
			return path
		else:
			raise Exception(f"not a directory {path}")
	if mkdir:
		os.makedirs(path)
		return path
	else:
		return None

class GitRepository(object):
	""" initialize a git repository """

	workTree = None
	gitdir = None
	config = None
	def __init__(self, path, force=False):
		self.workTree = path
		self.gitdir = os.path.join(path, ".git")

		if not (force or os.path.isdir(self.gitdir)):
			raise Exception("Not a git repository")

		self.config = configparser.ConfigParser()
		conf = repo_file(self, "config")
		if conf and os.path.exists(conf):
			self.config.read(conf)
		elif not force:
			raise Exception("configuration file missing")

		if not force:
			version = int(self.config["core"]["repositoryformatversion"])
			if version != 0:
				raise Exception(f"Unsoported repository version {version}")


def repo_default_config():
	ret = configparser.ConfigParser()

	ret["core"] = {
			"repositoryformatversion": "0",
			"filemode": "false",
			"bare": "false"
	}
	return ret

def repo_create(path):
	""" Create a new repository at path."""

	repo = GitRepository(path, True)

	if os.path.exists((repo.workTree)):
		if not os.path.isdir(repo.workTree):
			raise Exception(f"{repo.workTree} is not a directory")
		if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
			raise Exception(f"{repo.gitdir} is not empty")
	else:
		os.mkdirs(repo.workTree)

	assert repo_dir(repo, "branches", mkdir=True)
	assert repo_dir(repo, "refs", mkdir=True)
	assert repo_dir(repo, "objects", mkdir=True)
	assert repo_dir(repo, "refs", "tags", mkdir=True)
	assert repo_dir(repo, "refs", "heads", mkdir=True)

	with open(repo_file(repo, "description"), "w") as des:
		des.write("Unnamed repository; edit this file 'description' to name the repository.")

	with open(repo_file(repo, "HEAD"), "w") as head:
		head.write("ref: refs/heads/main")

	with open(repo_file(repo, "config"), "w") as conf:
		config = repo_default_config()
		config.write(conf)

	return repo
def cmd_init(args):
	repo_create(args.path)

def main(argv=sys.argv[1:]):
	argparser = argparse.ArgumentParser(description="Content Tracker")
	argsubparser = argparser.add_subparsers(title="Command", dest="command")
	argsubparser.required = True
	argps = argsubparser.add_parser("init", help="Initialize a new, empty directory")
	argps.add_argument("path",
					   metavar="Directory",
					   nargs="?",
					   default=".",
					   help="Where to create the repository."
					   )
	args = argparser.parse_args(argv)

	match args.command:
		case "add"          : cmd_add(argps)
		case "cat-file"     : cmd_cat_file(argps)
		case "check-ignore" : cmd_check_ignore(argps)
		case "checkout"     : cmd_checkout(argps)
		case "commit"       : cmd_commit(argps)
		case "hash-object"  : cmd_hash_object(argps)
		case "init"         : cmd_init(args)
		case "log"          : cmd_log(argps)
		case "ls-files"     : cmd_ls_files(argps)
		case "ls-tree"      : cmd_ls_tree(argps)
		case "rev-parse"    : cmd_rev_parse(argps)
		case "rm"           : cmd_rm(argps)
		case "show-ref"     : cmd_show_ref(argps)
		case "status"       : cmd_status(argps)
		case "tag"          : cmd_tag(argps)
		case _              : print("Invalid Command.")


