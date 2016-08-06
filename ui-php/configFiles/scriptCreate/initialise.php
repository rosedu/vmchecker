<?php
    include 'securityAdmin.php'


    function readConfig($find, $replace)//$find - the line to find , $replace the string to replace the found line
    {
        $courseConfig = 'config';
        $findLength = strlen($find);
        $replace = ' = ' . $replace;
        $replace = $find . $replace;
        $replace = $replace . "\n";
        if (file_exists($courseConfig))
        {
            // Read the file in as an array of lines
            $fileData = file($courseConfig);

            $newArray = array();
            foreach($fileData as $line)
            {
             // find the line that starts with $find and change it to $replace
                 if (substr($line, 0, $findLength) == $find)
                 {
                    $line = $replace;
                 }
                 $newArray[] = $line;
             }

            // Overwrite config
            $fp = fopen($courseConfig, 'w');
            fwrite($fp, implode("",$newArray));
            fclose($fp);

        }

    }



   $cmd = $cmd . '../../../../../../../configFiles/vmchecker-init-course storer';
   $cmd = "python " . $cmd;
   exec($cmd);

    readConfig('CourseName', $_GET['courseName']);

    $holidays = $_GET['holidays'];
    readConfig('Holidays', $holidays);

    readConfig('UploadActiveFrom', $_GET['uploadActiveFrom']);

    readConfig('UploadActiveUntil', $_GET['uploadActiveUntil']);

   exec('rm -R ./etc');
   exec('rm initialise.php');
   exec('rm username.txt');
   header("Location: ../../../../../../../courseCreate.php");


?>