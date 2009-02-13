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

import datetime
import optparse
import os
import random
import shutil
import sys
import tempfile
import time


def genTimeIntervallStr(time1, time2):
    '''Generates a time intervall string like "3d4h" out of two given unix timestamps.
    The time intervall string can be used for cleanup_old_files.py.
    Returns a tuple of intervallStr and timestamp rounded to notation.'''

    datetime1 = datetime.datetime.fromtimestamp(time1)
    datetime2 = datetime.datetime.fromtimestamp(time2)

    diff = abs(datetime2 - datetime1)
    hours = int(diff.seconds/3600)

    intervallStr = str(diff.days) + "d" + str(hours) + "h"
    timestampRounded = max(datetime1, datetime2) - datetime.timedelta(diff.days, hours*3600)

    return intervallStr, int(time.mktime(timestampRounded.timetuple()))


def recursiveDelete(dirname):
    '''Deletes recursively dirname and all sub directories and all files.'''
    for root, dirs, files in os.walk(dirname, topdown=False):
	for name in files:
	    os.remove(os.path.join(root, name))
	for name in dirs:
	    os.rmdir(os.path.join(root, name))
    os.rmdir(root)


def main():
    MAX_NR_OF_FILES = 10000

    parser = optparse.OptionParser(
	    usage="%prog [options]",
	    version="%prog " + os.linesep +
	    "Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de>",
	    epilog="Return code is 0 on successfull tests, 1 on any execution error in test program, 2 on failed tests")
    parser.add_option("-k","--keep",
	    dest="keep", default=False, action="store_true",
	    help="Does not delete temporary directories/files")
    
    (options, args) = parser.parse_args()

    try:
	tmpDir = tempfile.mkdtemp("","cleanup_old_files_test")
	testDir = os.path.join(tmpDir, "test")
	os.mkdir(testDir)
    except:
        print "Could not create test directories in " + tmpdir + ". Aborting."
        sys.exit(1)

    now = int(time.time())
    randomTime = 0
    roundedTime = 0
    # avoids that a random time is generated which is rounded off to 0 or rounded up to now
    while (roundedTime <= 0) or (roundedTime >= now):
	randomTime = random.randint(0,now)
	timeIntervallStr, roundedTime = genTimeIntervallStr(randomTime, now)
    randomTime = roundedTime

    print "Diced random timestamp %s (%d)" % (time.ctime(randomTime), randomTime)

    filesToKeep = {}
    filesToRemove = {}

    for i in range(0, MAX_NR_OF_FILES):
	filename = os.path.join(testDir, "%04d" % i)
	randMtime = random.randint(0, now)
	os.mknod(filename)
	os.utime(filename, (0, randMtime))
	if randMtime < randomTime:
	    filesToRemove[filename] = None
	else:
	    filesToKeep[filename] = None

    print "Expected: filesToKeep: %d, filesToRemove: %d" % (len(filesToKeep), len(filesToRemove))

    origDir = os.path.join(tmpDir, "orig")
    shutil.copytree(testDir, origDir)

    cmdStr = "python cleanup_old_files.py -w " + testDir + " " + timeIntervallStr
    print "calling " + cmdStr
    os.system(cmdStr)

    filesLeft = {}
    for entry in os.listdir(testDir):
	filename = os.path.join(testDir,entry)
	filesLeft[filename] = None

    returnCode = 0
    for key in filesToRemove:
	if filesLeft.has_key(key):
	    print "ERROR: file %s has not been removed!" % key
	    returnCode = 2

    for key in filesToKeep:
	if not filesLeft.has_key(key):
	    print "ERROR: file %s has been removed, but should not!" % key
	    returnCode = 2

    if not options.keep:
	recursiveDelete(tmpDir)

    if returnCode == 0:
	print "ALL TESTS SUCCEEDED!"
    sys.exit(returnCode)


if __name__ == "__main__":
    main()

