#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Seiran
# 
# Copyright 2015-2020 Matthew "garrick" Ellison.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

name = "seiran"
author = "gargargarrick"
__author__ = "gargargarrick"
__version__ = '1.5.0'
__copyright__ = "Copyright 2015-2019 Matthew Ellison"
__license__ = "GPL"
__maintainer__ = "gargargarrick"
__status__ = "Development"

import datetime, os, sys, argparse
import sqlite3
from appdirs import *
import seiran.ff_bkm_import
import seiran.onetab_bkm_import

def initBookmarks():
    """Check if a bookmarks database already exists."""
    try:
        c.execute('''CREATE TABLE bookmarks
            (title text,url text NOT NULL,date text,folder text,PRIMARY KEY(url))''')
        print("Database created.")
    except sqlite3.OperationalError:
        pass

def addBKM(title, url, folder):
    """
    Add a new bookmark to the database.

    Parameters
    ----------

    title : str
        The name of the new bookmark.
    url : str
        The new bookmark's Uniform Resource Locator. Must be unique.
    folder : str
        A category or folder for the new bookmark.
    """
    if title == None:
        title = input("Title? > ")
    if url == None:
        url = input("URL? > ")

    # I don't want to connect to the net to validate bookmarks (that's
    # what browsers are for) so this only looking the first few
    # characters and does absolutely no other checking or processing.
    # Checking is done to make opening bookmarks in the browser a bit
    # easier; feel free to take that part out if you don't want or need
    # this feature. I would recommend leaving in checking for empty
    # URLs, though.

    while url == "" or url[0:4] != "http":
        print("Sorry, that is empty or doesn't seem to be a URL. (Make sure your URL uses the HTTP or HTTPS protocol.)")
        url = input("URL? > ")
    # Add the current date
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    if folder == None:
        folder = input("Folder/Category? (can be left blank) > ")
    bkm = (title,url,date,folder,)

    # Frankly, I don't know how necessary SQL injection countermeasures
    # are for this specific program (what, are you going to inject your
    # OWN database?) but it always pays to be careful in my opinion.

    try:
        c.execute("INSERT INTO bookmarks VALUES (?,?,?,?)", bkm)
        print("Inserted.")
        conn.commit()
    ##I don't want users to end up with databases full of duplicated
    ## bookmarks by mistake, so URLs must be unique.
    except sqlite3.IntegrityError:
        print("Already exists.")
    except sqlite3.OperationalError:
        print("Operational error")

def delBKM(url):
    """
    Remove a bookmark from the database.

    Parameters
    ----------
    url : str
        The U.R.L. of the bookmark to be deleted.
    """
    if url == None:
        url = input("URL to delete? (Deleted bookmarks cannot be recovered!) > ")
    sq_url = (url,)
    c.execute("SELECT url FROM bookmarks WHERE url=?", sq_url)
    conn.commit()
    if len(c.fetchall()) >= 1:
        try:
            c.execute("DELETE FROM bookmarks WHERE url=?",url)
            conn.commit()
            print("DELETED!")
        except:
            ##Yeah, I got nothing.
            print("Unable to delete for unknown reasons.")
    else:
        print("No bookmark of {url} exists.".format(url=url))

def listBKMs():
    """
    List all bookmarks in the database. Spaces are included at the ends
    of lines such that the output can be interpreted as Markdown.
    """
    c.execute("SELECT * from bookmarks")
    print("# Seiran Bookmarks")
    template = "\nTitle: {title}  \n  URL: {url}  \n  Date: {date}  \n  Folder: {folder}"
    for i in c.fetchall():
        print(template.format(title=i[0], url=i[1], date=i[2], folder=i[3]))

def oneSearch(search_term, column):
    """
    Search a single field in the bookmark database.

    Parameters
    ----------
    search_term : str
        The phrase for which to search.
    column : str
        The field to search. Can be title, url, folder, or date.
    """
    sq_search_term = "%{search_term}%".format(search_term=search_term)
    t = (sq_search_term,)
    if column == "title":
        c.execute("SELECT * from bookmarks WHERE title LIKE ?",t)
    elif column == "url":
        c.execute("SELECT * from bookmarks WHERE url LIKE ?",t)
    elif column == "folder":
        c.execute("SELECT * from bookmarks WHERE folder LIKE ?",t)
    elif column == "date":
        c.execute("SELECT * from bookmarks WHERE date LIKE ?",t)
    result_list = c.fetchall()
    if result_list == []:
        print("No results.")
    else:
        print("\n# Seiran - Results for {column}: {search_term}".format(search_term=search_term, column=column))
        template = "\nTitle: {title}  \n  URL: {url}  \n  Date: {date}  \n  Folder: {folder}"
        for i in result_list:
            print(template.format(title=i[0], url=i[1], date=i[2], folder=i[3]))

