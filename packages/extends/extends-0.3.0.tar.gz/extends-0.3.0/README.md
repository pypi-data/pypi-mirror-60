# extends
A simple Python library that adds a decorator which helps extend functionality of classes by new methods without inheriting them

# Example
```python3
from dataclasses import dataclass
from typing import List
from extends import extends


@dataclass
class Student:
    name: str
    marks: List[int]


@extends(Student)
def avg(self: Student) -> float:
    return sum(self.marks) / len(self.marks)

```
