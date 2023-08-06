import click

from .commands import to_csv, to_xml, to_xlsx


@click.group()
def main():
    """
    Can convert 1 invoice to xml or a directory of invoices to csv.
    """
    pass


main.add_command(to_xml.to_xml)
main.add_command(to_csv.to_csv)
main.add_command(to_xlsx.to_xlsx)

if __name__ == "__main__":
    main()
