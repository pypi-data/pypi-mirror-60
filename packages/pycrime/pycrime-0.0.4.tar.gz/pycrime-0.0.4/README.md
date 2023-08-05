# PyCrime

Fetch crime statistics from the ExpenseCheck crime statistics API.

## Installation

PyPi is the easiest:

``` bash
pip install pycrime
```

## Usage

Create a new API client with:

``` python
from pycrime import CrimeClient


client = CrimeClient(jwt=<your-token>)
```

Please replace `<your-token>` with your API token as a string.

Fetch crime statistics based on postcode with:

``` python
client.locality_statistics(3000)
```

Here, the postcode for Melbourne's CBD, 3000, has been used. Please
substitute for the postcode of interest.
