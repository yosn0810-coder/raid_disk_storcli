#!/usr/bin/python3
# -*- coding: utf-8 -*-

# runcached
# Execute commands while caching their output for subsequent calls. 
# Command output will be cached for $cacheperiod and replayed for subsequent calls
#
# Author Spiros Ioannou sivann <at> inaccess.com
#

import os
import sys
import subprocess
import time
import hashlib
import random
import atexit
import syslog
import getpass

cacheperiod = 27  # seconds
maxwaitprev = 5   # seconds to wait for previous same command to finish before quiting
minrand = 0       # random seconds to wait before running cmd
maxrand = 0

cachedir = "/tmp/cache_" + getpass.getuser()
if not os.path.isdir(cachedir):
    try:
        os.mkdir(cachedir)
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            raise

def cleanup(pidfile):
    if os.path.isfile(pidfile):
        try:
            os.remove(pidfile)
        except OSError:
            pass

def myexcepthook(exctype, value, traceback):
    syslog.syslog(syslog.LOG_ERR, str(value))
    _old_excepthook(exctype, value, traceback)

def runit(cmd, cmddatafile, cmdexitcode, cmdfile):
    try:
        with open(cmddatafile, 'w') as f_stdout:
            p = subprocess.Popen(cmd, stdout=f_stdout, stderr=f_stdout, shell=True)
            p.communicate()
            exitcode = p.returncode

        with open(cmdfile, 'w') as f:
            f.write(cmd)
        with open(cmdexitcode, 'w') as f:
            f.write(str(exitcode))
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f"runcached error running command {cmd}: {str(e)}")

def file_get_contents(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except IOError:
        return ""

# install cleanup hook
_old_excepthook = sys.excepthook
sys.excepthook = myexcepthook

def main():
    global cacheperiod
    argskip = 1

    if (len(sys.argv) < 2) or (len(sys.argv) == 2 and sys.argv[1] == '-c'):
        sys.exit(f'Usage: {sys.argv[0]} [-c cacheperiod] <command to execute with args>')

    if sys.argv[1] == '-c':
        try:
            cacheperiod = int(sys.argv[2])
            argskip = 3
        except (IndexError, ValueError):
            sys.exit(f'Usage: {sys.argv[0]} [-c cacheperiod] <command to execute with args>')

    cmd = " ".join(sys.argv[argskip:])

    # hash of executed command w/args
    m = hashlib.md5()
    m.update(cmd.encode('utf-8'))
    cmdmd5 = m.hexdigest()

    # random sleep to avoid racing condition
    if maxrand - minrand > 0:
        time.sleep(random.randrange(minrand, maxrand))

    pidfile = os.path.join(cachedir, f"{cmdmd5}-runcached.pid")
    cmddatafile = os.path.join(cachedir, f"{cmdmd5}.data")
    cmdexitcode = os.path.join(cachedir, f"{cmdmd5}.exitcode")
    cmdfile = os.path.join(cachedir, f"{cmdmd5}.cmd")

    atexit.register(cleanup, pidfile)

    # don't run the same command in parallel
    count = maxwaitprev
    while os.path.isfile(pidfile):
        prevpid = file_get_contents(pidfile).strip()
        if not prevpid or not os.path.exists(f"/proc/{prevpid}"):
            try:
                os.remove(pidfile)
            except OSError:
                pass
            break
        time.sleep(1)
        count -= 1
        if count == 0:
            sys.stderr.write(f"timeout waiting for '{cmd}' to finish. (pid: {pidfile})\n")
            sys.exit(1)

    # write pidfile
    mypid = os.getpid()
    try:
        with open(pidfile, 'w') as f:
            f.write(str(mypid))
    except IOError as e:
        sys.stderr.write(f"Error writing pidfile {pidfile}: {str(e)}\n")

    # if not cached before, or too old, run it
    should_run = not os.path.isfile(cmddatafile)
    if not should_run:
        lastrun = int(os.path.getmtime(cmddatafile))
        diffsec = int(time.time()) - lastrun
        if diffsec > cacheperiod:
            should_run = True

    if should_run:
        runit(cmd, cmddatafile, cmdexitcode, cmdfile)

    if os.path.isfile(cmddatafile):
        sys.stdout.write(file_get_contents(cmddatafile))

if __name__ == '__main__':
    main()
