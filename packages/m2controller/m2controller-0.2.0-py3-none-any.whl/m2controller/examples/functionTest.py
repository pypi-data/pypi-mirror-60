#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from m2controller import m2controller
from m2controller import m2Const
from m2controller import constShared
import signal,sys
import time
import usrCfg

requestExit = False

def signal_handler(sig, frame):
    global requestExit
    print('user Ctrl-C')
    requestExit = True
    
signal.signal(signal.SIGINT, signal_handler)

def callbackfunc(telemetry):
    if telemetry['m_BtnStatus'][0] == 0:
        TouchEvent = 0
    else:
        TouchEvent = 1
    BtnStatus = telemetry['m_BtnStatus']
    print("debug BtnStatus: {}".format(BtnStatus))
    
controller = m2controller.BleCtrller(m2Const.etDebian,callbackfunc,usrCfg.BleMACinfoList)
if True:
    controller.connect()
    print('one Time reading of Telemetry Data')
    DictTelemetry = controller.readTelemetryData()
    print("debug DictTelemetry: {}".format(DictTelemetry))
    
while True:
    #controller.set_wallpaper(constShared.emoPic_happy)
    #controller.SendCmdTransBlking()
    #time.sleep(1)
    
    controller.clearPreviousCmd()
    #controller.send_a_SMS("14086665581", "helloworld")
    #controller.take_a_photo("myphoto.jpg")
    for ii in range(m2Const.USR_GPIO_CNT):
        controller.setGPIOn(ii)
    for ii in range(m2Const.RcPWMchanNum):
        controller.setPWM_n_pm1(ii,0.7)
    controller.SendCmdTransBlking()
    
    if controller.getPlatformType() == m2Const.etInternet:
        Telemetry = controller.getMqttTelemetry()
        if Telemetry is not None:
            print(Telemetry)
            
    controller.requestInternetTelemetry()    
    time.sleep(1)
    for ii in range(m2Const.USR_GPIO_CNT):
        controller.resetGPIOn(ii)
    for ii in range(m2Const.RcPWMchanNum):
        controller.setPWM_n_pm1(ii,-0.7)
    controller.SendCmdTransBlking()
    time.sleep(1)

    if requestExit:
        controller.stop()
        break


