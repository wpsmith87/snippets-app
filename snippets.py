import logging
import argparse
import psycopg2


# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")



# Stubs

def put(name, snippet):
    """Store a snippet with an associated name."""
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    cursor = connection.cursor()
    try:
        command = "insert into snippets values (%s, %s)"
        cursor.execute(command, (name, snippet))
    except psycopg2.IntegrityError as e:
        connection.rollback()
        command = "update snippets set message=%s where keyword=%s"
        cursor.execute(command, (snippet, name))
    
    return name, snippet
    
def get(name):
    """Retrieve the snippet with a given name.
    If there is no such snippet, return '404: Snippet Not Found'.
    Returns the snippet.
    """
    logging.info("Retrieving snippet {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        row = cursor.fetchone()  # Have to assign return value to variable
    logging.debug("Snippet retrieved successfully.")
    if not row: # No snippet was found with that keyword name
        return "404: Snippet not found"
    else:
        return row[0]  
        
def catalog():
    """ Return a list of available keywords."""
    
    logging.info("Retrieving keywords")
    with connection, connection.cursor() as cursor:
        cursor.execute("select * from snippets order by keyword")
        rows = cursor.fetchall()
    logging.debug("Keywords retrieved successfully")
    names = [x[0] for x in rows]
    return names
        
def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    
    # Subparser for get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help = "Return a snippet")
    get_parser.add_argument("name", help = "Name of the snippet")
    
    # Subparser for catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help = "Return all keywords")
    
    arguments = parser.parse_args()
    
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")
    
    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet,name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":
        keywords = catalog()
        print ("Available keywords: {!r}".format(keywords))

if __name__ == "__main__":
    main()
    