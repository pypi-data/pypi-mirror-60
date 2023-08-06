# Towards a Taxonomy of Word Embedding Models: The Database

This repository contains the code that was used to collect relevant 
publications and store them in a Postgres Database.
You are welcome to reproduce our database!
Note however that the search results on Google Scholar may have been updated
since our publication, leading to slightly different results.

As a prerequisite, you must have set up a Postgres database with the proper 
database schema. To do this, you can execute our Postgres schema dump provided 
in `data/wem_taxonomy_schema.sql` with the `psql` shell:
```bash
psql dbname < data/wem_taxonomy_schema.sql
```
where `dbname` is the name of an empty database that you have already created 
for this purpose.
You must also create a user called 'taxonomist' who will own the created
tables. If you intend to use the database with our Use Case Collector (UCC)
tool later on, you should execute the above schema dump with a Postgres user 
who has root privileges.
The root privileges are needed to install the Postgres trigram extension (pg_trgm).

## Step 1a): Installing from PyPI

Simply execute
```bash
python3 -m pip install reproduce_wem_taxonomy
```
to install the needed packages.


## Step 1b): Installing from source

First, clone this repository. Then, from within the repository root directory,
pull in the `pubfisher` submodule:
```bash
git submodule update --remote lib/pubfisher
```
Now, install this module from source using pip:
```bash
python3 -m pip install -e lib/pubfisher
```
After that, you can install the `reproduce_wem_taxonomy` package as well:
```bash
python3 -m pip install -e .
```

## Step 2: Collecting the publications from Google Scholar

In order to finally collect the publications,
simply execute the module `fish_wem_taxonomy`:
```bash
python3 -m reproduce_wem_taxonomy.collect_relevant_publications
```

The publications are now stored in the database table 'publications' of
your previously created Postgres database.
