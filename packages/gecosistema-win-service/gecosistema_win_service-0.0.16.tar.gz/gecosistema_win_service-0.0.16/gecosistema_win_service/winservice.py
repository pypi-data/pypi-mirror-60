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
import os,sys,datetime


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
    _svc_description_    = "This is a General Python Windows Service"

    @classmethod
    def install(self):
        win32serviceutil.HandleCommandLine(self)

    def log(self,text):
        print(text)

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        try:
            # Wait for service stop signal, if I timeout, loop again
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal encountered
                self.SvcStop()

            else:
                #Time to execute
                self.alarm()

        except Exception as ex:
            self.SvcStop()


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




