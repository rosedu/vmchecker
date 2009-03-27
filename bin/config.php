<?php
/**  
 *  @file	config.php
 *  @author	Gheorghe Claudiu-Dan, claudiugh [ at ] gmail dot com
 *  @date 	October 2008
 *  @brief	Configuration script for VMCHECKER
 * 
 */

$VMCHECKER_ROOT = ''; 		// must edit when installing vmchecker

/**
 * Get the content for a grade cell 
 * @param variable list of parameters 
 * @return string used in table cell as a content 
 */
function table_cell_content()
{
  list($nota, $href, $title) = func_get_args(); 
  return "<a href='$href' title='$title'>$nota</a>";
}


?>