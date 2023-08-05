# AmselPy

### Usage
Install package from pip:
```sh
pip install amselpy
```

Use it in your project:
``` python
# import library
from amselpy import Amsel

# create instance
amsel = Amsel()

# set adress
amsel.use("<YOUR-AMSELS-IP>")

# control movements
amsel.forward()
amsel.sleep(5)
amsel.stop()
```
### Documentation
For further information read the [documentation](https://baumeise.github.io/amsel/docs).

### License
[MIT License](https://github.com/baumeise/amselpy/blob/master/LICENSE) | Copyright © 2019 Moritz Gut (moritzgvt)
