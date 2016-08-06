

<?php
      include 'securityTeacher.php';

   if($_POST['course'])
   {
      $course = $_POST['course'];
       setcookie("course",$course, time()+3600*10);
   }
   if($_POST['assignment'])

   {
      $assignment = $_POST['assignment'];
       setcookie("assignment",$assignment, time()+3600*10);
   }

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



    function lookup(inputString, directoryRead, type) {

        if (type == 3)
        {
            var course =   "<?php  if($_POST['course'])
                                        echo $_POST['course'];
                                   else
                                        if( isset($_COOKIE['course']))
                                            echo $_COOKIE['course'];?>";
            var homework = "<?php print $_COOKIE['assignment']?>";
            directoryRead = directoryRead + '/'+ course + '/2012/repo/' + homework;
        }

        if(inputString.length == 0)
        {

            $('#suggestions' + type).hide();

        }
            else
            {

    $.post("searchDir.php", {queryString: ""+inputString+"",directory: ""+directoryRead+"", type: ""+type+""}, function(data)
    {

        if(data.length >0)
        {

            $('#suggestions' + type).show();

            $('#autoSuggestionsList' + type).html(data);

        }

    });

}

}

     function fill3(thisValue)
        {

            $('#inputString3').val(thisValue);

            setTimeout("$('#suggestions3').hide();", 200);

    }

</script>

    <head>

        <link rel="stylesheet" href="vmchecker.css">
        <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

    <title>Vmchecker grading</title>
</head>

<body bgcolor="#F6F6F6" style="font: Verdana">

            <br />
            <br />


    <form name="cometarii" action="grade.php" method="post">


    <table>
      <tr>

        <td>

            Cusul selectat este:
                <?php
                    if($_POST['course'])
                        echo $_POST['course'];
                    else
                    {
                        if( isset($_COOKIE['course']))
                            echo $_COOKIE['course'];
                        else

                            echo  "Nici un curs selectat";
                    }
                 ?>
        </td>
      </tr>
      <tr>
        <td>
            Tema selectat&#259 este:
                <?php

                    if($_POST['assignment'])
                        echo $_POST['assignment'];
                    else
                    {
                    if( isset($_COOKIE['assignment']) )
                        echo $_COOKIE['assignment'];
                    else
                        echo "Nici o tem&#259 selectat&#259";

                       }
                 ?>
        </td>

      </tr>
    </table>
                <BR  />
                Numele studentului <br />
                  <div>
                    <br />
                    <input type="text" size="47" value="" id="inputString3"
                    onkeyup="lookup(this.value,'opt/vmchecker/storer/home/courses',3);" onblur="fill();" />
                </div>

                <div class="suggestionsBox" id="suggestions3" style="display: none;">
                    <div class="suggestionList" id="autoSuggestionsList3">
                    </div>
                </div>
                <br />
        Las&#259 comentariu si noteaz&#259:
        <br />
        <div id="fooBar"><br /></div>
        <br />
        <br />

        <script>add(document.forms[0].value)</script>
        <input type="button"  class = "btn btn-success" value="Adaug&#259" onclick="add(document.forms[0].value)"/>
        <input type="button" class = "btn btn-success" value="&#350terge" onclick="remove()"/>
        <!--Finished adding the select and input functions -->
        <br />
        <br />
        Nume examinator:<input type="text" size="30" maxlength="100" name="fname">

        <br />
        <br />

        <input type="submit" class = "btn btn-success" value="Salveaz&#259" />

    </form>

    <?php

            $myFile = "grade.vmr";
            $fh = fopen($myFile, 'a') or die("can't open file");

            $j = 0;
            while(isset($_POST["select$j"]))
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
                $j = $j + 1;
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
    <table>
      <tr>
        <td>

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
        </td>

        <td>

            <form>
                <input type="button" class = "btn btn-success" value="Vizualizare comentarii si punctaje" onclick="View()" />
            </form>

        </td>

      </tr>
    </table>

</body>
</html>

<script src="http://code.jquery.com/jquery-1.7.2.min.js"></script>
<script src="jFunctions.js"></script>
