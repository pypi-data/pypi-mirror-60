# BCP

< badges will go here >

**This is a python utility that allows users to import/export data to/from a database.**

---

# Overview

This library began as a wrapper around SQL Server's BCP utility. It makes some assumptions
about parameters to simplify the interface and allow the user to work natively in python.
Though it currently supports MSSQL, there are plans to extend support to other database dialects.

# Requirements

- Python 3.6+

This library purposely requires no python packages outside of the standard library, beyond testing and documentation
needs. The intention is to maintain this status. However, you will need to have the appropriate command line utilities
installed for the specific database dialects with which you'll interact. For example, if your database is a MS SQL
SERVER instance, you'll need BCP installed. Consult the table below for further documentation, including download files
and instructions.

| RDBMS         | Utility | Documentation / Installation                           |
|:--------------|:--------|:-------------------------------------------------------|
| MS SQL Server | BCP     | https://docs.microsoft.com/en-us/sql/tools/bcp-utility |

# Installation

This library is still in development. So you'll have to build it from
source in the meantime. I'll soon get around to publishing it on pypi, 
in which case you'll be able to install it using `pip`

    pip install bcp

# Examples

Import data:
```python
import bcp

conn = bcp.Connection(host='HOST', driver='mssql', username='USER', password='PASSWORD')
my_bcp = bcp.BCP(conn)
file = bcp.DataFile(file_path='path/to/file.csv', delimiter=',')
my_bcp.load(input_file=file, table='table_name')
```

Export data:
```python
import bcp

conn = bcp.Connection(host='HOST', driver='mssql', username='USER', password='PASSWORD')
my_bcp = bcp.BCP(conn)
file = bcp.DataFile(file_path='path/to/file.csv', delimiter=',')
my_bcp.dump(query='select * from sys.tables', output_file=file)
```

# Full Documentation

For the full documentation, please visit: https://bcp.readthedocs.io/en/latest/
