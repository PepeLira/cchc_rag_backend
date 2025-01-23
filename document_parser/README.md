# Alembic + SQLAlchemy Project

This project demonstrates how to use SQLAlchemy ORM models together with Alembic migrations. It includes a small CLI (using IPython) to interact with the database and perform queries or other operations.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Database Setup](#database-setup)
4. [Migrations](#migrations)
5. [CLI Usage](#cli-usage)
6. [Troubleshooting](#troubleshooting)

---

## Requirements

- Python 3.7+
- [pip](https://pip.pypa.io/en/stable/installation/) (for installing Python dependencies)
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (recommended, but not mandatory)

---

## Installation

First cd on the document parser directory:
``` bash
  cd ./document_parser
```

**(Optional) Create and activate a virtual environment:**
``` bash
  python -m venv venv
  source venv/bin/activate  # On Linux/Mac
```

or
``` bash
  venv\Scripts\activate     # On Windows

```

**Install dependencies:**

``` bash
  pip install -r requirements.txt
```

## Database Setup
By default, this project uses an SQLite database. You can customize the database URL in the Alembic configuration file (usually in alembic.ini) or in your 
database.py. If you're using SQLite, the default behavior will create a file (e.g., app.db) in your project directory once migrations are applied.

Initialize the database: Make sure there's no existing old DB, **Only!** if you want a fresh start:

``` bash
rm -f ./db/parser_database.db  # or any .db file you're using
```
Run migrations:

``` bash
alembic upgrade head
```
This will apply all existing migrations up to the latest.

## Migrations
The project uses Alembic to handle database schema changes. Below are the main commands you’ll need.

Creating a new migration
Whenever you modify the SQLAlchemy models (e.g., add a new column), you should generate a new Alembic revision:

``` bash
alembic revision --autogenerate -m "Add new column to Chunk"
```
This command will create a new file inside the migrations/versions directory. Edit that file if necessary to correctly reflect the schema changes (Alembic will try to autogenerate them if configured to do so).

**Applying migrations**
To apply all your migrations (up to the latest) to the database:

``` bash
alembic upgrade head
```
This ensures your database schema is up-to-date with your latest models.

**Downgrading**
If you need to revert the last migration, you can use:

``` bash
alembic downgrade -1
```
You can replace -1 with a specific version ID if you want to go back to a particular revision.

## CLI Usage
This project provides a small CLI that starts an IPython shell with pre-imported objects (e.g., session, controller, Document, Chunk, Tag). This makes it easy to query the database and run custom commands.

**Start the CLI:**
``` bash
python -m src.parser_cli
```
or if there's a dedicated script (e.g., cli.py), you might run:

Available objects in the shell:

session: A SQLAlchemy Session object (for direct queries).
controller: An instance of DocumentController which may have helper methods for handling Document logic.
Document, Chunk, Tag: Your SQLAlchemy ORM models.
Example usage:

``` Python
In [1]: session.query(Document).all()
Out[1]: [<Document(id=1, title='Sample Doc')>, <Document(id=2, title='Another Doc')>]

In [2]: controller.create_document(title="My New Document", doc_path="/path/to/doc", output_dir="/path/to/output")
Out[2]: <Document(id=3, title='My New Document')>

In [3]: exit
```

## Troubleshooting
Permission errors on SQLite file: If you get permission issues, ensure the file is not locked by another process or that you have write permissions in the directory.
Missing Alembic commands: Make sure you installed Alembic inside your virtual environment. You can verify installation with pip show alembic.
Contributing
Feel free to open issues or create pull requests if you find improvements or bugs. Any help is appreciated!