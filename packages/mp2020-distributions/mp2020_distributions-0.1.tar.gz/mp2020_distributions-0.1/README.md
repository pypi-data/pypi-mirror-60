# mp2020_distributions Package

mp2020_distributions is a Python library for working with Binomial and Gaussian distributions.
The development and upload of this package was completed in conjunction with the Udacity Data Science Nanodegree program taken Jan 2020.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install mp2020_distributions.

```bash
pip install mp2020_distributions
```

## Usage

```python
from Gaussiandistribution import Gaussian

distribution = Gaussian() #Instantiate distribution
distribution.read_data_file('data.txt') #reads in single column of data from a txt file
distribution.plot_histogram_pdf() #plots a pdf histogram from the data provided

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)