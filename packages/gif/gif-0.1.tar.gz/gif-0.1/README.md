### gif



##### Installation

```
pip install gif
```



##### Usage

```
import random
from matplotlib import pyplot as plt

import gif
```

Decorate your plotting function with `gif.frame`:

```
@gif.frame
def plot(x, y):
    plt.figure(figsize=(5, 5))
    plt.scatter(x, y)
    plt.xlim((0, 100))
    plt.ylim((0, 100))
```

Build a bunch of frames:

```
frames = []
for _ in range(50):
    n = 10
    x = [random.randint(0, 100) for _ in range(10)]
    y = [random.randint(0, 100) for _ in range(10)]
    frame = plot(x, y)
    frames.append(frame)
```

Finally, save the gif:

```
gif.save(frames, 'yay.gif')
```