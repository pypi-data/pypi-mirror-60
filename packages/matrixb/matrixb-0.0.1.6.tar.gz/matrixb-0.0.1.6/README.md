[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# matrixb

matrixb is a Python library to provide a single interface to handle common data input, cleaning, and analysis features for data science datasets. The name MatrixB arise from a play on several interpretations - *Matrix, Beta* (Experimental tools to use with matrices) and *Matrix, Version B* (Enhancements on 2-D matrix processing).

In general, you might consider matrixb as occupying a middlespace between the speed and efficiency of using native 2-D array matrices in Python and sophisticated statistical datastructures such as dataframes in Pandas and R. It provides a singular interface to load in csv, xls, xlsx, and ods files, automatically cleans common mistakes (accidentally adding a space to the end of a text string, or changing the capitalization structure of column names between two different data files) and allows tremendous flexibility in programmer-assisted cleaning and analysis, in part by leveraging the tools in the *[pydatacleaner](https://libraries.io/pypi/pydatacleaner)* package. If you need more functionality than matrixb, you likely should be using Pandas. There isn't a lot of overhead in matrixb (at least that can't be eliminated with a switch passed into the constructor), and so if it is too heavy for you, you probably need to custom write your own processing.

## Distribution
* [GitLab Project](https://gitlab.com/krcrouse/matrixb)
* [PyPI Distribution Page](https://pypi.org/project/matrixb)
* [Read the Docs Full API Documentation](https://matrixb.readthedocs.io)


## Project Status

Currently, matrixb is functional but shallowly vetted condition and should be considered **alpha** software. Some features that were implemented in the past may have been broken with more recent refactoring, and test coverage is still limited. Your mileage may vary.

Code comments of *NOTE* and *TODO* indicate known shortcomings that may be useful to you. The interface will likely change in future versions.

If you wish to rely on features of this package, I am likely more than willing to accommodate and to incorporate sensible design improvements or, in some cases, changes.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install matrixb.

```bash
pip install matrixb
```

## Usage

Many examples of usage are available in the main test files included in the t/ subdirectory.

```python
import matrixb

**EXAMPLES coming soon**
```

## Contributing
Contributions are collaboration is welcome. For major changes, please contact me in advance to discuss.

Please make sure to update tests for any contribution, as appropriate.

## Author

[Kevin Crouse](mailto:krcrouse@gmail.com). Copyright, 2019.

## License
[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)
