#!/usr/bin/env python

from hostwinds.hostwinds import BaseHostwindsAPI

class BandWidthAlert(BaseHostwindsAPI):
  def __init__(self, keyFile, alertThreshold=0.9):
    super(BandWidthAlert, self).__init__(keyFile)
    self.__threshold = alertThreshold

  def request_data(self):
    res = self.request("get_instances")
    for instance in res['success']:
      tol = instance['bandwidth']
      used = instance['bandwidth_used']

      if None == tol:
        tolVal = None
      else:
        tolVal = tol * 1000000000

      if None == used:
        usedVal = None
      else:
        usedVal  = float(used)

      yield (tolVal, usedVal, instance['name'])

  def alert(self):
    for (bandwidthTol, bandwidthUsed, name) in self.request_data():
      if None == bandwidthTol or None == bandwidthUsed:
        yield (name, "unknown")
      elif bandwidthUsed >= (bandwidthTol * self.__threshold):
        yield (name, bandwidthUsed / bandwidthTol)

if __name__ == '__main__':
  alert = BandWidthAlert('/tmp/key', 0.00000007)
  for alertInfo in alert.alert():
    print(alertInfo)
