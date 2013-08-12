#!/usr/bin/python
#****************************************************************#
# ScriptName: trace.py
# Author: wangheng.wh@alibaba-inc.com
# Create Date: 2013-08-09 21:55
# Modify Author: wangheng.wh@alibaba-inc.com
# Modify Date: 2013-08-09 21:55
# Function: Subprocess trace.
#***************************************************************#


import os
import sys
import resource
from ptrace.binding import (ptrace_syscall,ptrace_attach,ptrace_getregs)
from ptrace.syscall import SYSCALL_NAMES

def wait_status():
    status = None
    pid, status = os.waitpid(-1,0)
    if os.WIFEXITED(status):
        print "-- child process was exited."
        return -1
    if os.WIFSIGNALED(status):
        print "-- child process terminated by a signal."
        return -1
    if os.WCOREDUMP(status):
        print "-- child process coredump."
        return -1
    if os.WSTOPSIG(status):
        return 0
    return -1

def trace(pid):

    ptrace_attach(pid)
    if wait_status() == -1:
        return -1
    print "-- start traceing %d ..." %pid

    while True:
        ptrace_syscall(pid)
        if wait_status() == -1:
            ptrace_detach(pid)
            return -1
        regs = ptrace_getregs(pid)
        res = SYSCALL_NAMES.get(regs.orig_rax)
        if res == "clone" or res == "fork" or res == "vfork" or res == "execve":
            limit = resource.getrlimit(resource.RLIMIT_NPROC)
            if regs.rax > 0 and regs.rax < limit[1]:
                print "create new child: %s" %regs.rax
    return 0


if __name__ == "__main__":
    ppid = int(sys.argv[1])
    trace(ppid)

