import sys
import os
import argparse
import datetime

from rivm.conversion.input import InputCSV
from rivm.conversion.builder import (
    AeriusRekenpunten,
    AeriusOverdrachtslijnen,
    AeriusWegvakkenSRM1,
    AeriusWegvakkenSRM2,
    AeriusMaatregelen,
    AeriusCorrecties,
)


def parse_args(args):
    """
    Parse command arguments required for this script.
    """
    parser = argparse.ArgumentParser(description='Bi-directional data conversion between NSL-Monitoring and Aerius') # noqa
    group = parser.add_mutually_exclusive_group(required=True)
    # Input
    group.add_argument("--rekenpunten", help='NSL-Monitoring rekenpunten.csv')
    group.add_argument('--wegvakken', help='NSL-Monitoring wegvakken.csv')
    group.add_argument('--maatregelen', help='NSL-Monitoring maatregelen.csv')
    group.add_argument('--correcties', help='NSL-Monitoring correcties.csv')
    # Output
    parser.add_argument('--destination', required=True, help="Destination for converted CSV") # noqa
    return parser.parse_args()


def main(argv=sys.argv):
    args = parse_args(argv)
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    AERIUS_REKENPUNTEN = f'AERIUS_REKENPUNTEN_{timestamp}.csv'
    AERIUS_WEGVAKKEN_SRM1 = f'AERIUS_WEGVAKKEN_SRM1_{timestamp}.csv'
    AERIUS_WEGVAKKEN_SRM2 = f'AERIUS_WEGVAKKEN_SRM2_{timestamp}.csv'
    AERIUS_MAATREGELGEBIEDEN = f'AERIUS_MAATREGELGEBIEDEN_{timestamp}.csv'
    AERIUS_CORRECTIES = f'AERIUS_CORRECTIES_{timestamp}.csv'
    AERIUS_OVERDRACHTSLIJNEN = f'AERIUS_OVERDRACHTSLIJNEN_{timestamp}.csv'

    if args.rekenpunten:
        input_csv = InputCSV(args.rekenpunten, primary_key='receptorid')
        # Rekenpunten
        destination = os.path.join(args.destination, AERIUS_REKENPUNTEN)
        result = AeriusRekenpunten(input_csv).build()
        result.to_csv(destination, sep=';', index=False)
        # Overdrachtslijnen
        destination = os.path.join(args.destination, AERIUS_OVERDRACHTSLIJNEN)
        result = AeriusOverdrachtslijnen(input_csv).build()
        result.to_csv(destination, sep=';', index=False)

    elif args.wegvakken:
        input_csv = InputCSV(args.wegvakken, primary_key='receptorid')
        # Wegvakken SRM1
        destination = os.path.join(args.destination, AERIUS_WEGVAKKEN_SRM1)
        result = AeriusWegvakkenSRM1(input_csv).build()
        result.to_csv(destination, sep=';', index=False)
        # Wegvakken SRM2
        destination = os.path.join(args.destination, AERIUS_WEGVAKKEN_SRM2)
        result = AeriusWegvakkenSRM2(input_csv).build()
        result.to_csv(destination, sep=';', index=False)

    elif args.maatregelen:
        input_csv = InputCSV(args.maatregelen, primary_key='maatr_id')
        # Maatregelen
        destination = os.path.join(args.destination, AERIUS_MAATREGELGEBIEDEN)
        result = AeriusMaatregelen(input_csv).build()
        result.to_csv(destination, sep=';', index=False)

    elif args.correcties:
        input_csv = InputCSV(args.correcties, primary_key='correctie_id')
        # Correcties
        destination = os.path.join(args.destination, AERIUS_CORRECTIES)
        result = AeriusCorrecties(input_csv).build()
        result.to_csv(destination, sep=';', index=False)
