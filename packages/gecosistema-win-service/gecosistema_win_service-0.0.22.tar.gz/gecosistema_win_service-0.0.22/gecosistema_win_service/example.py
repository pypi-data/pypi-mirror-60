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
import os,sys
import datetime
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
    _svc_description_  = "This is an Example Python Windows Service"

    #Override this method
    def run(self):
        if self:
            now = datetime.datetime.now()
            filename = "D:/WatchDogSvc.log"
            with open(filename, "a") as stream:
                stream.write(now.strftime("running @ %H:%M:%S...\n"))

    Run = staticmethod(run)




if __name__ == '__main__':


    DEBUG = len(sys.argv)<=1

    if not DEBUG:
        WatchDogSvc.install()
    else:
        WatchDogSvc.Run(False)

