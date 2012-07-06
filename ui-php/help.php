<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
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
?>

<html xmlns="http://www.w3.org/1999/xhtml">

<head>

    <link rel="stylesheet" href="vmchecker.css">
    <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

  <title>Pagina de ajutor pentru admin</title>

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
                <li><a href="/~cdidii/vmchecker/help.php">Ajutor</a></li>


            </ul>
         </form>

        <br />
        <br />
        <br />



</body>

</html>
<script src="jFunctions.js"></script>