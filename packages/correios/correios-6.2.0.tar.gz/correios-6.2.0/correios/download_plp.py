import argparse
import sys

from .client import Correios

correios_client = Correios("solidarium2", "n2ai9g")


def cli():
    parser = argparse.ArgumentParser(description="Updates Correios WSDL files")
    parser.add_argument("numero", metavar="N", type=int, help="an integer for the accumulator")

    args = parser.parse_args()

    xml = correios_client._auth_call("solicitaXmlPlp", args.numero)
    with open(f"plp-{args.numero}.xml", "w") as f:
        f.write(xml)


if __name__ == "__main__":
    sys.exit(cli() or 0)
