# Topsis
##### by Ramneet Singh
#
#
#
##### Python package to calculate  performance score of different models and their ranks.

## Usage
```python
from topsis34.topsis import topsis
obj = topsis.Topsis("data.csv","2.5,3,5,3.5","+,-,+,+")    # (filename,weights,impacts)
obj.calculate_print_rank()                                 # calculate and prints rank
```
#### or

##### Type in your terminal
#
```sh
$ topsis34 <file_name> <weights> <impacts>
```
example:

```sh
$ topsis34 data.csv "2.5,3,5,3.5" "+,-,+,+"
```
