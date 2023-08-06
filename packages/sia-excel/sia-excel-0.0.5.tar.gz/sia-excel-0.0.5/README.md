# sia-excel
SIA customization on top of a python excel writer

## Installation
_TO DO..._

## Usage
```python
import pandas as pd
import sia_excel as excel # I doubt this would create a naming conflict as far as I know

wb = excel.Workbook(file_path)

table = pd.DataFrame({'col1': [0, 1], 'col2': [2, 3]})

wb.write(
    data=table, 
    ws_name='excel_export'
    node="A2", 
    index=True, 
)
```
