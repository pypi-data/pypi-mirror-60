# Readme

## Status

ncbi-taxonomist is still under development. The basic operations are working
and unlikely to change in the near future. Metadata querying is still in
development.

## Synopsis

ncbi-taxonomist handles and manages phylogenetic data from NCBI. It can:
  - map between taxids and names
  - resolve lineages
  - store obtained taxa and their data locally in a SQLite database
  - group taxa into user defined groups (locally)

taxonomist has several simple operations, e.g. map or import, which work
together using pipes, e.g. to populate a database, map will fetch data from
Entrez and print it to STDOUT while import reads the STDIN to populate a local
database. Taxonomic information is obtained from Entrez, but a predownloaded
database can be imported as well.

The true strength is to find and link related metadata from other Entrez
databases, e.g. fetching data for metagenomic data-sets for specific or
diverse group of organisms. It can store phylogenetic groups, e.g. all taxa
for a specific project, in a local database.

## Install

```$pip install ncbi-taxonomist --user```

This will fetch and install `ncbi-taxonomist` and its required dependencies
(see below) use for an user (no `root` required)

### Dependencies

`ncbi-taxonomist` has two dependencies:

  - `entrezpy`: to handle remote requests to NCBI's Entrez databases

    - https://gitlab.com/ncbipy/entrezpy.git
    - https://pypi.org/project/entrezpy/
    - https://doi.org/10.1093/bioinformatics/btz385


  - `taxnompy`: to parse taxonomic XML files from NCBI
    - https://gitlab.com/ncbipy/taxonompy.git
    - https://pypi.org/project/taxonompy/

These are libraries maintained by myself and rely solely on the Python standard
library. Therefore, `ncbi-taxonomist` is less prone to suffer
[dependency hell](https://en.wikipedia.org/wiki/Dependency_hell).

## Usage

**`ncbi-taxonomist <command> <options>`**

### Available commands

call without any command or option  to  get an overview of available commands.

`$ ncbi-taxonomist`

### Command help

To get the usage for a specific command, use:

`$ ncbi-taxonomist <command> -h`

For example, to see available options for the command `map`, use:

`$ ncbi-taxonomist map -h`.

## Output

`ncbi-taxonist` uses `JSON` as main output because I have no clue what you want
to do with the result. `JSON` allows to use or write quick formatter or viewers
and read the data directly from `STDIN`.

[`jq`](https://stedolan.github.io/jq/) is an excellent tool to filter and
manipulate `JSON` data.

An example how to extract attributes from the `ncbi-taxonomist map` command
`JSON` output:

```
ncbi-taxonomist map -t 2 -n human -r | # ncbi-taxonomist map step
jq -r '[.taxon.taxon_id,.taxon.rank, ( .taxon.names | to_entries[] | select(.value=="scientific_name").key) ]  |   @csv'
       ^  ^               ^          ^              ^              ^                                        ^  ^   ^
       |  |               |          |            jq pipe        jq pipe                                    |  |   |
       |  +-------+-------+          +----------------------------------------------------------------------+  jq  |
       |  Add taxon_id and                Extract scientific_name from taxon names and add to array         | pipe |
       |  rank attribute to                                                                                 |     jq csv output
       |         array                                                                                      |     from array
       |                                                                                                    |
       `- create array for csv output for each JSON output line---------------------------------------------+
```

For more `jq` help, please refer to:

  - [`jq` manual](https://stedolan.github.io/jq/manual/)
  - [Matthew Lincoln, "Reshaping JSON with jq," The Programming Historian 5 (2016)](https://programminghistorian.org/en/lessons/json-and-jq)


## Commands

### map

map taxonomic information from Entrez phylogeny server or loading a downloaded
NCBI Taxonomy database into a local database. Returns taxonomic nodes in `JSON`.

#### Map taxid and names remotely

`ncbi-taxonomist map -t 2 -n human -r`

#### Map taxid and names from local database

`ncbi-taxonomist map -t 2 -n human -db taxa.db`

#### Map sequence accessions

`ncbi-taxonomist map -t 2 -n human -db taxa.db`

#### Format specific filed from map output to csv using `jq`

- Extract  taxid, rank, and scientific name from `map` `JSON` output using `jq`:

```
ncbi-taxonomist map -t 2 -n human -r | \
jq -r '[.taxon.taxon_id,.taxon.rank,(.taxon.names|to_entries[]|select(.value=="scientific_name").key)]|@csv'
```

### import

Importing stores taxa in a local SQLite database. The taxa are fetched remotely.

#### Import taxa

```
ncbi-taxonomist map -t 2 -n human -r  | ncbi-taxonomist import -db testdb.sql
```

### Resolve

Resolves lineages for names and taxids. The result is a `JSON` array with the taxa
defining the lineage in ascending order. This guarnatees the query is the  first
element in the array.

Further extraction can be done via a script reading `JSON` arrays line-be-line or
via othe tools, e.g. `jq` [REF]

#### Resolve and format via `jq`

```
ncbi_taxonomist resolve  -n man  -db testdb2.sql |  \
jq -r  '[.[] |  .names.scientific_name ]| @tsv'

```

#### Resolve accessions remotely

```
ncbi-taxonomist map  -a MH842226.1 NQWZ01000003.1 -r | ncbi-taxonomist resolve -m -r

```
### Extract

Extract nodes from a specified superkingdom and subtree
WIP

### Group **WIP**

Collect NCBI taxids into a group for later use
