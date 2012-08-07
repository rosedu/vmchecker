<?php
    include 'securityTeacher.php';
?>

<html >

<head>

    <link rel="stylesheet" href="vmchecker.css">
    <link rel="icon" type="image/gif"  width="16"  height="12" href="img/vmchecker-logo-perfect-fit-16x12.png" />

    <title>Vmchecker search box</title>



<script src="http://code.jquery.com/jquery-1.7.2.min.js"></script>

<script type="text/javascript">

      var fh = fopen("config");
      var file = fread(fh,flength(fh));
      alert(file);
    

    function lookup(inputString, directoryRead, type) {

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

    function fill1(thisValue)
        {

            $('#inputString1' ).val(thisValue);

            setTimeout("$('#suggestions1').hide();", 200);

    }

</script>

</head>

<body bgcolor="#F6F6F6" style="font: Verdana">


    <br />
    <br />

    <div>

        <form action="addHomework.php" method="post">

            <table>
                <tr>

                    <td>
                        Selecteaz&#259 curs: &nbsp;&nbsp;
                    </td>


                    <td>

                        <div>
                            <br />

                                <input type="text" size="47" value="" id="inputString1" name="courseName"
                                onkeyup="lookup(this.value,'opt/vmchecker/storer/home/courses',1);"
                                onblur="fill();" />
                        </div>

                        <div class="suggestionsBox" id="suggestions1" style="display: none;">

                            <div class="suggestionList" id="autoSuggestionsList1">
                            </div>

                        </div>

                    </td>
                </tr>

                <tr>
                    <td>

                        Numele temei:

                    </td>

                    <td>

                        <input type="text" size="30" value="" name="assignment" />
                        Ex: HashTable

                    </td>
                </tr>

                <tr>
                    <td>

                        Id tem&#259:

                    </td>

                    <td>

                        <input type="text" size="30" value="" name="assignment" />
                        Ex: powershell

                    </td>
                </tr>

                <tr>
                    <td>

                        Penaliz&#259ri pe zi dup&#259 termenul de predare:

                    </td>

                    <td>

                        <input type="text" size="30" value="" name="penaltyWeights" />
                        Default: 0.25

                    </td>
                </tr>

            <tr>
                    <td>

                        Maxim de puncte de penalizare:

                    </td>

                    <td>

                        <input type="text" size="30" value="" name="penaltyLimit" />
                        Default: 3

                    </td>
            </tr>

            <tr>
                    <td>

                        Termen de predare:

                    </td>

                    <td>

                        <input type="text" size="30" value="" name="deadline" />
                        Ex: 2012.03.01 23:59:00

                    </td>
            </tr>

            <tr>
                    <td>

                        Timp maxim de rulare a unei teme:

                    </td>

                    <td>

                        <input type="text" size="30" value="" name="timeout" />
                        Default: 180 secunde

                    </td>
            </tr>

            <br />
            <br />
            </table>
        </form>
    </div>

</body>

</html>
