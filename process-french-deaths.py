# file_in = 'test.txt'
file_in = 'deces-2020-m02.txt'
file_out = 'french-deaths.txt'
DATE_FORMAT = '%Y%m%d'


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
        if (mont_is_not_set(raw_date)):
            if (day_is_not_set(raw_date)):
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


def mont_is_not_set(raw_date):
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


def process_file(filename):
    with open(filename, "r") as file:
        return [parse_line(line) for line in file]


def write_to_file(records, filename):
    with open(filename, "w") as file:
        for record in records:
            file.write(serialise(record))


print("starting to process")
data = process_file(file_in)
write_to_file(data, file_out)
print("processed %d lines" % len(data))