def searchAll(search_term):
    """
    Search all fields in the bookmark database.

    Parameters
    ----------
    search_term : str
        The phrase for which to search.
    """
    sq_search_term = "%{search_term}%".format(search_term=search_term)
    t = (sq_search_term, sq_search_term, sq_search_term, sq_search_term,)
    results = []
    c.execute("SELECT DISTINCT * from bookmarks WHERE title LIKE ? OR url LIKE ? OR folder LIKE ? OR date LIKE ?",t)
    result_list = c.fetchall()
    for i in result_list:
        results.append(i)
    if results == []:
        print("No results.")
    else:
        print("\n# Seiran - {search_term}".format(search_term=search_term))
        template = "\nTitle: {title}  \n  URL: {url}  \n  Date: {date}  \n  Folder: {folder}"
        for i in results:
            print(template.format(title=i[0],url=i[1],date=i[2],folder=i[3]))

def editBKM(url,field,new):
    """
    Edit an existing bookmark.

    Parameters
    ----------
    url : str
        The U.R.L. of the target bookmark.
    field : str
        The field to be edited. Can be title or folder.
    new : str
        The new value for the edited field.
    """
    if url == None:
        url = input("Which URL do you want to edit? > ")
    sq_url = (url,)
    c.execute("SELECT * from bookmarks WHERE url = ?", sq_url)
    # error handling goes here
    you_found_it = False
    for row in c:
        print("\nCurrent bookmark data:")
        print("\nTitle: {title}\n  URL: {url}\n  Date: {date}\n  Folder: {folder}".format(title=row[0], url=row[1], date=row[2], folder=row[3]))
        you_found_it = True
    if you_found_it == False:
        print("Sorry, that doesn't seem to be a URL in the database. Try again.")
        return(False)
    if field == None:
        field = input("Which field do you wish to edit? (title/category/none)> ")
    if field == "folder":
        field = "category"
    if field not in ["title", "category"]:
        return
    if new == None:
        new = input("What should the new {field} be? > ".format(field=field))
        new = str(new)
    newBKM = (new,url)
    if field == "title":
        c.execute("UPDATE bookmarks SET title=? WHERE url=?",newBKM)
        conn.commit()
    elif field == "category":
        c.execute("UPDATE bookmarks SET folder=? WHERE url=?",newBKM)
        conn.commit()
    else:
        return
    print("\nUpdated bookmark.")
    c.execute("SELECT * from bookmarks WHERE url = ?", sq_url)
    for row in c:
        print("\nTitle: {title}\n  URL: {url}\n  Date: {date}\n  Folder: {folder}".format(title=row[0], url=row[1], date=row[2], folder=row[3]))

def getFirefoxBookmarks():
    """
    Import bookmarks from Mozilla-based browsers. (This is an
    experimental feature and may cause errors. Please back up your
    bookmark database before use.)
    """
    ## Grab the Firefox bookmarks.
    fmarks = seiran.ff_bkm_import.importDatabase()
    ## Add them to Seiran's database.
    for i in fmarks:
        bkm = (i[0], i[1], str(i[2]), i[3],)
        try:
            c.execute("INSERT INTO bookmarks VALUES (?,?,?,?)",bkm)
            conn.commit()
        except sqlite3.IntegrityError:
            print("Duplicate found. Ignoring {i}.".format(i=i[1]))
        except sqlite3.OperationalError:
            print("Operational error")
    print("Import complete!")
    return

def getOneTabBookmarks():
    """Import bookmarks from a OneTab text export."""
    omarks = seiran.onetab_bkm_import.importFromTxt()
    for i in omarks:
        bkm = (i[0], i[1], str(i[2]), i[3],)
        try:
            c.execute("INSERT INTO bookmarks VALUES (?,?,?,?)",bkm)
            conn.commit()
        except sqlite3.IntegrityError:
            print("Duplicate found. Ignoring {i}.".format(i=i[1]))
        except sqlite3.OperationalError:
            print("Operational error")
    print("Import complete!")
    return

