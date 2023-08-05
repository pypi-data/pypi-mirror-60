class Connection():

  def __init__(self, local_ip):
    self.local_ip = local_ip
    self.local_address = "amsel.local"

  # Log into network
  async def login(self, ssid, passphrase):
    try:
        return await self.get("/login?ssid=" + ssid + "&pass=" + passphrase)
    except IOError:
        print("Something went wrong we could not connect you to the network!")
    
