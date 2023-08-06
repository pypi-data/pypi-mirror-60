# jblib-pandas
## Author: Justin Bard

This module was written to minimize the need to write the pandas related functions I use often. These modules were stripped out of jblib to minimize the dependencies required to import jblib. I.E. Pandas

---
The source code can be viewed here: [https://github.com/ANamelessDrake/jblib-pandas](https://github.com/ANamelessDrake/jblib-pandas)

More of my projects can be found here: [http://justbard.com](http://justbard.com)

---

INSTALL:  ` python3 -m pip install jblib-pandas `

---
` from jblib-pandas import mean_deviation `

```
    DESCRIPTION:
        This function takes a Pandas DataFrame column in and then returns a series of calculated mean deviations

    FUNCTION:
        mean_deviation(data, mean=None)

    EXAMPLE:
        data["MeanDeviation"] = pd.Series(mean_deviation(data['column']), index=data.index)
```

---
` from jblib-pandas import standard_deviation `

```
    DESCRIPTION:
        This function takes a Pandas DataFrame column in and then returns the calculated standard deviation

    FUNCTION:
        standard_deviation(data, mean=None)

    EXAMPLE:
        standard_dev = standard_deviation(data['column'])
```