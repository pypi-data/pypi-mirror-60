# rivm-conversion

- Installation:
```
$ pip install rivm
```

## Usage

### Convert CSV's to Aerius format:

- Aerius rekenpunten & overdrachtslijnen:
```
$ convert_to_aerius
    --rekenpunten=path/to/csv
    --destination=.
```

- Aerius wegvakken SRM1 & wegvakken SRM2:
```
$ convert_to_aerius
    --wegvakken=path/to/csv
    --destination=.
```

- Aerius maatregelen:
```
$ convert_to_aerius
    --maatregelen=path/to/csv
    --destination=.
```

- Aerius correcties:
```
$ convert_to_aerius
    --correcties=path/to/csv
    --destination=.
```

### Convert CSV's to NSL-Monitoring format:

- NSL Monitoring rekenpunten:
```
$ convert_to_nsl
    --rekenpunten=path/to/csv
    --overdrachtslijnen=path/to/csv
    --destination=.
```

- NSL Monitoring rekenpunten:
```
$ convert_to_nsl
    --wegvakken_srm1=path/to/csv
    --wegvakken_srm2=path/to/csv
    --destination=.
```
