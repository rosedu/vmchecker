<?php
    include 'securityAdmin.php'
?>


<html >


<head>

    <link rel="stylesheet" href="vmchecker.css">
    <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

  <title>Vmchecker administration page</title>

</head>

<body bgcolor="#F6F6F6" style="font: Verdana">   

  <?php
        include 'menuAdmin.htm';
  ?>

        <br />
        <br />
        <br />

         <table align="center" width="100%">
            <tr>

            <td>
                <img src="img/vmchecker_logo_large.png" width="300" height="50" alt="" />
                  <br /><br />
                  <font face="Times New Roman" size="4">Bine ai venit pe pagina de administrare a cursurilor de pe vmchecker.
                  Pentru a naviga in interiorul aplica&#539ei folose&#537te butoanele de navigare de mai sus.</font>
                  <br />
                  <br />

                 <?php
                    $myFile = "courseDir.txt";
                    if ($_POST['newCourseDir'])
                    {
                        $fh = fopen($myFile, 'w') or die("can't open file");
                        fwrite($fh,$_POST['newCourseDir']);
                    }

                    $fh = fopen($myFile, 'r') or die("can't open file");
                    $courseDir = fread($fh, filesize($myFile));

                    if (!is_dir($courseDir) )
                    {
                        mkdir ($courseDir, 0755, true);
                    }

                 ?>

             </td>
            </tr>
          </table>




</body>

</html>

<script src="jFunctions.js"></script>
