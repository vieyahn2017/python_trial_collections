#!/usr/bin/python
"""
Initiator Class for testing PGR
"""

import os
import logging

from cmd import runCmdWithOutput
from reservation import Reservation


################################################################

log = logging.getLogger('nose.user')

################################################################


class Initiator:
    """A General PGR initiator"""
    def __init__(self, dev, key):
        self.dev = dev
        self.key = key

    def runSgCmdWithOutput(self, cmd):
        """Run the SG command on specified host"""
        my_cmd = ["sg_persist", "-n"] + cmd + [self.dev]
        return runCmdWithOutput(my_cmd)

    def getRegistrants(self):
        """Get list of registrants using specified initiator"""
        registrants = []
        res = self.runSgCmdWithOutput(["-k"])
        if "no registered reservation keys" not in res.lines[0].lower():
            for l in res.lines[1:]:
                log.debug("key=%s" % l.strip())
                registrants.append(l.strip())
        log.debug("Returning registrants list: %s" % registrants)
        return registrants

    def register(self):
        """Register the remote I_T Nexus"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--register",
             "--param-sark=" + self.key])
        return res.result

    def registerAndIgnore(self, new_key):
        """Register the remote I_T Nexus"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--register",
             "--param-rk=" + self.key,
             "--param-sark=" + new_key])
        return res.result

    def unregister(self):
        """UnRegister the remote I_T Nexus"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--register",
             "--param-rk=" + self.key])
        return res.result

    def reserve(self, prout_type):
        """Reserve for the host using the supplied type"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--reserve",
             "--param-rk=" + self.key,
             "--prout-type=" + prout_type])
        return res.result

    def getReservation(self):
        """Get current reservation"""
        retry_cnt = 3
        while retry_cnt > 0:
            res = self.runSgCmdWithOutput(["-r"])
            if res.result == 0:
                break
            if res.result != 6:
                log.debug("oh oh -- strange error returned: %d" % res.result)
                return None
            if retry_cnt == 1:
                log.debug("oh oh -- command failed to run after retry")
                return None
            log.debug("command returned %d so retrying" % res.result)
            retry_cnt = retry_cnt - 1
        if not res.lines:
            log.debug("No lines! FAIL")
            return None
        log.debug("Parsing %d lines of reservations:" % len(res.lines))
        for o in res.lines:
            log.debug("line=%s" % o)
        rr = Reservation()
        if "Reservation follows" in res.lines[0]:
            rr.key = res.lines[1].split("=")[1]
            rline = res.lines[2]
            ridx = rline.index("type:")
            rr.rtype = rline[ridx:].split(":")[1].strip()
            log.debug("Reservation: found key=%s type=%s" % (rr.key, rr.rtype))
        else:
            log.debug("No Reservation found")
        return rr

    def release(self, prout_type):
        """Reserve for the host using the supplied type"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--release",
             "--param-rk=" + self.key,
             "--prout-type=" + prout_type])
        return res.result

    def clear(self):
        """Clear Registrations and Reservation on a target"""
        res = self.runSgCmdWithOutput(
            ["--out",
             "--clear",
             "--param-rk=" + self.key])
        return res.result

    def getDiskInquirySn(self):
        """Get the Disk Serial Number"""
        res = runCmdWithOutput(["sg_inq", self.dev])
        ret = None
        if res.result == 0:
            if "Unit serial number" in res.lines[-1]:
                line = res.lines[-1]
                ret = line.split()[-1]
        log.debug("getDiskInquirySn(%s) -> %s" % (self.dev, ret))
        return ret

    def runTur(self):
        """Clear any UA by sending TUR"""
        res = runCmdWithOutput(["sg_turs", self.dev])
        return res.result

    def readFromTarget(self):
        """See if we can read from the target"""
        return runCmdWithOutput(["dd",
                                 "if=" + self.dev,
                                 "iflag=direct",
                                 "of=/dev/null",
                                 "skip=1",
                                 "bs=4096",
                                 "count=1"])
        
    def writeToTarget(self):
        """See if we can write to the target (destructive!) """
        return runCmdWithOutput(["dd",
                                 "if=/dev/zero",
                                 "of=" + self.dev,
                                 "oflag=direct",
                                 "bs=4096",
                                 "skip=1",
                                 "seek=1",
                                 "count=1"])

#
# For all to use
#

initA = Initiator("/dev/sdc", "0x123abc")
initB = Initiator("/dev/sdd", "0x696969")
initC = Initiator("/dev/sde", None)
