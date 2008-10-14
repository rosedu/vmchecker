#! /usr/bin/python

__author__ = 'Gheorghe Claudiu-Dan, claudiugh@gmail.com'

import sqlite3
import misc
import os

"""
The script generates a HTML table that contains the grade for each student and for each homework
The layout can be modified by editing the following CSS elements: 

table#hw-results-table {}           
table#hw-results-table td.hw-h {}   /* home heading row */
table#hw-results-table td.st-h {}   /* student heading column */
table#hw-results-table td.grade {}  /* the grade cell */

"""

db_path = misc.db_file()
if None == db_path:
    print "DB file does not exist"
    exit()

db_conn = sqlite3.connect(db_path)
db_cursor = db_conn.cursor()

def get_db_content():
    """ Retrieve all the information needed from the DB    
    @return
    a touple (results, hws) :
    - a 2-D dictionary, having student names as rows and homework names as columns
    - a list containing all the homeworks in the DB
    """
    global db_cursor
    results = {}
    hws = []

    # first, get all the homeworks 
    db_cursor.execute('SELECT nume, deadline from teme;')
    for row in db_cursor.fetchall():
        (hw_name, deadline) = row        
        hws.append(hw_name)
        
    # build the 2-D dictionary, based on a JOIN selection  
    db_cursor.execute('SELECT studenti.nume, teme.nume, nota FROM studenti, teme, note WHERE studenti.id = note.id_student AND teme.id = note.id_tema ;') 
    for row in db_cursor.fetchall():
        (student_name, hw_name, grade) = row
        if not results.has_key(student_name):
            results[student_name] = {}
        results[student_name][hw_name] = grade
        
    return (results, hws)

def gen_html(results, hws):
    # table header 
    html = "<table id='hw-results-table'> <tr> <td > Nume </td> "
    # the row with the name of the homeworks 
    for hw_name in hws:
        html += "<td class='hw-h'> %s </td> \n" %hw_name
    html += "</tr>"
    # table content 
    for student_name in sorted(results.keys()):
        html += "<tr> <td class='st-h'> %s </td> " %student_name
        # for each student we generate a full row 
        for hw_name in hws:
            html += '<td class="grade">'
            if results[student_name].has_key(hw_name):
                html += str(results[student_name][hw_name])
            else:
                html += 'x'
            html += '</td>'
        html += "</tr> \n"
    html += ' </table>'
    return html 

def main():
    (results, hws) = get_db_content()
    # send to the stdout all the HTML content 
    print gen_html(results, hws)
    db_cursor.close()
    db_conn.close()

if __name__ == '__main__':
    main()
