#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# the plant is watered at programmable time and amount. Group study of the same plant growth rate is an interesting topic

from m2controller import m2controller
from m2controller import m2Const
import signal
import time
import datetime
import usrCfg
import ctypes
def get_iSecondSinceMidNight():
    now = datetime.datetime.now()
    return round((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())

def get_iSecondFromHMS(hour,minute,second):
    return (hour*60+minute)*60+second

def second2HWunitTime(iSecond):
    return iSecond*10
    
requestExit = False
def signal_handler(sig, frame):
    global requestExit
    print('user Ctrl-C')
    requestExit = True

signal.signal(signal.SIGINT, signal_handler)

# return true if error detected
def sanityCheck():
    hardware_settings = controller.readSettingData()
    '''
    if (hardware_settings['CH0dutyCycleMode']):
        return True
    if (hardware_settings['CH1dutyCycleMode']):
        return True
    if (hardware_settings['CH01_merged2be_H_bridge']):
        return True
    '''
    return False

def callbackfunc(telemetry):
    pass

bUseCallBack = False #True False, choose to use callback or explicit read request for telemetry data retrieval
controller = m2controller.BleCtrller(m2Const.etDebian,None,usrCfg.BleMACinfoList)

controller.connect() # establish hw connection
if sanityCheck():    # hw configuration sanity test
    print("controller HW setting cfg error")
else:
    iSecond = 0 # timer
    if True: #True: False
        controller.flashActionResetFlashStorage()
        constVal = 0x80;
        controller.flashActionSave2Flash(second2HWunitTime(get_iSecondSinceMidNight(8,0,2)),0x1+constVal,list(bytes(ctypes.c_int8(-128)))*m2Const.RcPWMchanNum)
        controller.flashActionSave2Flash(second2HWunitTime(get_iSecondSinceMidNight(8,0,4)),0x2+constVal,list(bytes(ctypes.c_int8(127)))*m2Const.RcPWMchanNum)
        controller.flashActionSave2Flash(second2HWunitTime(get_iSecondSinceMidNight(8,0,6)),0x3+constVal,list(bytes(ctypes.c_int8(-128)))*m2Const.RcPWMchanNum)
        controller.flashActionSave2Flash(second2HWunitTime(get_iSecondSinceMidNight(8,0,8)),0x4+constVal,list(bytes(ctypes.c_int8(127)))*m2Const.RcPWMchanNum)
        controller.flashActionSave2Flash(second2HWunitTime(get_iSecondSinceMidNight(8,0,10)),0,list(bytes(ctypes.c_int8(-128)))*m2Const.RcPWMchanNum)
        controller.flashActionEndOfSequence()
    controller.flashActionSetTimeOneTenthS(second2HWunitTime(get_iSecondSinceMidNight(8,0,0)))
    controller.flashActionResetSequenceExecAndGo()

        #photofilename = 'photo-{date:%Y-%m-%d-%H_%M_%S}.jpg'.format(date=datetime.datetime.now())
        #controller.take_a_photo(photofilename) #take photo, file name format:photo-year-,pmtj-day-hour-min-sec.jpg
