DATE_FORMAT = '%Y%m%d'

"""
This is a utility script to transform the data found at:
https://www.data.gouv.fr/fr/datasets/fichier-des-personnes-decedees/

When run, will operate on all files located in the 'source_data' directory.
For each file, will generate:
- an output file containg transformed data: (date of death, sex, age, geographical code)
- an error file with all the input lines that couldn't be parsed.

to use on command line, from script directory: python process-french-deaths.py 
"""

def determine_age(raw_dob, raw_dod):
    date_of_birth = parse_tolerant_of_errors(raw_dob)
    date_of_death = parse_tolerant_of_errors(raw_dod)
    from dateutil.relativedelta import relativedelta
    age = relativedelta(date_of_death, date_of_birth)
    return age.years + age.months / 12


def parse_tolerant_of_errors(raw_date):
    try:
        return parse(raw_date)
    except ValueError:
        if month_is_not_set(raw_date):
            if day_is_not_set(raw_date):
                return parse(raw_date[0:4] + "0101")
            else:
                return parse(raw_date[0:6] + "01")
        else:
            raise ValueError("couldn't parse %s" % raw_date)


def parse(raw_date):
    from datetime import datetime
    return datetime.strptime(raw_date, DATE_FORMAT)


def day_is_not_set(raw_date):
    return raw_date[4:6] == "00"


def month_is_not_set(raw_date):
    return raw_date[6:8] == "00"


def parse_line(line):
    sex = line[80]
    dob = line[81:89]
    dod = line[154:162]
    age_in_years = determine_age(dob, dod)
    geographic_code_at_death = line[162:167]
    return dod, sex, age_in_years, geographic_code_at_death


def serialise(record):
    (dod, sex, age_in_years, geographic_code_at_death) = record
    return "%s,%s,%.1f,%s\n" % (dod, sex, age_in_years, geographic_code_at_death)


def process_file(input_path, output_path, error_path):
    processed_count = 0
    error_count = 0
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as output_file, \
            open(error_path, "w") as error_file, \
            open(input_path, "r", errors='replace') as input_file:
        for line in input_file:
            try:
                data = parse_line(line)
                output_file.write(serialise(data))
                processed_count += 1
            except ValueError as e:
                print(e)
                error_file.write(line)
                error_count += 1
    print("processed %s.\n\tcount=%d\terrors=%d" % (input_path, processed_count, error_count))

    # remove opened error file if there were no errors.
    if os.stat(error_path).st_size == 0:
        os.remove(error_path)


def process_files(source_path, output_path):
    from os import walk
    (_, _, filenames) = next(walk(source_path))
    for filename in filenames:
        process_file(source_path + "/" + filename,
                     output_path + "/processed-" + filename,
                     output_path + "/errors-" + filename)


print("starting to process")
source_data_path = './source_data'
output_path = 'output'
process_files(source_data_path, output_path)
print("finished processing")