#!/usr/bin/python

import sys
import os
import commands
import re
import json
import datetime
import uuid

# input parameter : project path, revertdate
if len(sys.argv) < 3:
    print 'num of parameter wrong ...'
    exit(1)

rootdir = sys.argv[1] if (sys.argv[1][-1] == '/') else sys.argv[1]+'/'
revertdate = sys.argv[2]
datetarget = datetime.datetime.strptime(revertdate, '%Y-%m-%d').date()
jsonall = []
jsonfile = '/tmp/'+str(uuid.uuid4())+'.txt'

def init():
    os.path.exists(jsonfile) and os.remove(jsonfile)

def record_git_log(path):
    command_git = 'cd %s; git log --pretty=format:"%s" --date=short  ' %(path, '%H|%cd|%s')
    git_log_ret = commands.getoutput(command_git).split('\n')
    subpath = path.replace(rootdir, '')
    jsonret = [subpath, git_log_ret]
    jsonall.append(jsonret)

def save_to_file(path):
    file = open(path, 'w')
    try:
        json.dump(jsonall, file)
    except:
        print 'json dump failed'
    finally:
        file.close()

def git_reset_to_date(path):
    jsondata=[]
    try:
        file = open(jsonfile, 'r')
        jsondata = json.loads(file.read())
    except:
        print 'load json failed'
    finally:
        file.close()
    hashret='HEAD'
    for data in jsondata:
        print 'project <'+data[0]+'>'
        gitdata = data[1]
        for line in gitdata:
            if datetarget >= datetime.datetime.strptime((line.split('|'))[1], '%Y-%m-%d').date():
                hashret=(line.split('|'))[0]
                print "\treset to ["+line+']'
                break
    command_git = 'cd %s; git checkout %s' %(path, hashret)
    commands.getoutput(command_git)


# reverse project manifest
init()
record_git_log(rootdir+'.repo/manifests');
save_to_file(jsonfile)
git_reset_to_date(rootdir+'.repo/manifests')
command_git = 'cd %s; repo sync' %(rootdir)
commands.getoutput(command_git)

print "==================== reset manifest done ======================"

# traverse root directory
init()
for subroot, dirs, files in os.walk(rootdir):
    skipdir = ['.repo']
    if subroot.replace(rootdir, '') in skipdir:
        continue
    for d in dirs:
        if d == '.git':
            record_git_log(subroot)
            save_to_file(jsonfile)
            git_reset_to_date(subroot)
            jsonall=[]
            break
