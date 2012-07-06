


<html >

<head>

    <link rel="stylesheet" href="vmchecker.css">
    <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

  <title>Vmchecker administration login</title>
</head>

<body>

        <form class = "well">

            <ul id="list-nav" >

                <p style="text-align: left"><li><a href="https://elf.cs.pub.ro/vmchecker">&#60; &#60;vmchecker</a></li></p>

            </ul>
         </form>

            <table align="center" width="1000" height="500">
  <tr>

    <td>
    <img src="img/vmchecker_logo_large.png" width="300" height="50" alt="" /><br /><br /> &nbsp;&nbsp;
     Aceasta este o pagina de autentificare destinata titularilor si administraorilor cursurilor de pe vmchecker.
     Introduceti aici contul si parola primite sau cele de pe cs.curs.pub.ro , daca contul dumneavoastra are asemenea drepturi.</td>

    <td>
    <br />
        <form name="userPass" action="userType.php" method="post">
            <center>
             <div style="width:400px;height:300px;border:3px solid #DCDCDC;">
                     <h2>Formular de autentificare</h2>
                 <br />
                    <font color="#008000">
                     <h3>
                         <p style="text-align: center">Utilizator &nbsp;&nbsp;
                         <input type="text"  tabindex="-1"  size="30" maxlength="100" name="userName"></p>
                     </h3>
                   </font>
                   <br />
                    <font color="#008000">
                     <h3>
                         <p style="text-align: center">Parola &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                         <input type="password" size="30" maxlength="100" name="userPassword"></p>
                     </h3>
                   </font>
                   <input class = "btn" type = "submit" value = "Login" />

             </div>
            </center>
        </form>
    </td>

  </tr>
</table>

</body>

</html>
