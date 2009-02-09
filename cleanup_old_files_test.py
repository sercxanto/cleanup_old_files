#!/usr/bin/python
#
#    cleanup_old_files_test.py
#
#    Test script for cleanup_old_files.py
# 
#    Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import optparse
import os
import random
import tempfile
import time


def recursiveDelete(dirname):
    '''Deletes recursively dirname and all sub directories and all files.'''
    for root, dirs, files in os.walk(dirname, topdown=False):
	for name in files:
	    os.remove(os.path.join(root, name))
	for name in dirs:
	    os.rmdir(os.path.join(root, name))
    os.rmdir(root)


def main():
    MAX_NR_OF_FILES = 5000
    NR_OF_FILES_IN_DIR = 100 # must be smaller than MAX_NR_OF_FILES

    parser = optparse.OptionParser(
	    usage="%prog [options]",
	    version="%prog " + os.linesep +
	    "Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de>")
    parser.add_option("-k","--keep",
	    dest="keep", default=False, action="store_true",
	    help="Does not delete temporary directories/files")
    
    (options, args) = parser.parse_args()

    tmpdir = tempfile.mkdtemp("","cleanup_old_files_test")

    nowUnix = int(time.time())
    randUnix = random.randint(0, nowUnix)
    # randUnix should be rounded to the notation of days and hours

    filesToKeep = {}
    filesToRemove = {}

    for i in range(0, MAX_NR_OF_FILES):
	filename = os.path.join(tmpdir, "%04d" % i)
	randMtime = random.randint(0, nowUnix)
	os.mknod(filename)
	os.utime(filename, (0, randMtime))
	if randMtime < randUnix:
	    filesToRemove[filename] = None
	else:
	    filesToKeep[filename] = None

    if not options.keep:
	recursiveDelete(tmpdir)


if __name__ == "__main__":
    main()

