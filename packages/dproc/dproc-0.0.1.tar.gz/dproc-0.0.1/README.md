# dproc
> A convenient data flow to preprocess data using metadata.


## Install

```python 
pip install dproc
````

## How to use

### Import

```python
from dproc import *
```

### Load the definition file
Load the data defintion from the location of your choice (locally, server, cloud).

```python 
dproc.meta.definition = pd.read_excel('your-data-definition-file')
````

This file contains all meta information such as 

In order to generate a specifc entity definition ...


```python
dproc.meta.entity = 'your-entity'
```

and then you can apply the dataflow steps:

```python 
entity_cleaned = (entity_raw
                  .step_rename_cols()
                  .step_replace_missing_with_nan()
                  .step_remove_not_needed_cols()
                  .step_remove_rows_with_missing_ids()
                  .step_remove_duplicate_rows()
                  .step_format_dates(cols=['created'])
                  .step_format_dates(cols=['modified'])
                  .step_format_round_numeric_cols(cols=['rating'], decimal_places=2)
                  .step_change_dtypes()
                 )
```
