# `notebookquery`: SQL integration and table display for IPython notebooks

Install with `pip`:

```bash
pip install notebookquery
```

Then just import into a notebook:

```python
import notebookquery
```

From there you can choose a database with `%db` at the start of a cell, for instance:

```python
%db postgresql:///example
```

Then write a query with `%%sql`:

```python
%%sql

select * from example_table;
```

