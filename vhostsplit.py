#!/usr/bin/env python
#
# @file         vhostsplit.py
# @author       Alexandru Apostolache 
# @email        apostolacheac@gmail.com
# @description  splits <VirtualHost> entries into multiple files in the current folder and creates a copy of the original input

# @ todo 	clean the original input file for VirtualHost in the new created copy - function to delete a row already done
# @ todo	scan apachectl -S and take the input from there
# @ todo	create /home/rack/ticketnumber/vhost-split where all the work should be and the input should be only the ticketnumber (validate)

import re
import sys
from shutil import copyfile
import ntpath

if len(sys.argv) == 1:
  print "\n!!! The output will be in the current folder !!! \n\nUsage: \n\n %s </path/to/config_file> \n" % sys.argv[0]
  sys.exit(1)

def path_leaf(path):
  head, tail = ntpath.split(path)
  return tail or ntpath.basename(head)

def fileCopy(filename):
  try:
    copyfile(filename, path_leaf(filename)+".new")
  except IOError:
    print "\n!!! File %s doesn't exist \n" % filename
    sys.exit(1)
  else:
    return path_leaf(filename)+".new"

def new_httpd_conf(inputFile,stringToDelete):
  with open(inputFile, "r") as f:
    rows = f.readrows()
  with open(inputFile, "w") as f:
    for row in rows:
      if row.strip("\n") != stringToDelete:
        f.write(row)

newInputFile=fileCopy(sys.argv[1])
print "\nName for new config file stripped of VirtualHost(s): %s \n\n" % newInputFile,
# @todo strip the file of VirtualHost(s)

inputFile = open(newInputFile, "rb")

lineCommented = re.compile(r"[\s\t]*#.*")
startVirtualHost = re.compile(r"<VirtualHost[^>]+>")
endVirtualHost = re.compile(r"</VirtualHost>")
matchServerName = re.compile(r"ServerName[\s\t]*(.*)")
fileName = "dummy-host"
f = False
c = False
serverName = {}
virtualHostLines = []
totalNumber = 0
cNumber = 0

for row in inputFile:
  if not f:
    p = startVirtualHost.search(row)
    if p:
      f = True
      fileName = "dummy-host"
      virtualHostLines.append(row)
      p = lineCommented.search(row)
      c = False
      if p:
        c = True
  else:
    virtualHostLines.append(row)
    p = matchServerName.search(row)
    if p:
      fileName = p.group(1).strip()
    p = endVirtualHost.search(row)
    if p:
      f = False
      if fileName in serverName:
        serverName[fileName] += 1
        fileName += "-%d" % serverName[fileName]
      else:
        serverName[fileName] = 0
      print "Creating new VirtualHost file - %s" % fileName,
      if c:
        cNumber += 1
        print " (commented)"
      else:
        print
      output = open(fileName, "wb")
      output.writelines(virtualHostLines)
      output.close()
      virtualHostLines = []
      totalNumber += 1
inputFile.close()
print "\nSummary: %d virtual hosts from which %d commented.\n" % (totalNumber, cNumber)
