#-------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2020 Luzzi Valerio for Gecosistema S.r.l.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:         WindowsService.py
# Purpose:      Run a python script as Windows Service
#
# Author:      Luzzi Valerio
#
# Created:     29/01/2020
#-------------------------------------------------------------------------------
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys,datetime


def now():
    return datetime.datetime.now()

def yesterday():
    return datetime.datetime.now() - datetime.timedelta(days=1)

def justpath(pathname, n=1):
    """
    justpath
    """
    for j in range(n):
        (pathname, _) = os.path.split(pathname)
    if pathname=="":
        return "."
    return os.path.normpath(pathname).replace("\\", "/")


class WindowsService(win32serviceutil.ServiceFramework):

    _svc_name_ = __name__
    _svc_display_name_   = _svc_name_
    _svc_interval_       = 30000  #30 seconds
    _svc_working_dir     = justpath(__file__)
    _svc_next_execution  = now()

    @classmethod
    def install(self):
        win32serviceutil.HandleCommandLine(self)

    def log(self,text):
        print(text)

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        self.SvcSetStartDate()

    def getWorkdir(self):
        return self._svc_working_dir

    #Set the hour of starting with the folder name
    def SvcSetStartDate(self):
        self._svc_interval_ = 10*1000 #milliseconds
        self._svc_start_date = yesterday()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.log("Service - STARTED!\n")
        self.timeout =0
        self.SvcSetStartDate()
        self._svc_next_execution = self._svc_start_date

        #Calculate delta
        delta = (self._svc_next_execution-now()).total_seconds()*1000
        while delta <0:
            self._svc_next_execution += datetime.timedelta(milliseconds = self._svc_interval_)
            delta = (self._svc_next_execution-now()).total_seconds()*1000

        self.setTimerTo(self._svc_next_execution)

        while True:
            try:
                # Wait for service stop signal, if I timeout, loop again
                rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
                # Check to see if self.hWaitStop happened
                if rc == win32event.WAIT_OBJECT_0:
                    # Stop signal encountered
                    servicemanager.LogInfoMsg("%s - STOPPED!"%self._svc_name_)  #For Event Log
                    break
                else:
                    #Time to execute
                    delta = (self._svc_next_execution-now()).total_seconds()*1000

                    if delta >0:
                        self.setTimerTo(self._svc_next_execution)

                    if delta <0:
                        self.alarm()
                        self._svc_next_execution += datetime.timedelta(milliseconds = self._svc_interval_)
                        self.timeout = 0

            except Exception as ex:
                self.log("Exception cycle %s"%ex)

    def setTimerTo(self,date):
        delta = (date-now()).total_seconds()*1000
        while self.timeout < delta:
            self.timeout +=500
        #self.log("Next execution in %s s"%(self.timeout/1000))

    def alarm(self):
        #If some condition call run()
        if True:
            self.run()

    #Override this method
    def run(self):
        #Here DO The JOB here!
        text ="Ok running @ %s. "%(now())
        if self:
            self.log(text)
        else:
            print(text)

    Run = staticmethod(run)




