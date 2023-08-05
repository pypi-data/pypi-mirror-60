# Python Avri API

Unofficial wrapper around the [Avri](https://avri.nl/) API, for automation purposes.

## Usage

Initialize the client with you `postal code` and `house number`. Optionally provide a `house_nr_extension` and/or a `country_code`.
```python
from avri.api import Avri
client = Avri('1234AB', 42)
```

Exposes the following functions:
- ```client.upcoming()``` returns first upcoming collecting day in a `Garbage` object
- ```client.upcoming_of_each()``` returns first upcoming collecting day for each garbage type in a `List[Garbage]` object
- ```client.all()``` returns all upcoming collecting days in a `List[Garbage]` object


### The `Garbage` object

Contains 
- `name`: The name of the garbage type, e.g. `plastic` or `gft`.
- `day`: A python datetime object representing the collecting date.

## In a long living process
Data is cached for `14` days before it's refreshed to reduce the number of API calls made.
