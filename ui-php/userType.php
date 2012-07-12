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

    $userInput = $_POST['userName'];
    $passwordInput = $_POST['userPassword'];

    $myFile = "username.txt";
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


    $hashPass = hasher($password);
    if (hasher($passwordInput, $hashPass) == true && $i != $len)
    {
        setcookie("userName",$userInput, time()+3600*24);
        setcookie("userPass",$hashPass, time()+3600*24);
        if ($type == "A")
            header("Location: adminControlPannel.php");
        if ($type == "T")
            header("Location: titularControlPannel.php");
    }
    else
        header("Location: login.php");
?>