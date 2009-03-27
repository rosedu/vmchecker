<?php 
/**  
 *  @file	view_grades.php
 *  @author	Gheorghe Claudiu-Dan, claudiugh [ at ] gmail dot com
 *  @date 	October 2008
 *  @brief	Script that generates the HTML code for vmchecker.db content 
 * 
 */

require_once('config.php');

$db = sqlite3_open($VMCHECKER_ROOT . "vmchecker.db");
if (!$db) die ("Could not open database...");


/**
 * Get the information from the DB in two arrays   
 * @global $db SQLite3 database connection 
 * @return array containing the results array and the homeworks array
 * 
 */
function get_db_content()
{
  global $db; 
  $results = array(); 
  $hws = array(); 
	
  // get the results 
  $query = sqlite3_query($db, 
			 "SELECT studenti.nume as nume_st, teme.nume as nume_hw, nota ".
			 "FROM studenti, teme, note ".
			 "WHERE studenti.id = note.id_student AND teme.id = note.id_tema;");
  if (!$query) die (sqlite3_error($db));
  while ($entry = sqlite3_fetch_array($query))
    {
      if (!isset($results[$entry[nume_st]]))
	$results[$entry[nume_st]] = array();
      $results[$entry[nume_st]][$entry[nume_hw]] = $entry[nota];
    }
  sqlite3_query_close($query);

  // get the homeworks
  $query = sqlite3_query($db, "SELECT nume, deadline FROM teme;");
  if (!$query) die (sqlite3_error($db));
  while ($entry = sqlite3_fetch_array($query))
    {
      $hws[$entry[nume]] = $entry[deadline];
    }
  sqlite3_query_close($query);
  ksort($results);
  return array(results => $results, hws => $hws);
}

/** 
 * Generate the HTML code with the data structures given
 * @param array $results Associative 2D array that contains arrays of students 
 * @param array $hws Associative array that contains information about the homeworks 
 * 	  key = homework name, value = the homework deadline 
 * @return string the generated HTML table 
 */
function gen_html($results, $hws)
{
  $html = '<table id="hw-results-table" >';
  $html .= '<tr> <td> Nume </td> ';
  foreach ($hws as $nume_hw => $deadline) 
    $html .= "<td class='hw-h'>$nume_hw</td>"; // HW header 
  $html .= '</tr>';
	
  $odd = TRUE;
  foreach ($results as $nume_st => $res_st)
    {
      $tr_class = $odd ? 'tr-odd' : 'tr-even';
      $html .= "<tr class='$tr_class'><td class='st-h'>$nume_st</td>";
      foreach ($hws as $nume_hw => $deadline)
	{
	  $html .= '<td class="grade">';
	  if (isset($results[$nume_st][$nume_hw]))	    
	    $html .= table_cell_content($results[$nume_st][$nume_hw], '#', 'click pentru detalii'); // defined in config.php
	  else
	    $html .= 'x';
	  $html .= '</td>';
	}
      $html .= "</tr>\n";			
      $odd = !$odd;
    }

  $html .= '</table>';
  return $html; 
}

$db_content = get_db_content($db);
echo gen_html($db_content[results], $db_content[hws]);

sqlite3_close ($db);
?>
