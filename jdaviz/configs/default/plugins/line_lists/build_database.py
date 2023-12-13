import csv
import importlib.resources
import json
import sqlite3 as sql

def create_linelist_database():
    database_file = importlib.resources.files("jdaviz").joinpath("data/linelists/spectral_lines.sqlite")
    conn = sql.connect(database_file)
    cur = conn.cursor()

    # Create the tables we want in the database
    # Main line list table
    stmt = ("CREATE TABLE IF NOT EXISTS spectral_lines ("
            "id INTEGER PRIMARY KEY,"
            "name TEXT NOT NULL,"
            "rest_value REAL NOT NULL,"
            "medium_id INTEGER NOT NULL,"
            "citation_id INTEGER,"
            "rest_unit_id INTEGER NOT NULL,"
            "FOREIGN KEY (medium_id) REFERENCES media (id),"
            "FOREIGN KEY (citation_id) REFERENCES citations (id),"
            "FOREIGN KEY (rest_unit_id) REFERENCES units (id)"
            ")")

    cur.execute(stmt)

    # Small table for vacuum vs air
    stmt = ("CREATE TABLE IF NOT EXISTS media ("
            "id INTEGER PRIMARY KEY, medium TEXT UNIQUE NOT NULL)")
    cur.execute(stmt)

    # Table to store units
    stmt = ("CREATE TABLE IF NOT EXISTS units ("
            "id INTEGER PRIMARY KEY, unit TEXT UNIQUE NOT NULL)")
    cur.execute(stmt)

    # Table to store citation/metadata information
    stmt = ("CREATE TABLE IF NOT EXISTS citations ("
            "id INTEGER PRIMARY KEY, citation TEXT UNIQUE NOT NULL)")
    cur.execute(stmt)

    # Loop through existing line lists, adding the line data to the database
    # Read metadata file
    metadata_file = importlib.resources.files("jdaviz").joinpath("data/linelists/linelist_metadata.json")
    with open(metadata_file, "r") as f:
        linelist_metadata = json.load(f)

    stmt = "INSERT OR IGNORE INTO units (unit) values ('micron'), ('Angstrom')"
    cur.execute(stmt)
    stmt = "INSERT OR IGNORE INTO media (medium) values ('air'), ('vacuum')"
    cur.execute(stmt)

    print("Loading line lists")
    for listname, values in linelist_metadata.items():
        # Add citation
        citation = values["Citations/Notes"]
        unit = values['units']
        try:
            medium = values['medium']
        except KeyError:
            medium = "unknown"
        stmt = f"INSERT OR IGNORE INTO citations (citation) values ('{citation}')"
        cur.execute(stmt)
        # Get linked IDs for line inserts
        citation_id = cur.execute(f"SELECT id from citations where citation='{citation}'").fetchone()
        unit_id = cur.execute(f"SELECT id from units where unit='{unit}'").fetchone()
        medium_id = cur.execute(f"SELECT id from media where medium='{medium}'").fetchone()

        # Read linelist file and insert rows into spectral_lines table
        fbase = values['filename_base']
        fname = importlib.resources.files("jdaviz").joinpath(f"data/linelists/{fbase}.csv")
        line_names = []
        line_rests = []
        with open(fname, "r") as f:
            freader = csv.reader(f)
            next(freader, None)  # skip the headers
            for row in freader:
                line_names.append(row[0])
                line_rests.append(row[1])
        unit_ids = (unit_id,)*len(line_names)
        medium_ids = (medium_id,)*len(line_names)
        citation_ids = (citation_id,)*len(line_names)
        stmt = ("INSERT OR IGNORE INTO spectral_lines (name, rest_value, medium_id, "
                f"citation_id, rest_unit_id) values {tuple(line_names)}, {tuple(line_rests)}"
                f" {medium_ids}, {citation_ids}, {unit_ids}")
        cur.execute(stmt)


    conn.commit()
    cur.close()
    conn.close()