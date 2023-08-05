# atlasify

The Python package `atlasify` applies the ATLAS style to matplotlib plots. This includes

 - Switching to Arial font (not Helvetica since it's not widely available),
 - Adding ticks on all edges,
 - Making ticks to inward,
 - Adding the ***ATLAS*** badge with optional labels (e.g. Internal),
 - Adding a description below the badge, and
 - Moving the ***ATLAS*** badge outside the axes area.

## Quickstart

The package will use Helvetica. The
package ships with GPL-licensed Nimbus Sans L as a fallback.

The `atlasify` package can be installed using pip.

```console
pip install atlasify
# or 
pip install https://gitlab.cern.ch/fsauerbu/atlasify/-/archive/master/atlasify-master.tar.gz
```

## Usage

To apply the basic style, simply call the method without any arguments.


<!-- write example.py -->
```python
import matplotlib.pyplot as plt
import numpy as np
from atlasify import atlasify

x = np.linspace(-3, 3, 200)
y = np.exp(-x**2)

plt.plot(x, y)
atlasify()
plt.savefig("test_1.pdf")
```

<!-- append example.py
```python
plt.savefig("test_1.png", dpi=300)
plt.clf()
```
-->

![ATLAS style plot](https://gitlab.cern.ch/fsauerbu/atlasify/-/jobs/artifacts/master/raw/test_1.png?job=doxec)

## Label
If the first argument is a string, e.g. `Internal`, it is added after
the ***ATLAS*** badge.

<!-- append example.py -->
```python3
plt.plot(x, y)
atlasify("Internal")
plt.savefig("test_2.pdf")
```

<!-- append example.py
```python
plt.savefig("test_2.png", dpi=300)
plt.clf()
```
-->

![ATLAS style plot](https://gitlab.cern.ch/fsauerbu/atlasify/-/jobs/artifacts/master/raw/test_2.png?job=doxec)

## Subtext
The second argument can be used to add text on the second line. Multiple lines
are rendered independently.

<!-- append example.py -->
```python3
plt.plot(x, y)
atlasify("Internal", 
         "The Gaussian is defined by the\n"
         "function $f(x) = e^{-x^2}$.\n")
plt.savefig("test_3.pdf")
```

<!-- append example.py
```python
plt.savefig("test_3.png", dpi=300)
plt.clf()
```
-->

![ATLAS style plot](https://gitlab.cern.ch/fsauerbu/atlasify/-/jobs/artifacts/master/raw/test_3.png?job=doxec)

## Enlarge
Usually there is not enought space for the additinal ***ATLAS*** badge. By
default, the method enlarges the y-axis by a factor of `1.3`. The factor can
be changed with the `enlarge` keyword argument.

<!-- append example.py -->
```python3
plt.plot(x, y)
atlasify("Internal", enlarge=1.5)
plt.savefig("test_4.pdf")
```

<!-- append example.py
```python
plt.savefig("test_4.png", dpi=300)
plt.clf()
```
-->

![ATLAS style plot](https://gitlab.cern.ch/fsauerbu/atlasify/-/jobs/artifacts/master/raw/test_4.png?job=doxec)

## Font and figure size and resolution
The font sizes are defined in module constants and can be changed on demand.
Please note that the apparent size of the badge does not change when the
resolution is changed. However, the badge appears to be larger when the figure
size is made smaller.

In the two following plots with different resolution, the badges take the same fraction
of the canvas.
<!-- append example.py -->
```python3
plt.plot(x, y)
atlasify("Internal")
plt.savefig("test_5.png", dpi=72)
plt.savefig("test_6.png", dpi=300)
```

<!-- append example.py
```python
plt.clf()
```
-->

![ATLAS style plot](https://gitlab.cern.ch/fsauerbu/atlasify/-/jobs/artifacts/master/raw/test_5.png?job=doxec)
![ATLAS style plot](https://gitlab.cern.ch/fsauerbu/atlasify/-/jobs/artifacts/master/raw/test_6.png?job=doxec)

When a smaller figure size is choose, the badge takes a larger fraction of the
canvas.
<!-- append example.py -->
```python3
plt.figure(figsize=(4,3))
plt.plot(x, y)
atlasify("Internal")
plt.savefig("test_7.pdf")
```

<!-- append example.py
```python
plt.savefig("test_7.png", dpi=300)
plt.clf()
```
-->

![ATLAS style plot](https://gitlab.cern.ch/fsauerbu/atlasify/-/jobs/artifacts/master/raw/test_7.png?job=doxec)


<!-- append example.py -->
```python
plt.figure(figsize=(4, 4))
heatmap = np.random.normal(size=(4, 4))

plt.imshow(heatmap)
atlasify("Internal", "Random heatmap, Outside badge", outside=True)
plt.tight_layout()
plt.savefig("test_8.pdf")
```

<!-- append example.py
```python
plt.savefig("test_8.png", dpi=300)
plt.clf()
```
-->

![ATLAS style plot](https://gitlab.cern.ch/fsauerbu/atlasify/-/jobs/artifacts/master/raw/test_8.png?job=doxec)





<!-- console
```
$ python3 example.py
```
-->



