<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?php

include 'securityTeacher.php';

?>



<html xmlns="http://www.w3.org/1999/xhtml">
<script>
     function clearOptions(id)
    {
    	var selectObj = document.getElementById(id);
    	var selectParentNode = selectObj.parentNode;
    	var newSelectObj = selectObj.cloneNode(false); // Make a shallow copy
    	selectParentNode.replaceChild(newSelectObj, selectObj);
    	return newSelectObj;
    }

    function create(directory,type,value)
    {
         if( value != '0')
            directory = directory + '/'+ value + '/2012/repo';

         $.post("searchDirDrop.php", {directory: ""+directory+"",type: ""+type+""}, function(data)
    {

         if(data.length >0)
        {
           eval(data);
        }


    });
     }
    function lookup(inputString, directoryRead, type) {

        if (type == 2)
        {
            var course = document.getElementById('inputString1').value;
            directoryRead = directoryRead + '/'+ course + '/2012/repo';
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

</script>
<head>
  <title></title>
</head>

<body onload="create('opt/vmchecker/storer/home/courses','1','0')">

 <form name="selection" action="grade.php" method="post">
<table>
      <tr>
        <td>
            Numele cursului
        </td>
        <td>
              Numele temei
        </td>
      </tr>
      <tr>
        <td>
                   <div>

                      <input type="text" size="47" value="" name="course" id="inputString1"
                      onkeyup="lookup(this.value,'opt/vmchecker/storer/home/courses',1);"
                      onblur="fill(); setCookie('course',this.value);" />
                  </div>

                  <div class="suggestionsBox" id="suggestions1" style="display: none;">
                      <div class="suggestionList" id="autoSuggestionsList1">
                      </div>
                  </div>
        </td>

        <td>
            <div>

                    <input type="text" size="47" value="" name="assignment" id="inputString2"
                    onkeyup="lookup(this.value,'opt/vmchecker/storer/home/courses',2);"
                    onblur="fill();" />
            </div>

            <div class="suggestionsBox" id="suggestions2" style="display: none;">
                    <div class="suggestionList" id="autoSuggestionsList2">
                    </div>
            </div>


        </td>
      </tr>
      <tr>
        <td>
            <select  name="course" id="select1"
            onchange="clearOptions('select2'); create('opt/vmchecker/storer/home/courses','2',this.value)" style="width: 300px">

            </select>
        </td>
        <td>
            <select  name="assignment" id="select2" style="width: 300px">

            </select>
        </td>
      </tr>
      <tr>

        <td>

            Cusul selectat este:
                <?php
                    $course = $_POST['course'];
                    if( isset($_COOKIE['course']))
                        echo $_COOKIE['course'];
                      else
                      {
                        if($_POST['course'])
                            echo $_POST['course'];
                        else
                            echo  "Nici un curs selectat";


                      }
                 ?>
        </td>

        <td>
            Tema selectat&#259 este:
                <?php
                    if( isset($_COOKIE['assignment']) )
                        echo $_COOKIE['assignment'];
                    else
                       {
                         if($_POST['assignment'])
                            echo $_POST['assignment'];
                        else
                            echo "Nici o tem&#259 selectat&#259";

                       }
                 ?>
        </td>

      </tr>
</table>
<input type="submit" class = "btn btn-success" value="Schimb&#259" />
</form>
</body>

</html>
<script src="http://code.jquery.com/jquery-1.7.2.min.js"></script>
<script src="jFunctions.js"></script>
