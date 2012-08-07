<?php
    $directory = $_POST['directory'];
    $type = $_POST['type'];
    if ($handle = opendir($directory)) {

        while (false !== ($entry = readdir($handle)))
        {
            if(strcmp($entry,".") !=0 && strcmp($entry,"..") !=0 && strcmp($entry,".git") !=0)
                    echo "document.selection.select".$type.".
                    add( new Option('".$entry."'".","."'".$entry."'".",false,false));
                    ";
        }

    }
        closedir($handle);



?>
