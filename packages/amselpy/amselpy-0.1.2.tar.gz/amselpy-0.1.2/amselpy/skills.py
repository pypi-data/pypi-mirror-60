class Skills():

  def __init__(self, speed=100):
    self.speed = speed

  # Set new default speed
  def setSpeed(self, newSpeed):
    self.speed = newSpeed
    print("Amsel CLI uses now %s as default speed" % self.speed)

  # Get the current default speed
  def getSpeed(self, newSpeed):
    return self.speed
    print("Amsel CLI uses %s as default speed" % self.speed)

  # Define movement functions.for
  def forward(self, speed=0):
    if not speed: speed = self.speed
    endpoint = "/forward?speed=%s" % speed
    response = self.get(endpoint)

  def backward(self, speed=0):
    if not speed: speed = self.speed
    endpoint = "/reverse?speed=%s" % speed
    response = self.get(endpoint)
    print(response.status)

  def left(self, speed=0):
    if not speed: speed = self.speed
    endpoint = "/left?speed=%s" % speed
    response = self.get(endpoint)
    print(response.status)

  def right(self, speed=0):
    if not speed: speed = self.speed
    endpoint = "/right?speed=%s" % speed
    response = self.get(endpoint)
    print(response.status)

  # Stop movement
  def stop(self):
    endpoint = "/stop"
    response = self.get(endpoint)
    print(response.status)

  # Set amsel to sleep for a certain amount of time
  def sleep(self, duration=0):
    time.sleep(duration)
