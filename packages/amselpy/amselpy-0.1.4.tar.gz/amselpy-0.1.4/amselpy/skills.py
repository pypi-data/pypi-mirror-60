import time
import random

class Skills():

  def __init__(self, speed=100):
    self.speed = speed

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

  # Infinite run with obsticle avoidance
  def go(self, duration=-1, proximity=30):
    start = time.time()
    now = time.time()
    try:
      while (now - start) < duration or duration == -1:
        self.forward(100)
        obsticle = 1 if self.getDistance() < proximity else 0
        if obsticle:
          self.stop()
          randomDirection = random.randint(0, 1)
          randomDuration = random.random()*1
          if randomDirection:
            self.right()
          else:
            self.left()
          self.sleep(randomDuration)
          self.stop()
        now = time.time()
    except KeyboardInterrupt:
      print "Wow what a run!"
