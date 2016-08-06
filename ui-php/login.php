


<html >

<head>

    <link rel="stylesheet" href="vmchecker.css">
    <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

  <title>Vmchecker administration login</title>
</head>

<body bgcolor="#F6F6F6" style="font: Verdana" leftmargin="0px" topmargin="0px" marginwidth="0px" marginheight="0px">

        <form class = "well">

            <ul id="nav" >

                <li><a href="https://elf.cs.pub.ro/vmchecker"><b>&nbsp;Interfa&#539&#259 veche</b></a></li>

            </ul>
         </form>

            <table align="center" width="1000" height="500">
  <tr>

    <td>
      <img src="img/vmchecker_logo_large.png" width="300" height="50" alt="" /><br /><br />


       <b>vmchecker</b> ofer&#259 o infrastructur&#259 de testare automat&#259 si evaluare
       a temelor de cas&#259. Folosind aceast&#259 interfa&#539&#259, pute&#539i submite
       teme de cas&#259(studen&#539i) sau pute&#539i evalua temele de cas&#259
       (cadre didactice). Pentru persoanele cu drept administrativ, interfa&#539a permite
       gestiunea &#537i configurarea cursurilor &#537i a temelor de cas&#259 aferente.
    </td>

    <td>
    <br />
        <form name="userPass" action="userType.php" method="post">
            <center>

             <div style="width:400px;height:230px;border:3px solid #DCDCDC;">
                     <br />
                     <h3>Acceseaz&#259 interfa&#539a vmchecker</h3>
                         <br />
                    <font color="#008000" size="4">
                        <p style="text-align: center ">Utilizator &nbsp;&nbsp;
                         <input type="text"  tabindex="-1"  size="20" maxlength="100" name="userName"></p>
                   </font>
                    <font color="#008000" size="4">
                         <p style="text-align: center">Parol&#259 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                         <input type="password" size="20" maxlength="100" name="userPassword"></p>
                   </font>
                   <br />
                   <input class = "btn" type = "submit" value = "Autentificare" />

             </div>
            </center>
        </form>
    </td>

  </tr>
</table>

</body>

</html>
