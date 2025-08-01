# Smileyfix

A Python library that makes Python easier and more fun to use.

## Features

- Automatically concatenates text and numbers with `+`
- Converts `input()` to numbers if possible
- Functions that end with `print()` will return the printed value
- Differentiates between `True` and `1`, `False` and `0`
- Differentiates between `None` and the string `"None"`
- Automatically imports `time`, `math`, and `random`
- Helper functions to read and write files

## Installation

```
pip install smileyfix
```

## Usage

```python
import smileyfix

a = input("Write something: ")
b = input("Write something more: ")

print(a + b)

def hello():
    print("Hello!")

result = hello()
print(result)
```
