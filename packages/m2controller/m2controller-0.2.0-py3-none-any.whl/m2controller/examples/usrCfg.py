#!/usr/bin/env python
from m2controller import constShared
# -*- coding: UTF-8 -*-
#BleMACinfoList= [["80:6F:B0:A7:F7:BF",constShared.fwImage_generic]] # ICE-debugger
#BleMACinfoList= [["80:6F:B0:2C:E5:82",constShared.fwImage_stepMotor]] # microscope
#BleMACinfoList= [["80:6F:B0:A7:F4:41",constShared.fwImage_generic]] # wearable
BleMACinfoList= [["80:6F:B0:A7:F7:8A",constShared.fwImage_generic]] # experiment
#BleMACinfoList= [["80:6F:B0:A7:F7:AF",constShared.fwImage_generic],["80:6F:B0:A7:F7:81",constShared.fwImage_generic],["80:6F:B0:A7:F5:F1",constShared.fwImage_generic],["80:6F:B0:2C:E3:EF",constShared.fwImage_generic]] #
RaspberrPiName = 'tigerRPi'
adaptorID = 0
InternetHostIPaddr =  "breakthru.xyz" # typically your mqtt server IP 192.168.31.211
IntranetHostIPaddr = "192.168.31.68" # typically your mobile phone
mqttPort = 1883
mqttusername = "dev"
mqttpassword = "BreakThru.xyz"

