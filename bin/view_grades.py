#! /usr/bin/env python2.5
#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-

"""Generates a HTML table containing the students' grades.

The layout can be modified by editing the following CSS elements: 

table#hw-results-table {}           
table#hw-results-table tr.tr-odd {} /* odd rows from table */
table#hw-results-table tr.tr-even {}/* even rows from table */           
table#hw-results-table td.hw-h {}   /* home heading row */
table#hw-results-table td.st-h {}   /* student heading column */
table#hw-results-table td.grade {}  /* the grade cell */
"""

__author__ = 'Gheorghe Claudiu-Dan <claudiugh@gmail.com>'


import sqlite3
import os
import urllib
import logging


import config
import vmcheckerpaths


_logger = logging.getLogger("vmchecker.view_grades")




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


def href(target, text, title='Click pentru detalii'):
    """ Generate a HTML anchor with target, text, and title attributes
    @return
    a HTML string with an A tag and it's attributes
    """
    return "<a href='%s' title='%s'>%s</a>" % (target, title, text)


def cpl_hack(student_name, hw_name, result):
    # TODO(alexandru): replace with something less specifi
    if result == '-1':
    	result = 'ok'
    return "<a href=\"Teme/nota.php?user=%s&homework=%s\">%s</a>" % (
        urllib.quote(student_name), urllib.quote(hw_name), result)


def gen_html(results, hws):
    # table header 
    html = "<table id='hw-results-table'> <tr> <td > Nume </td> "
    # the row with the name of the homeworks 
    for hw_name in hws:
        html += "<td class='hw-h'> %s </td> \n" %hw_name
    html += "</tr>"
    # table content 
    odd = True
    for student_name in sorted(results.keys()):
        if odd :
            tr_class = 'tr-odd' 
        else: 
            tr_class = 'tr-even'
        html += "<tr class='%s'> <td class='st-h'> %s </td> " %(tr_class, student_name)
        # for each student we generate a full row 
        for hw_name in hws:
            html += '<td class="grade">'
            if results[student_name].has_key(hw_name):
                html += cpl_hack(
                    student_name, hw_name, str(results[student_name][hw_name]))
            else:
                html += 'x'
            html += '</td>'
        html += "</tr> \n"
        odd = not odd
    html += ' </table>'
    return html 


def main():
    config.config_storer()

    global db_connect, db_cursor
    db_conn = sqlite3.connect(vmcheckerpaths.db_file())
    db_cursor = db_conn.cursor()

    (results, hws) = get_db_content()
    # send to the stdout all the HTML content 
    print (gen_html(results, hws))
    db_cursor.close()
    db_conn.close()

    print """
<div>
    <div style="float:left">
        Powered by <a href="http://github.com/vmchecker/vmchecker/tree/master">vmchecker</a>
    </div>
    <div style="float:left">
        &nbsp;-&nbsp;
    </div>
    <div style="float:left">
        <script type="text/javascript" src="http://www.ohloh.net/p/26869/widgets/project_users_logo.js"></script>
    </div>
</div>
"""


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
