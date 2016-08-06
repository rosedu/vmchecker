<?php
    $queryString = $_POST['queryString'];
    $type = $_POST['type'];
    if ($handle = opendir($_POST['directory'])) {

        while (false !== ($entry = readdir($handle)))
        {
            if(substr($entry, 0, strlen($queryString)) == $queryString )
            {
                if($type == 1)
                    echo '<li onClick="fill1(\''.$entry.'\');">'.$entry.'</li>';
                if($type == 2)
                    echo '<li onClick="fill2(\''.$entry.'\');">'.$entry.'</li>';
                if($type == 3)
                    echo '<li onClick="fill3(\''.$entry.'\');">'.$entry.'</li>';
            }
        }

    }

        closedir($handle);



?>