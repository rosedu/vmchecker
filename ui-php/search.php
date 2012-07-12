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

    if (hasher($password, $hashPass) != true && $i != $len)
        header("Location: login.php");
?>

<html >

<head>

    <link rel="stylesheet" href="vmchecker.css">
    <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

    <title>Vmchecker search box</title>



<script src="http://code.jquery.com/jquery-1.7.2.min.js"></script>

<script type="text/javascript">

    function lookup(inputString, directoryRead, type) {

        if (type == 2)
        {
            var course = document.getElementById('inputString1').value;
            directoryRead = directoryRead + '/'+ course + '/2012/repo';
        }

        if (type == 3)
        {
            var course = document.getElementById('inputString1').value;
            var homework = document.getElementById('inputString2').value;
            directoryRead = directoryRead + '/'+ course + '/2012/repo/' + homework;
        }

        if(inputString.length == 0)
        {

            $('#suggestions' + type).hide();

        }
            else
            {

    $.post("searchFolder.php", {queryString: ""+inputString+"",directory: ""+directoryRead+"", type: ""+type+""}, function(data)
    {

        if(data.length >0)
        {

            $('#suggestions' + type).show();

            $('#autoSuggestionsList' + type).html(data);

        }

    });

}

}

    function fill1(thisValue)
        {

            $('#inputString1' ).val(thisValue);

            setTimeout("$('#suggestions1').hide();", 200);

    }

        function fill2(thisValue)
        {

            $('#inputString2').val(thisValue);

            setTimeout("$('#suggestions2').hide();", 200);

    }

     function fill3(thisValue)
        {

            $('#inputString3').val(thisValue);

            setTimeout("$('#suggestions3').hide();", 200);

    }

</script>

</head>

<body>

    <form class = "well">

            <ul id="list-navy" >
                <li><a href="#" onclick="javascript:deleteCookie();">Logoff</a></li>
                <li><a>User : <?php echo $userInput; ?></a></li>
            </ul>

            <ul id="list-nav" >

                <li><a href="https://elf.cs.pub.ro/vmchecker">&#60; &#60;vmchecker</a></li>
                <li><a href="adminControlPannel.php">Home</a></li>
                <li><a href="location.href='search.php">Noteaza</a></li>
                <p style="text-align: right"><li><a href="addUser.php">Adauga student</a></li> </p>
                <li><a href="addHomework.php">Adauga tema</a></li>
                <li><a href="helpTitular.php">Ajutor titular</a></li>

            </ul>
    </form>
    <br />
    <br />

    <div>

            <form action="grade.php" method="post">

            <table>
              <tr>
                <td>Nume cursului</td>
                <td>Numele temei</td>
                <td>Numele studentului</td>
              </tr>
              <tr>

                <td>

                <div>
                    <br />
                    <input type="text" size="47" value="" id="inputString1" onkeyup="lookup(this.value,'opt/vmchecker/storer/home/courses',1);" onblur="fill();" />
                </div>

                <div class="suggestionsBox" id="suggestions1" style="display: none;">
                    <div class="suggestionList" id="autoSuggestionsList1">
                    </div>
                </div>

                </td>

                <td>

                <div>
                    <br />
                    <input type="text" size="47" value="" id="inputString2" onkeyup="lookup(this.value,'opt/vmchecker/storer/home/courses',2);" onblur="fill();" />
                </div>

                <div class="suggestionsBox" id="suggestions2" style="display: none;">
                    <div class="suggestionList" id="autoSuggestionsList2">
                    </div>
                </div>

                </td>

                <td>

                 <div>
                    <br />
                    <input type="text" size="47" value="" id="inputString3" onkeyup="lookup(this.value,'opt/vmchecker/storer/home/courses',3);" onblur="fill();" />
                </div>

                <div class="suggestionsBox" id="suggestions3" style="display: none;">
                    <div class="suggestionList" id="autoSuggestionsList3">
                    </div>
                </div>

                </td>

              </tr>
            </table>

                <input type="submit" class = "btn btn-success" value="Trimite tot" />

            </form>
    </div>

    </body>

</html>