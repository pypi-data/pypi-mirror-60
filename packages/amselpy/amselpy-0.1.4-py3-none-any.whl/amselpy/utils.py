import time

class Utils():

  ## Setter
  # Set new default speed
  def setSpeed(self, newSpeed):
    print "Amsel CLI used %s as default speed now it uses %s" % (self.speed, newSpeed)
    self.speed = newSpeed

  ## Getter
  # Get the current default speed
  def getSpeed(self):
    return self.speed

  # Returns teh distance measured by the IR sensor
  def getDistance(self):
    endpoint = "/distance"
    response = self.get(endpoint)
    print(response.status)

  # Perform get request and return status
  def get(self, path):
    connection = self.enableHTTPConnection(self.local_ip)
    connection.request("HEAD", path)
    response = connection.getresponse()
    return response

  ## Helper
  # Set amsel to sleep for a certain amount of time
  def sleep(self, duration=0):
    time.sleep(duration)