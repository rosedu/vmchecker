<?php
   include 'securityTeacher.php';

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

                $holidays = $_POST['holidays'];
                $createCall = $createCall . "&holidays=";
                $createCall = $createCall . $holidays;
                for($i = 0; $i < $holidays; $i++)
                {
                    $createCall .= "&hStart" . $i . "=" . $_POST['hStart' . $i];
                    $createCall .= "&hEnd" . $i . "=" . $_POST['hEnd' . $i];
                }

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

    <script type="text/javascript">
        var holidaysOld = 0;
        function holiday()
        {
          var holidays = document.getElementById('holidays').value;
          var holidayStart = document.getElementById("holidayStart");
          var holidayFinish = document.getElementById("holidayFinish");
          if(holidays > this.holidaysOld)
            for(i = 0; i < holidays; i++)
            {

                  var hStart = document.createElement("input");
                  hStart.setAttribute("type", "text");
                  hStart.setAttribute("value", "");
                  hStart.setAttribute("name", "hStart" + i);
                  hStart.setAttribute("id", "hStart" + i);
                  hStart.setAttribute("size", 30);


                  var hEnd = document.createElement("input");
                  hEnd.setAttribute("type", "text");
                  hEnd.setAttribute("value", "");
                  hEnd.setAttribute("name", "hEnd" + i);
                  hEnd.setAttribute("id", "hEnd" + i);
                  hEnd.setAttribute("size", 30);

                  holidayFinish.appendChild(hEnd);
                  holidayStart.appendChild(hStart);

            }
            this.holidaysOld = this.holidays;

        }
    </script>

  <head>

      <link rel="stylesheet" href="vmchecker.css">
      <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

    <title>Vmchecker administration page</title>

  </head>


<body>



        <br />
        <br />
        <br />

         <tr>

                <td>
                         Completeaz&#259 c&#226mpurile de mai jos pentru a crea un curs nou.
                         <form name="courseCreate" action="courseCreate.php" method="post">
                         <table>

                            <tr>

                                <td>

                                    Numele cursului:

                                </td>

                                <td>

                                    <input type="text"
                                    size="30" maxlength="100" name="courseName"> &nbsp;&nbsp;Ex: Sisteme de operare

                                </td>

                           </tr>

                           <tr>

                             <td>
                                Id curs:
                             </td>

                             <td>

                                <input type="text"
                                size="30" maxlength="100" name="courseId">&nbsp;&nbsp;Ex: so

                             </td>

                           </tr>

                            <tr>

                             <td>
                                Upload activ incep&#226nd cu data de:
                             </td>

                             <td>

                                <input type="text"
                                size="30" maxlength="100" name="uploadActiveFrom">&nbsp;&nbsp;Ex: 2012.03.31 23:59:00

                             </td>

                             </tr>

                             <tr>

                             <td>
                                Upload activ p&#226n&#259 la data de:
                             </td>

                             <td>

                                <input type="text"
                                size="30" maxlength="100" name="uploadActiveUntil">&nbsp;&nbsp;Ex: 2012.03.31 23:59:00

                             </td>

                           </tr>

                           <tr>

                             <td>
                                Num&#259r de vacan&#355e:
                             </td>

                             <td>
                                <script>holiday();</script>
                                <input type="text"  id="holidays" onkeyup="holiday()"
                                size="30" maxlength="100" name="holidays">&nbsp;&nbsp;Ex: 2
                             </td>

                           </tr>

                           <tr>

                             <td>
                                Inceputul vacan&#355ei:
                             </td>

                             <td>

                                <span id="holidayStart"><br /></span>
                                &nbsp;&nbsp;Ex: 2013.03.27 23:59:00
                             </td>

                           </tr>

                            <tr>

                             <td>
                                Sf&#226r&#351itul vacan&#355ei:
                             </td>

                             <td>

                                <span id="holidayFinish"><br /></span>
                                  &nbsp;&nbsp;Ex: 2013.03.31 23:59:00
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
