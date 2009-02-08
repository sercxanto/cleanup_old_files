#!/usr/bin/python
#
#    cleanup_old_files.py
#
#    Deletes files recursively older than a given modification date
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
import logging
import optparse
import os
import os.path
import re
import sys
import time

VERSIONSTRING = "0.1dev"


def deleteFiles(dirName, date, recurse, deleteEmptySubDirs, write):
    '''Recursively delete files in a directory older than a given modification
    date. Symbolic links are not honoured.
    Parameters: dirName: String. Name of the folder to start search.
    date: Unix timestamp. Files older than date are deleted.
    recurse: Boolean: Should we descend in directories eventually found in
    dirName?
    deleteEmptySubDirs: Boolean: If there are no more files left in a sub
    directory, should we delete it? Does not apply to current directory given
    in dirName!
    write: Boolean. Only if set to true files are really deleted.'''

    logging.debug("deleteFiles(%s, %d, %s, %s, %s) called" %
	    (dirName, date, recurse, deleteEmptySubDirs, write) )
    
    if not os.path.isdir(dirName): return

    for entry in os.listdir(dirName):
	path = os.path.join(dirName, entry)
	if recurse and os.path.isdir(path):
	    deleteFiles(path, date, recurse, deleteEmptySubDirs, write)
	    if deleteEmptySubDirs and (len(os.listdir(path)) == 0):
		logging.info("Deleting directory " + path)
		if write:
		    try:
			os.rmdir(path)
		    except:
			logging.error("Could not delete directory " + path)
	else:
	    if os.path.isfile(path):
		if os.path.getmtime(path) < date :
		    logging.info("Deleting file " + path)
		    if write:
			try:
			    os.unlink(path)
			except:
			    logging.error("Could not delete file " + path)

	    else:
		# todo: Should we honour other entry types too? Note that isdir and
		# islink or isfile and islink can both be true!
		pass


def parseMaxAge(text, datetimestamp):
    '''Parses the maximum age of file given in command line and fills a datetime
    object which this information.

    Examples for valid text format: "3d4h" (3 days 4 hours), "3d" (3 days), "4h" (4
    hours). Limits: 5 digits for days, 6 digits for hours.

    Parameter text: String. Represents time difference relative to now. Format to be defined.
    Parameter datetimestamp: datetime. Defines the absolutive point of time.
    Calculated from text and current timestamp.
    Return true if parsing has succeeded, false on any parsing error.
    '''
    if len(text) == 0:
	return False

    days = 0
    hours = 0
    m = re.match("^(\d{1,5})d(\d{1,6})h$", text)
    if m != None:
	days = int(m.group(1))
	hours = int(m.group(2))
    else:
	m = re.match("^(\d{1,5})d$", text)
	if m != None:
	    days = int(m.group(1))
	else:
	    m = re.match("^(\d{1,6})h$", text)
	    if m != None:
		hours = int(m.group(1))
	    else:
		return False

    seconds = hours * 3600
    # todo: I thought paramters are already parsed as reference. Why this does
    # not work?
    datetimestamp[0] = datetime.datetime.now() - datetime.timedelta(days, seconds)
    return True


########### MAIN PROGRAM #############
def main():
    parser = optparse.OptionParser(
	    usage="%prog [options] directory max_age",
	    version="%prog " + VERSIONSTRING + os.linesep +
	    "Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de>",
	    epilog = "directory: Directory to scan" + os.linesep +
	    "max_age: Examples for valid text format: \"3d4h\" (3 days 4 hours), \"3d\" (3 days), \"4h\" (4 hours). Limits: 5 digits for days, 6 digits for hours. Resulting timestamp must be a valid unix timestamp.")
 
    parser.add_option("-d", "--debuglevel", dest="debuglevel",
	    type="int", default=logging.WARNING,
	    help="Sets numerical debug level, see library logging module. Default is 30 (WARNING). Possible values are CRITICAL 50, ERROR 40, WARNING 30, INFO 20, DEBUG 10, NOTSET 0. All log messages with debuglevel or above are printed. So to disable all output set debuglevel e.g. to 100.")
    parser.add_option("-e", "--empty-delete",
	    dest="emptydelete", default=False, action="store_true",
	    help="Delete empty sub directories? The given root directory will not be deleted.")
    parser.add_option("-r", "--recursive",
	    dest="recursive", default=False, action="store_true",
	    help="Recurses through sub directories")
    parser.add_option("-w", "--write",
	    action="store_true", dest="write", default=False,
	    help="write changes to filesystem (delete files)")

    (options, args) = parser.parse_args()

    logging.basicConfig(format="%(message)s", level=options.debuglevel)

    if len(args) < 2:
	parser.print_help()
	sys.exit(2)


    dirName = os.path.expanduser(args[0])
    if not os.path.isdir(dirName):
	logging.error("directory not found")
	sys.exit(1)

    maxAge = args[1]
    # use array so parameters are passed as referenc and can be altered
    maxAgeDate = []
    maxAgeDate.append(datetime.datetime.max)
    if not parseMaxAge(maxAge, maxAgeDate):
	logging.error("invalid max_age format")
	parser.print_help()
	sys.exit(1)
    if maxAgeDate[0].year < 1970 or maxAgeDate[0].year >= 2038:
	logging.error("Resulting date \"" + str(maxAgeDate) + "\" not supported. Year must be >=1970 and <=2038")
	sys.exit(1)

    deleteFiles(dirName, time.mktime(maxAgeDate[0].timetuple()), options.recursive,
	    options.emptydelete, options.write)


if __name__ == "__main__":
    main()

