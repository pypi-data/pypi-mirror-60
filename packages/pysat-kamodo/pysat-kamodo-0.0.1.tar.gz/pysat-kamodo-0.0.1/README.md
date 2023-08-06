# About

This project tracks development of the kamodo-pysat interface. While pysat focuses
on providing a unified way of retrieving, loading and cleaning instrument data,
Kamodo provides a math-oriented API for interpolation, function composition, 
and quick-look graphics. The combination of the two approaches simplifies 
the workflow for science users, while minimizing the effort needed for science discovery.

## Install

```console
pip install pysat-kamodo
```

## Usage

```python
pki = Pysat_Kamodo('2009, 1, 1', # Pysat_Kamodo allows string dates
                  platform = 'cnofs', # pysat keyword
                  name='vefi', # pysat keyword
                  tag='dc_b',# pysat keyword
                  )

pki.B_up().head()
```
```console
2009-01-01 00:00:00   -3984.774658
2009-01-01 00:00:01   -3966.702637
2009-01-01 00:00:02   -3951.631592
2009-01-01 00:00:03   -3936.454102
2009-01-01 00:00:04   -3921.183594
Name: B_up, dtype: float32
```


## Requirements

`pysat_kamodo` requires `pysat` and `kamodo`:
```console
pip install pysat
pip install kamodo
```

The following are needed for writing publication-ready graphics:

```console
conda install -c plotly plotly-orca
conda install psutil
```

To generate the documentation site:

```console
pip install mkdocs
pip install mknotebooks
pip install python-markdown-math
pip install markdown-include

mkdocs serve (from base directory)
```
