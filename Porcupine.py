#!/usr/bin/python

import wx
from wx import xrc
import subprocess
from pyudev import Context, Monitor
import pyudev.wx


class Porcupine_main(wx.Frame):
    def __init__(self):
        self.InitUI()
        self.observer_status = 0
        self.obs = Observer(self.radio_mode, self.chkbox_usb, self.chkbox_cd, self.chkbox_sd)
        self.tskic = PorcupineTaskBarIcon(self)

    def InitUI(self):
        self.ui = xrc.XmlResource('Porcupine.xrc')
        self.frame_settings = self.ui.LoadFrame(None, 'Porcupine_settings')
        
        self.radio_mode = xrc.XRCCTRL(self.frame_settings, "radiobox_mode")
        self.chkbox_usb = xrc.XRCCTRL(self.frame_settings, "chkbox_usb")
        self.chkbox_cd = xrc.XRCCTRL(self.frame_settings, "chkbox_cd")
        self.chkbox_sd = xrc.XRCCTRL(self.frame_settings, "chkbox_sd")
        self.frame_settings.Bind(wx.EVT_CLOSE, self.FrameClose)

    def check_usb():
        pass

    def OnAbout(self, event):
        wx.MessageBox("ABOUT.")

    def OnQuit(self, event):
        self.tskic.Destroy()
        if self.frame_settings:
            self.frame_settings.Destroy()

    def FrameClose(self, event):
        self.frame_settings.Hide()

    def OnSettings(self, event):
        if not self.frame_settings:
            self.frame_settings = self.ui.LoadFrame(None, 'Porcupine_settings')
        self.frame_settings.Show()

    def OnObserverStart(self, event):
    	if(self.observer_status == 0):
            self.obs.OnStart()
            self.observer_status = 1
        elif(self.observer_status == 1):
            pass
        else:
            pass

    def OnObserverStop(self, event):
        if(self.observer_status == 1):
            self.obs.OnStop()
            self.observer_status = 0
        elif(self.observer_status == 0):
            pass
        else:
            pass


class PorcupineTaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon('porcupine_icon.png', wx.BITMAP_TYPE_PNG), 'Porcupine')
        self.Bind(wx.EVT_MENU, self.frame.OnObserverStart, id=1)
        self.Bind(wx.EVT_MENU, self.frame.OnObserverStop, id=2)
        self.Bind(wx.EVT_MENU, self.frame.OnSettings, id=3)
        self.Bind(wx.EVT_MENU, self.frame.OnAbout, id=4)
        self.Bind(wx.EVT_MENU, self.frame.OnQuit, id=5)

    def CreatePopupMenu(self):
        self.menu = wx.Menu()
        self.menu.Append(1, 'Start')
        self.menu.Append(2, 'Stop')
        self.menu.Append(3, 'Settings')
        self.menu.Append(4, 'About')
        self.menu.Append(5, 'Quit')
        return self.menu


class Observer:
    def __init__(self, radio_mode, chkbox_usb, chkbox_cd, chkbox_sd):
        self.context = Context()
        self.evil = Evil(self)
        self.radio_mode = radio_mode
        self.chkbox_usb = chkbox_usb
        self.chkbox_cd = chkbox_cd
        self.chkbox_sd = chkbox_sd

    def OnStart(self):
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='block')
        self.obs = pyudev.wx.WxUDevMonitorObserver(self.monitor)
        self.obs.Bind(pyudev.wx.EVT_DEVICE_EVENT, self.OnDispatch)
        self.monitor.start()

    def OnStop(self):
        self.obs.enabled = False

    def OnDispatch(self, event):
        if(str(event.action) == "add" and str(event.device.device_node[7]) != "a" and str(event.device.device_node[5:7]) == "sd" and self.chkbox_usb.GetValue() == True and event.device['ID_BUS'] != "scsi" and event.device['ID_BUS'] == "usb"):
            if(self.radio_mode.GetStringSelection() == "Defensive"):
                self.evil.OnReboot()
            elif(self.radio_mode.GetStringSelection() == "Offensive"):
                self.evil.OnOverwrite(event.device)
            else:
                self.evil.OnOverwrite(event.device)
                self.evil.OnReboot()
        elif(str(event.action) == "change" and str(event.device.device_node[5:7]) == "sr" and self.chkbox_cd.GetValue() == True and event.device['ID_BUS'] == "scsi" and event.device['ID_TYPE'] == 'cd'):
            if(self.radio_mode.GetStringSelection() == "Defensive"):
                self.evil.OnReboot()
            elif(self.radio_mode.GetStringSelection() == "Offensive"):
                self.evil.OnEject(event.device)
            else:
                self.evil.OnEject(event.device)
                self.evil.OnReboot()
        else:
            pass


class Evil:
    def __init__(self, observer):
        self.obs = observer

    def OnReboot(self):
        retcode = subprocess.call("reboot", shell = True)

    def OnOverwrite(self, device):
        dev = str(device.device_node)
        retcode = subprocess.call("cat /dev/urandom > " + dev, shell = True)

    def OnEject(self, device):
        dev = str(device.device_node)
        retcode = subprocess.call("eject -v " + dev, shell = True)


class Porcupine_app(wx.App):
    def OnInit(self):
        Porcupine_main()
        return True

app = Porcupine_app(0)
app.MainLoop()