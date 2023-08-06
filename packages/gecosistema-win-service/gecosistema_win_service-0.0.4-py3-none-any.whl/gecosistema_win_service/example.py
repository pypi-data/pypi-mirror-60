# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2020 Luzzi Valerio 
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
# Name:        watchdog.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     29/01/2020
# -------------------------------------------------------------------------------
import sys,os
from datetime import datetime
from gecosistema_win_service import *

### Install service
##python example.py stop
##python example.py --startup=auto install
##python example.py start


### Remove service
##python example.py stop
##python example.py remove

class WatchDogSvc(WindowsService):

    _svc_name_         = "WatchDogSvc"
    _svc_display_name_ = _svc_name_

    #Override this method
    def run(self):
        if self:
            now = datetime.now()
            filename = "D:/WatchDogSvc.log"
            with open(filename, "w") as stream:
                stream.write(now.strftime("running @ %H:%M:%S..."))


    Run = staticmethod(run)




if __name__ == '__main__':


    DEBUG = (__file__!="")

    if not DEBUG:
        WatchDogSvc.install()
    else:
        filepy = os.path.basename(__file__)
        filebat = "install.bat"
        if not os.path.isfile(filebat):
            with open(filebat, "w") as stream:
                stream.write("@echo off\n")
                stream.write("python %s stop\n"%(filepy))
                stream.write("python %s --startup=auto install\n"%(filepy))
                stream.write("python %s start\n"%(filepy))
        WatchDogSvc.Run(False)

