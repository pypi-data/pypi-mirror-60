import time
import requests

class Utils():

  ## Setter
  # Set IP
  def use(self, newIP):
    self.local_ip = newIP
    print("Amsel CLI uses now %s for requests" % self.local_ip)

  # Set new default speed
  def setSpeed(self, newSpeed):
    print("Amsel CLI used %s as default speed now it uses %s") % (self.speed, newSpeed)
    self.speed = newSpeed

  ## Getter
  # Get the current default speed
  def getSpeed(self):
    return self.speed

  # Returns teh distance measured by the IR sensor
  def getDistance(self):
    endpoint = "/distance"
    response = self.get(endpoint)
    return response.text

  # Perform get request and return status
  def get(self, endpoint):
    path = "http://" + str(self.local_ip) + str(endpoint)
    response = requests.get(path)
    return response

  # Return IP
  def IP(self):
    print("Amsel CLI uses %s as IP" % self.local_ip)
    return self.local_ip

  # Return address
  def address(self):
    print("Amsel CLI uses %s as network address" % self.local_address)
    return self.local_address

  ## Helper
  # Set amsel to sleep for a certain amount of time
  def sleep(self, duration=0):
    time.sleep(duration)