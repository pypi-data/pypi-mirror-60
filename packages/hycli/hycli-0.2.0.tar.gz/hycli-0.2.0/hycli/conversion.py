import os
import csv
from operator import itemgetter
from concurrent.futures import ThreadPoolExecutor as Executor
from pathlib import Path

import xmltodict
import click
import xlsxwriter
from filetype import guess

from .services.requests import extract_invoice, validate_vat, validation
from .commons import read_pdf


def convert_to_xlsx(path, token, extractor_endpoint, workers):
    types = ("*.pdf", "*.tif", "*.tiff", "*.png", "*.jpg")
    file_count = 0
    fieldnames = set()
    result = {}
    workbook = xlsxwriter.Workbook("example.xlsx")

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
                    result[file_count]["file_path"] = file_path.split("/")[-1]
                    [
                        fieldnames.add(fieldname)
                        for fieldname in result[file_count].keys()
                    ]
                    file_count += 1

    single_cardinality = {}
    single_fieldnames = set()
    multi_cardinality = {}
    multi_fieldnames = set(["row_number", "file_path"])

    for idx, invoice in result.items():
        single_item = {}
        multi_item = {}

        for col, value in invoice.items():
            if col[-1].isdigit():
                num = int(col.split("_")[-1]) + 1
                label = "_".join(col.split("_")[:-1])
                if num not in multi_item:
                    multi_item[num] = {"row_number": num}

                multi_item[num][label] = value
                multi_fieldnames.add(label)
                if "file_path" not in multi_item[num]:
                    multi_item[num]["file_path"] = invoice["file_path"]
            else:
                single_item[col] = value
                single_fieldnames.add(col)

        single_cardinality[idx] = single_item
        multi_cardinality[idx] = multi_item

    workbook = xlsxwriter.Workbook("example.xlsx")
    workbook.add_worksheet("single_cardinality")
    worksheet = workbook.get_worksheet_by_name("single_cardinality")

    for idx, row in single_cardinality.items():
        count = 0
        for col in single_fieldnames:
            if col in row.keys():
                worksheet.write(0, count, col)
                worksheet.write(idx + 1, count, row[col])
            count += 1

    workbook.add_worksheet("multi_cardinality")
    worksheet = workbook.get_worksheet_by_name("multi_cardinality")

    item_count = 1
    for idx, row in multi_cardinality.items():
        for row_number, row_item in row.items():
            count = 0
            for key, value in row_item.items():
                worksheet.write(0, count, key)
                worksheet.write(item_count, count, value)
                count += 1
            item_count += 1

    workbook.close()


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

    with open("example.csv", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(fieldnames, key=itemgetter(0, -1)))
        writer.writeheader()

        for row in result:
            writer.writerow(result[row])


def convert_to_xml(
    path,
    output_path,
    extractor_endpoint,
    vat_validator_endpoint=None,
    validation_endpoint=None,
    token=None,
):
    result = {}
    _, pdf = read_pdf(path)

    # Extraction
    _, result["invoiceExtractor"] = extract_invoice(
        (path, pdf), extractor_endpoint, "application/pdf", token
    )

    # Validation
    if validation_endpoint:
        validation(result, validation_endpoint)

    # Vat validation
    if vat_validator_endpoint:
        validate_vat(result, vat_validator_endpoint)

    merge_validation(result)
    clean_datastructure(result)

    file_name = path.split("/")[-1]
    file_name = file_name.split(".")[0]
    xmltodict.unparse(
        {"hypatosResults": result},
        output=open(f"{output_path}/{file_name}.xml", "w+"),
        pretty=True,
    )


def flatten_invoice(invoice):
    return_dict = {}

    def traverse_items(entities, _dict, *idx):
        for entity, value in entities.items():
            if isinstance(value, dict):
                _dict[entity] = {}
                traverse_items(entities[entity], _dict[entity])
            elif isinstance(entity, list):
                for counter, list_item in enumerate(entity):
                    temp_dict = {}
                    for item, value in list_item.items():
                        temp_dict[f"{entity}_{item}_{counter}"] = value
                    traverse_items(temp_dict, return_dict)
            else:
                _dict[entity] = str(entity)

    traverse_items(invoice["entities"], return_dict)
    return return_dict


def merge_validation(result):
    return_dict = {}

    def traverse_merge_items(entities, _dict, *validation):
        for entity, value in entities.items():
            if isinstance(value, dict):
                _dict[entity] = {}
                traverse_merge_items(
                    entities[entity],
                    _dict[entity],
                    validation[0][entity][0] if validation else None,
                )
            elif isinstance(value, list):
                _dict[entity] = []
                for idx in range(0, len(value)):
                    _dict[entity].append({})
                    traverse_merge_items(
                        entities[entity][idx],
                        _dict[entity][idx],
                        validation[0][entity][0][str(idx)][0]
                        if validation[0] and entity in validation[0]
                        else None,
                    )
            else:
                if validation[0] and entity in validation[0]:
                    # Entity was in validation schema and has errors
                    if str(validation[0][entity][0]) != "unknown field":
                        _dict[entity] = {
                            "@risk": create_risk(entity, validation[0][entity]),
                            "#text": str(value),
                        }
                    # Entity was not in validation schema
                    else:
                        _dict[entity] = {"#text": str(value)}
                else:
                    # Entity was in validation schema but no errors
                    _dict[entity] = {"@risk": "low", "#text": str(value)}

    traverse_merge_items(
        result["invoiceExtractor"]["entities"], return_dict, result["validation"]
    )
    result["invoiceExtractor"]["entities"] = return_dict


def clean_datastructure(result):
    result["invoiceExtractor"]["entities"]["lineItems"] = {}
    result["invoiceExtractor"]["entities"]["lineItems"]["item"] = result[
        "invoiceExtractor"
    ]["entities"]["items"]

    del (
        result["invoiceExtractor"]["entities"]["items"],
        result["invoiceExtractor"]["probabilities"],
        result["invoiceExtractor"]["infos"],
    )


def create_risk(entity, validation_errors):
    """ Create risk flag """
    err_amount = len(validation_errors)

    if err_amount == 0:
        return "low"
    elif err_amount == 1:
        return "med"
    else:
        return "high"
