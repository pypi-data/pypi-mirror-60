import os
import csv
from operator import itemgetter
from concurrent.futures import ThreadPoolExecutor as Executor
from pathlib import Path

import click
from filetype import guess

from ..services.requests import extract_invoice
from .commons import read_pdf


def convert_to_csv(path, token, extractor_endpoint, workers):
    types = ("*.pdf", "*.tif", "*.tiff", "*.png", "*.jpg")
    file_count = 0
    fieldnames = set()
    result = {}

    with Executor(max_workers=workers) as exe:
        for file_type in types:
            full_path = os.path.join(os.getcwd(), path)
            files = Path(full_path).rglob(file_type)
            jobs = [
                exe.submit(
                    extract_invoice,
                    read_pdf(str(filename)),
                    extractor_endpoint,
                    guess(str(filename)).mime,
                    token,
                )
                for filename in files
                if guess(str(filename)).mime
            ]
            label = f"Converting {len(jobs)} invoices with {file_type} extension"
            with click.progressbar(jobs, label=label) as bar:
                for id, job in enumerate(bar):
                    file_path, response = job.result()
                    result[file_count] = flatten_invoice(response)
                    result[file_count]["file_path"] = file_path
                    [
                        fieldnames.add(fieldname)
                        for fieldname in result[file_count].keys()
                    ]
                    file_count += 1

    if not result:
        quit(f"No files of extension: {types} found in path")

    processed_dir_name = os.path.normpath(path).split(os.path.sep)[-1]

    with open(f"{processed_dir_name}.csv", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(fieldnames, key=itemgetter(0, -1)))
        writer.writeheader()

        for row in result:
            writer.writerow(result[row])


def flatten_invoice(invoice):
    return_dict = {}

    def traverse_items(entities, _dict):
        for entity, value in entities.items():
            if isinstance(value, dict):
                traverse_items(value, _dict)
            elif isinstance(value, list):
                for counter, list_item in enumerate(value):
                    temp_dict = {}
                    for item, value in list_item.items():
                        temp_dict[f"{entity}_{item}_{counter}"] = value
                    traverse_items(temp_dict, return_dict)
            else:
                _dict[entity] = str(value)

    traverse_items(invoice["entities"], return_dict)
    return return_dict