def getSeiranBookmarks():
    """Import bookmarks from an existing Seiran database."""
    print("Warning! This is not well-tested and may ruin everything.")
    print("Back up your database before use!")
    seiran_file = input("Enter the path to the Seiran database you want to copy. > ")
    if seiran_file.lower() == "q":
        print("Import cancelled.")
        return
    sconn = sqlite3.connect(seiran_file)
    sc = sconn.cursor()
    attach_main = "ATTACH DATABASE ? as x"
    main_db_path = installToConfig()
    main_db = (main_db_path,)
    c.execute(attach_main,main_db)
    attach_branch = "ATTACH DATABASE ? as y"
    branch_db = (seiran_file,)
    c.execute(attach_branch,branch_db)
    c.execute("INSERT OR IGNORE INTO x.bookmarks SELECT * FROM y.bookmarks;")
    conn.commit()
    print("Import complete!")
    return

def exportBookmarks(format):
    """
    Export bookmark database to a file in the user data directory.

    Parameters
    ----------
    format : str
        The target output format. Can be txt or html.
    """
    c.execute("SELECT * from bookmarks")
    if format == "txt":
        ## Using the same format as [list]
        template = "Title: {title}  \n  URL: {url}  \n  Date: {date}  \n  Folder: {folder}\n"
    elif format == "html":
        template = "<p><a href={url}>{title}</a> ({folder}) [<time='{date}'>{date}</a>]</p>"
    bookmarks = []
    for i in c.fetchall():
        if i[0] == "" or i[0] == None or i[0] == "None":
            title=i[1]
        else:
            title = i[0]
        bookmarks.append(template.format(title=title, url=i[1], date=i[2], folder=i[3]))
    if format == "txt":
        bookmarks_write = "\n".join(bookmarks)
    elif format == "html":
        front_matter = ["<!DOCTYPE HTML>", "<html>", "<head>",
               "<title>Seiran Bookmarks</title>",
               """<meta charset="utf-8">""", "</head>", "<body>",
               "<h1>Seiran Bookmarks</h1>"]

        end_matter = ["</body>","</html>"]
        bookmarks_write = "\n".join(front_matter+bookmarks+end_matter)
    save_path = user_data_dir(name, author)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_name = "seiran_bookmarks_export_{date}.{format}".format(date=datetime.datetime.now().strftime("%Y-%m-%d"),format=format)
    bookmarks_out = os.path.join(save_path,file_name)
    with open(bookmarks_out,"w",encoding="utf-8") as f_out:
        f_out.write(bookmarks_write)
    print("Exported to {bookmarks_out}.".format(bookmarks_out=bookmarks_out))
    return

def cleanBKMs():
    """
    Perform basic housekeeping features on the bookmarks database.
    It checks for bookmarks without titles, then adds their U.R.L. as a
    title. It also lists bookmarks that have the same title, which may
    indicate duplicates.
    """
    c.execute("SELECT * from bookmarks")
    for i in c.fetchall():
        # Check for empty titles
        if i[0] == "" or i[0] == None or i[0] == "None":
            print("Bookmark {url} doesn't have a title. Adding URL as title.".format(url=i[1]))
            new_title = i[1]
            newBKM = (new_title,i[1],)
            c.execute("UPDATE bookmarks SET title=? WHERE url=?",newBKM)
            conn.commit()
    ## And this one checks for ones that might be duplicates.
    print("# Seiran Cleanup")
    c.execute("SELECT title, COUNT(*) c FROM bookmarks GROUP BY title HAVING c > 1;")
    result_list = c.fetchall()
    if result_list == []:
        print("No results.")
    else:
        template = """\n{count} bookmarks have the title "{title}":\n"""
        for i in result_list:
            print(template.format(title=i[0],count=i[1]))
            t = (i[0],)
            c.execute("SELECT url from bookmarks where title is ?",t)
            url_list = c.fetchall()
            ordinal = 1
            for u in url_list:
                print("{ordinal}. {url}".format(ordinal=str(ordinal), url=u[0]))
                ordinal += 1
    return

def installToConfig():
    """
    Create a Seiran folder in the user's data directory, and get the
    path to the bookmarks database within.

    Returns
    -------
    bookmarks_file : str
        The path to the active bookmarks.db file.
    """
    config_path = user_data_dir(name, author)
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    bookmarks_file = os.path.join(config_path,"bookmarks.db")
    return(bookmarks_file)

