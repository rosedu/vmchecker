<?php
    function hasher($info, $encdata = false)
        {
            $strength = "08";
      //if encrypted data is passed, check it against input ($info)
            if ($encdata)
         {
             $hash2 = hasher($info);
             if (substr($encdata, 0, 7) == substr($hash2, 0, 7))
             {
                  return true;
             }
             else
             {
             return false;
             }
         }
         else
         {
  //make a salt and hash it with input, and add salt to end
             $salt = "";
             for ($i = 0; $i < 22; $i++)
             {
                 $salt .= substr("./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", mt_rand(0, 63), 1);
             }
  //return 82 char string (60 char hash & 22 char salt)
              return crypt($info, "$2a$".$strength."$".$salt).$salt;
         }
        }

    $userInput = $_COOKIE['userName'];
    $hashPass =  $_COOKIE['userPass'];


    $myFile = "../../../../../../../username.txt";   //The file in which I have the username:pasword:userTy[e
    $fh = fopen($myFile, 'r') or die("can't open file");
    $jsonCode = fread($fh, filesize($myFile));


   $user = explode(":",$jsonCode);

   $len = count($user);

   for ($i=0 ; $i<$len; $i++)
   {
        if ( strcmp($user[$i] , $userInput) == 0)
            break;
   }

     $password = $user [$i + 1];
     $type = $user[$i+2];

    if (hasher($password, $hashPass) == true && $i != $len)
    {
        if ($type == "T")   //if the user is a titular and tries to access the adminControlPannel it will be redirected to the titularControlPannel
            header("Location: /~cdidii/vmchecker/titularControlPannel.php");
    }
    else
        header("Location: /~cdidii/vmchecker/login.php");

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

    $holidayStart = date('Y') + 1;
    $holidayStart = $holidayStart . '.03.31 23:59:00';
    readConfig('HolidayStart', $holidayStart);

    $holidayStart = date('Y') + 1;
    $holidayStart = $holidayStart . '.04.02 23:59:00';
    readConfig('HolidayFinish', $holidayFinish);

    readConfig('UploadActiveFrom', $_GET['uploadActiveFrom']);

    readConfig('UploadActiveUntil', $_GET['uploadActiveUntil']);

   exec('rm -R ./etc');
   exec('rm initialise.php');
   exec('rm username.txt');
   header("Location: /~cdidii/vmchecker/courseCreate.php");


?>