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

<html>



<script type="text/javascript">
     var i = 0;

    function View()
    {
      myRef = window.open("grade.vmr",'mywin','left=20,top=20,width=500,height=500,toolbar=1,resizable=0');
    }

    function remove()
    {
        i--;
      var textName = "input" + i;
      var selectName = "select" + i;
      var select = document.getElementById(selectName);
      var text = document.getElementById(textName);

      select.parentNode.removeChild(select);
      text.parentNode.removeChild(text);



    }

    function add(type) {

      //Create a select and a text area on click.
      var textName = "input" + i;
      var selectName = "select" + i;
      var text = document.createElement("input");
      var select = document.createElement("select");
      var newSpace = '\r\n\t\t\t\t\t\t';
      var newSpace = document.createTextNode(newSpace);

      i++;

      select.setAttribute("name", selectName);
      select.setAttribute("id", selectName);
      select.setAttribute("size", '1');

      select.add(new Option("Noteaza", "+0.0"));
      select.add(new Option("+1.0", "+1.0"));
      select.add(new Option("+0.9", "+0.9"));
      select.add(new Option("+0.8", "+0.8"));
      select.add(new Option("+0.7", "+0.7"));
      select.add(new Option("+0.6", "+0.6"));
      select.add(new Option("+0.5", "+0.5"));
      select.add(new Option("+0.4", "+0.4"));
      select.add(new Option("+0.3", "+0.3"));
      select.add(new Option("+0.2", "+0.2"));
      select.add(new Option("+0.1", "+0.1"));

      select.add(new Option("-0.1", "-0.1"));
      select.add(new Option("-0.2", "-0.2"));
      select.add(new Option("-0.3", "-0.3"));
      select.add(new Option("-0.4", "-0.4"));
      select.add(new Option("-0.5", "-0.5"));
      select.add(new Option("-0.6", "-0.6"));
      select.add(new Option("-0.7", "-0.7"));
      select.add(new Option("-0.8", "-0.8"));
      select.add(new Option("-0.9", "-0.9"));
      select.add(new Option("-1.0", "-1.0"));

      //Assign different attributes to the element.
      text.setAttribute("type", type);
      text.setAttribute("value", " ");
      text.setAttribute("name", textName);
      text.setAttribute("id", textName);
      text.setAttribute("size", 250);

      var foo = document.getElementById("fooBar");

    //Append the element in page (in span)
      foo.appendChild(select);
      foo.appendChild(text);
      foo.appendChild(newSpace);

}

</script>

    <head>

        <link rel="stylesheet" href="vmchecker.css">
        <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

    <title>Vmchecker grading</title>
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
                <li><a href="search.php">Noteaza</a></li>
                <p style="text-align: right"><li><a href="addUser.php">Adauga student</a></li> </p>
                <li><a href="addHomework.php">Adauga tema</a></li>
                <li><a href="helpTitular.php">Ajutor titular</a></li>

            </ul>
         </form>
            <br />
            <br />
    <form name="cometarii" action="grade.php" method="post">


        Lasa comentariu si noteaza:
        <br />
        <span id="fooBar"><br /></span>
        <br />
        <br />

        <script>add(document.forms[0].value)</script>
        <input type="button"  class = "btn btn-success" value="Add" onclick="add(document.forms[0].value)"/>
        <input type="button" class = "btn btn-success" value="Remove" onclick="remove()"/>
        <!--Finished adding the select and input functions -->
        <br />
        <br />
        Nume examinator:<input type="text" size="30" maxlength="100" name="fname">

        <br />
        <br />

        <input type="submit" class = "btn btn-success" value="Trimite" />

    </form>

    <?php
            $addNumber = 1000;
            $myFile = "grade.vmr";
            $fh = fopen($myFile, 'a') or die("can't open file");
            for($j = 0; $j < $addNumber ; $j++)
        {
            $select = "select$j";
            $input = "input$j";
            if($_POST[$select])
            {
                fwrite($fh, $_POST[$select]);
                fwrite($fh," ");
            }
            if($_POST[$input])
            {
                fwrite($fh,$_POST[$input]);
                fwrite($fh,"\n");
            }
        }

        if($_POST["fname"])
         {
            fwrite($fh,"\n");
            $myFile = "grade.vmr";
            $fh = fopen($myFile, 'a') or die("can't open file");
            fwrite($fh,"graded by:");
            fwrite($fh,$_POST["fname"]);
        }

    ?>

    <form action="grade.php" method="post">
        <input type="hidden" name="Reset" value="Reset" />
        <input type="submit" class = "btn btn-success" value="Reseteaza" />
    </form>

    <?php
        if($_POST["Reset"])
        {
             $myFile = "grade.vmr";
             $fh = fopen($myFile, 'w') or die("can't open file");
             fwrite($fh,"");
        }
    ?>

    <form>
        <input type="button" class = "btn btn-success" value="Vizualizare comentarii si punctaje" onclick="View()" />
    </form>

</body>
</html>

<script src="http://code.jquery.com/jquery-1.7.2.min.js"></script>
<script src="jFunctions.js"></script>