def main():
    """
    Set up the database and parse arguments.
    """
    global c
    global conn
    bookmarks_file = installToConfig()
    conn = sqlite3.connect(bookmarks_file)
    c = conn.cursor()
    initBookmarks()
    print("{name} by {author}, v.{version}.".format(name=name,author=__author__,version=__version__))

    parser = argparse.ArgumentParser(prog='seiran')
    subparsers = parser.add_subparsers(dest="command", help='Commands')
    parser_help = subparsers.add_parser("help", help="List commands")
    parser_add = subparsers.add_parser("add", help="Create a new bookmark.")
    parser_del = subparsers.add_parser("del", help="Remove a bookmark.")
    parser_list = subparsers.add_parser("list", help="Display all bookmarks in the database.")
    parser_search = subparsers.add_parser("search", help="Find specific bookmark(s).")
    parser_edit = subparsers.add_parser("edit", help="Change a bookmark's metadata.")
    parser_import = subparsers.add_parser("import", help="Add bookmarks from anothe system to the database.")
    parser_export = subparsers.add_parser("export", help="Save all bookmarks to a formatted file.")
    parser_clean = subparsers.add_parser("clean", help="Tidy up bookmark metadata.")
    parser_copyright = subparsers.add_parser("copyright", help="Show legal information.")

    parser_add.add_argument("-t", "--title", help="A bookmark's name. Usually appears in <h1> or <title> tags on the page.")
    parser_add.add_argument("-u", "--url", help="A bookmark's Universal Resource Locator. Must be unique.")
    parser_edit.add_argument("-u", "--url", help="A bookmark's Universal Resource Locator. Must be unique.")
    parser_del.add_argument("-u", "--url", help="The Universal Resource Locator of the bookmark you want to delete.")
    parser_add.add_argument("-c", "--category", help="A bookmark's category. This is inspired by Firefox's folders, but you can put almost anything here.")
    parser_search.add_argument("-f", "--field", help="The column you want to search. Available arguments are title, url, category, date, or all.")
    parser_edit.add_argument("-f", "--field", help="The column you want to edit. Available arguments are title or category.")
    parser_search.add_argument("-q", "--query", help="The term you want to search for.")
    parser_edit.add_argument("-n", "--new", help="The new value you want an edited field to have.")
    parser_import.add_argument("-i", "--importformat", help="The system you want to import bookmarks from. Available arguments are firefox, onetab, or seiran.")
    parser_export.add_argument("-x", "--exportformat", help="The format you want to export your bookmarks to. Available options are txt or html.")
    choice = parser.parse_args()

    if choice.command == "add":
        addBKM(choice.title, choice.url, choice.category)
    elif choice.command == "del":
        delBKM(choice.url)
    elif choice.command == "list":
        print("Listing all bookmarks...")
        listBKMs()
        return
    elif choice.command == "search":
        field = choice.field
        if field == None:
            field = input("  Which field? (title/url/category/date/all) > ")
        search_term = choice.query
        if search_term == None:
            search_term = input("  Search term? (case insensitive) > ")
        if field.lower() == "title":
            oneSearch(search_term,"title")
        elif field.lower() == "url":
            oneSearch(search_term,"url")
            return
        elif field.lower() == "category":
            oneSearch(search_term,"folder")
            return
        elif field.lower() == "date":
            oneSearch(search_term,"date")
        else:
            searchAll(search_term)
            return
    elif choice.command == "edit":
        editBKM(choice.url,choice.field,choice.new)
    elif choice.command == "import":
        ## This has a big enough possibility to mess things up that I'm not adding an
        ## argument to do it automatically. You must accept manually to avoid accidents.
        ic = input("Are you sure you want to import bookmarks? It might take a while. Back up your database first! (y/n) > ")
        if ic.lower() == "y" or ic.lower() == "yes":
            importer_c = choice.importformat
            if importer_c == None:
                importer_c = input("Import from Firefox-type browser, OneTab export, or another Seiran database? (firefox/onetab/seiran) > ")
            if importer_c == "firefox":
                getFirefoxBookmarks()
                return
            elif importer_c == "onetab":
                getOneTabBookmarks()
                return
            elif importer_c == "seiran":
                getSeiranBookmarks()
                return
        else:
            print("OK, nothing will be copied.")
    elif choice.command == "export":
        ex_form = choice.exportformat
        if ex_form == None:
            ex_form = input("Which format? (html,txt) > ")
        if ex_form == "html":
            exportBookmarks("html")
            return
        if ex_form == "txt":
            exportBookmarks("txt")
            return
        else:
            print("Export cancelled.")
            return
    elif choice.command == "clean":
        cleanBKMs()
        return
    elif choice.command == "copyright":
        print("Copyright 2015-2020 Matthew 'gargargarrick' Ellison. Released under the GNU GPL version 3. See LICENSE for full details.")
    elif choice.command == "help":
        print("Available arguments: add [a bookmark], del[ete a bookmark], list [all bookmarks], search [bookmarks], edit [a bookmark], import [bookmarks from other system], export [bookmarks to other formats], clean [bookmark metadata], copyright, help")
    else:
        conn.close()

if __name__ == '__main__':
    main()
