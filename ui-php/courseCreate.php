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


    $myFile = "username.txt";   //The file in which I have the username:pasword:userTy[e
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

    //ending of the security part

    //begining of the create course

    $myFile = "courseDir.txt";
    $fh = fopen($myFile, 'r') or die("can't open file");
    $courseDir = fread($fh, filesize($myFile));
    $courseDir = $courseDir . "/" ;

    if ($_POST['courseId'])
    {
        if(date("m")<=6 && date("m")>=1 )
            $year = date("Y") - 1;
        else
            $year = date("Y");
        $courseDir = $courseDir . $_POST['courseId'];
        $courseDir = $courseDir . "/";
        $courseDir = $courseDir . $year;

            if (!is_dir($courseDir) )
            {
                mkdir ($courseDir, 0755, true);
                rcopy("configFiles/scriptCreate/",$courseDir);

                $createCall = 'Location: ' . $courseDir;
                $createCall = $createCall . '/initialise.php';
                $createCall = $createCall . "?courseName=";
                $createCall = $createCall . $_POST['courseName'];
                $createCall = $createCall . "&uploadActiveFrom=";
                $createCall = $createCall . $_POST['uploadActiveFrom'];
                $createCall = $createCall . "&uploadActiveUntil=";
                $createCall = $createCall . $_POST['uploadActiveUntil'];
                header($createCall);
            }
            else
                echo "Cursul exista deja";
    }
        // removes files and non-empty directories
    function rrmdir($dir)
    {
        if (is_dir($dir))
        {
            $files = scandir($dir);
            foreach ($files as $file)
            if ($file != "." && $file != "..") rrmdir("$dir/$file");
            rmdir($dir);
        }
        else
             if (file_exists($dir))
                unlink($dir);
    }

    // copies files and non-empty directories
    function rcopy($src, $dst)
    {
      if (file_exists($dst))
        rrmdir($dst);
      if (is_dir($src))
      {
        mkdir($dst);
        $files = scandir($src);
        foreach ($files as $file)
        if ($file != "." && $file != "..")
            rcopy("$src/$file", "$dst/$file");
      }
      else
        if (file_exists($src))
            copy($src, $dst);
    }


?>

<html xmlns="http://www.w3.org/1999/xhtml">

<head>

    <link rel="stylesheet" href="vmchecker.css">
    <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

  <title>Vmchecker administration page</title>

</head>


<body>

   <form class = "well">

            <ul id="list-navy" >
                <li><a href="#" onclick="javascript:deleteCookie();">Logoff</a></li>
                <li><a>User : <?php echo $userInput; ?></a></li>
            </ul>

            <ul id="list-nav" >

                <li><a href="https://elf.cs.pub.ro/vmchecker">&#60; &#60;vmchecker</a></li>
                <li><a href="/~cdidii/vmchecker/adminControlPannel.php">Home</a></li>
                <li><a href="/~cdidii/vmchecker/titularControlPannel.php">Titular</a></li>
                <p style="text-align: right"><li><a href="/~cdidii/vmchecker/courseCreate.php">Adauga Curs</a></li> </p>
                <li><a href="/~cdidii/vmchecker/helpAdmin.php">Ajutor admin</a></li>
            </ul>
         </form>

        <br />
        <br />
        <br />

         <tr>

                <td>
                         Completeaza campurile de mai jos pentru a crea un curs nou.
                         <form name="courseCreate" action="courseCreate.php" method="post">
                         <table>

                            <tr>

                                <td>

                                    Numele cursului:

                                </td>

                                <td>

                                    <input type="text"  tabindex="-1"
                                    size="30" maxlength="100" name="courseName"> &nbsp;&nbsp;Ex: Sisteme de operare

                                </td>

                           </tr>

                           <tr>

                             <td>
                                Id curs:
                             </td>

                             <td>

                                <input type="text"  tabindex="-1"
                                size="30" maxlength="100" name="courseId">&nbsp;&nbsp;Ex: so

                             </td>

                           </tr>

                            <tr>

                             <td>
                                Upload activ incepand cu data de:
                             </td>

                             <td>

                                <input type="text"  tabindex="-1"
                                size="30" maxlength="100" name="uploadActiveFrom">&nbsp;&nbsp;Ex: 2012.03.31 23:59:00

                             </td>

                             </tr>

                             <tr>

                             <td>
                                Upload activ pana la data de:
                             </td>

                             <td>

                                <input type="text"  tabindex="-1"
                                size="30" maxlength="100" name="uploadActiveUntil">&nbsp;&nbsp;Ex: 2012.03.31 23:59:00

                             </td>

                           </tr>

                         </table>

                         <br />

                         <input type="submit" class = "btn btn-success" name="" value="Trimite" />
                    </form>

                </td>

            </tr>



</body>

</html>
<script src="jFunctions.js"></script>