'''
Based on this article:
http://www.chrisumbel.com/article/windows_services_in_python
'''

import os, sys, time, subprocess, importlib

import servicemanager, traceback
from win32api import CloseHandle, GetLastError, SetConsoleCtrlHandler
import win32event, win32service, win32serviceutil


class WindowsService(win32serviceutil.ServiceFramework):
    # you can NET START/STOP the service by the following name
    _svc_name_ = "WindowsService"
    # this text shows up as the service name in the Service
    # Control Manager (SCM)
    _svc_display_name_ = "Windows Service"
    # this text shows up as the description in the SCM
    _svc_description_ = "Windows service example"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        SetConsoleCtrlHandler(lambda x: True, True)
        # create an event to listen for stop requests on
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.module_2run = None

    # core logic of the service
    def SvcDoRun(self):
        # Go to module install directory
        os.chdir(os.path.dirname(__file__))
        servicemanager.LogMsg (
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_,'')
        )
        try: # try main
            rc_ = None
            # if the stop event hasn't been fired keep looping
            while rc_ != win32event.WAIT_OBJECT_0:
                # Log message before module run
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    0xF000, ("Call module_2run", '')
                )

                # Import of reload module to run
                if not self.module_2run: self.module_2run = importlib.import_module('module_2run')
                else: importlib.reload(self.module_2run)

                # Call module main function
                self.module_2run.main()

                # Log message after module run
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    0xF000, ("Exit module_2run", '')
                )

                # block for 20 seconds and listen for a stop event every 5 seconds
                wt_ = 20000
                ct_ = 5000
                ic_ = wt_ / ct_
                while ic_ >= 0:
                    ic_ -= 1
                    rc_ = win32event.WaitForSingleObject(self.hWaitStop, ct_)
                    if rc_ == win32event.WAIT_OBJECT_0: break

        except:
            servicemanager.LogErrorMsg(traceback.format_exc()) # if error print it to event log
            os._exit(-1) # return some value other than 0 to OS so that service knows to restart

    # called when we're being shut down
    def SvcStop(self):
        # tell the SCM we're shutting down
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # fire the stop event
        win32event.SetEvent(self.hWaitStop)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(WindowsService)
