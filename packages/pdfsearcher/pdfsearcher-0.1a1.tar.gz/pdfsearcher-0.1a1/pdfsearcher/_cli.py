import os
import click
from pdfsearcher._pdf_searcher import search_string_in_files

@click.command()
@click.argument("match_string", type=str)
@click.argument("files", type=click.Path(True), nargs=-1)
def cli(match_string, files):
    '''
    Lists the pdf files from FILES that match the MATCH_STRING

    MATCH_STRING will be treated as a regular expression

    FILES is a list of pdf files or directories with pdf files
    '''
    search_string_in_files(match_string, files)
    
