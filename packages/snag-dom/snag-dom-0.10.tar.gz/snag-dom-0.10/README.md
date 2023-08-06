# snag-dom

A simple Python project to make accessing HTML elements easier; really more of an experiment than a full-fledged project.


It is recommended that you create a virtual environment before installing.

`pip install virtualenv`

`virtualenv ev`

`source ev/bin/activate`


Then install snag-dom.

`pip install snag-dom`


To use, simply call `S` with the CSS selector and the URL you intend to select elements from.

```python
from snag_dom import S
header = S('h1', 'http://www.example.com')[0]
print(header)
```
