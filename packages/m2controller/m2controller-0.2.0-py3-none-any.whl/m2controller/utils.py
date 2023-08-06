#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from m2controller import constShared
def isRaspberryPi():
    unameRes = str(os.uname())
    if -1 == unameRes.find('raspberrypi') and -1 == unameRes.find('armv7l'):
        return False
    else:
        return True

def analyzeBleDevName(strBleDevName):
    if strBleDevName.__len__() == constShared.bleDevScanNameLen:
        # hwType, versionMajorMinor, device_name
        return strBleDevName[constShared.bleDevScanNameLen - 4],strBleDevName[constShared.bleDevScanNameLen - 2:constShared.bleDevScanNameLen],strBleDevName[0:constShared.bleDevScanNameLen-4]
    else:
        return '','',''