"use strict";

var Courses = new Meteor.Collection("courses");
var Assignments = new Meteor.Collection("assignments");
var Grades = new Meteor.Collection("grades");
var Results = new Meteor.Collection("results");
var Files = new Meteor.Collection("files");

var Notifications = new Meteor.Stream('notifications');

// Restricts creating accounts on the client
Accounts.config({
  forbidClientAccountCreation: true
});

var Repo = new FS.Collection("repo", {
  stores: [new FS.Store.FileSystemRO("repo")]
});


if (Meteor.isClient) {

  var NotificationCollection = new Meteor.Collection(null);
  var CurrentTree = "";

  Notifications.on( 'message', function(message, path) {
    var editor = ace.edit("editor");
    editor.setReadOnly(false);
    editor.setValue(message);
    editor.setReadOnly(true);
    NotificationCollection.upsert(
    {path:path},
    {
      message: message,
      path: path
    });
  });

  Notifications.on( 'filetree', function(serial_tree) {
    $('#jstree_demo_div').jstree("destroy");
    $('#jstree_demo_div').jstree({ 'core' : {
    'data' : JSON.parse(serial_tree)
    } });
    $('#jstree_demo_div').on('select_node.jstree', function(e,object) {
      console.log(object.node.id);
      var found = NotificationCollection.findOne({path:object.node.id});
      if (found) {
        console.log("found");
        var editor = ace.edit("editor");
        editor.setReadOnly(false);
        editor.setValue(found.message);
        editor.setReadOnly(true);
      } else {
        Notifications.emit('getfile', object.node.id);
      }
    });
  });

  Meteor.startup(function() {
    Notifications.emit('start');
    //var editor = ace.editor("editor");
  });

  // subscribing to databases
  Deps.autorun(function() {
    Meteor.subscribe("courses");
    Meteor.subscribe("assignments");
    Meteor.subscribe("grades");
    Meteor.subscribe("userData");
    Meteor.subscribe("results");
    Meteor.subscribe("files");
    Meteor.subscribe('myRepoFiles');
  });

  // get current course
  var initializedCursor = false;
  Deps.autorun( function() {
    if ( typeof Session.get("courseCursor") == 'undefined' ) {

      Session.set("courseCursor" , Courses.findOne({}, {
        sort: {
          id: -1,
          title: 1
        }
      }));

      if ( typeof Session.get("courseCursor") != 'undefined' ) {

        Session.set("courseId", Session.get("courseCursor").id );
        Meteor.call('getAssignments', Session.get("courseId"));
        Meteor.call('getAllGrades', Session.get("courseId"));
      }
    } else if ( ! initializedCursor ) {
      Session.set("courseId", Session.get("courseCursor").id );
      Meteor.call('getAssignments', Session.get("courseId"));
      Meteor.call('getAllGrades', Session.get("courseId"));
      initializedCursor = true;
    }
  });

  // courses geter
  Template.courses.courses = function() {
    return Courses.find({}, {
      sort: {
        id: -1,
        title: 1
      }
    });
  };

  // get archives
  Template.fileList.helpers({
    files: function () {
      return Repo.find({
        username: Meteor.user().username,
        course: Session.get('courseId')
      });
    }
  });

  Template.courses.events({
    'change': function(event) {
      var elem = event.currentTarget;
      Session.set("courseId", elem.value);
      Meteor.call('getAssignments', Session.get("courseId"));
      Meteor.call('getAllGrades', Session.get("courseId"));
      Session.set("courseCursor",  Session.get("courseId"));
    },
    'click': function(event) {
      var elem = event.currentTarget;
      Meteor.call('getCourses');
      if (Session.get("courseId") != elem.value) {
        Session.set("courseId", elem.value);
        Meteor.call('getAssignments', Session.get("courseId"));
        Meteor.call('getAllGrades', Session.get("courseId"));
        Session.set("courseCursor",  Session.get("courseId"));
      }
    }
  });

  Template.assignments.events({
    'change': function(event) {
      var text = event.currentTarget.value;
      console.log(text);
      Session.set("assignmentId", text.trim());
      Meteor.call(
        'getUserResults',
        Session.get('courseId'),
        Session.get('assignmentId'),
        Meteor.user().username
      );
      console.log("---" + Session.get("assignmentId"));
      Notifications.emit('changetree', Meteor.user().username, Session.get('courseId'), Session.get('assignmentId'));
    },
    'click': function(event) {
      var text = event.currentTarget.value;
      Session.set("assignmentId", text.trim());
      Meteor.call(
        'getUserResults',
        Session.get('courseId'),
        Session.get('assignmentId'),
        Meteor.user().username
      );
      console.log("---" + Session.get("assignmentId"));
      Notifications.emit('changetree', Meteor.user().username, Session.get('courseId'), Session.get('assignmentId'));
    }
  });

  Template.changeLang.events({
    'change': function(event) {
      if (Cookie.get("i18next") != event.currentTarget.value) {
        Cookie.set("i18next", event.currentTarget.value);
        history.go(0);
      }
    }
  });

  Template.changeLang.languages = function() {
    // TODO: use database maybe?
    return [{
      "code": "ro",
      "name": "Romana",
      "selected": (Cookie.get('i18next') == "ro" ? "selected" : "")
    }, {
      "code": "en",
      "name": "English",
      "selected": (Cookie.get('i18next') == "en" ? "selected" : "")
    }];
  }

  Template.assignments.assignments = function() {
    return Assignments.find({
      courseId: Session.get("courseId")
    });
  };

  Template.editor.events({
    'render' : function(event) {
      console.log('salut');
    }
  });


  Template.assignmentInfo.content = function() {
    return Assignments.find({
      courseId: Session.get("courseId"),
      assignmentId: Session.get("assignmentId")
    });
  }

  Template.grades.grades = function() {
    return Grades.find({
      courseId: Session.get("courseId")
    }, {
      sort: {
        studentId: -1
      },
      limit: 10
    });
  }

  Template.grades.display = function() {
    return Session.get("assignmentId") == "";
  }

  Template.result.content = function() {
    if (Meteor.user()) {

      if (! Session.get('courseId') || ! Session.get('assignmentId'))
        return "";

      var val = Results.findOne({
        courseId: Session.get('courseId'),
        assignmentId: Session.get('assignmentId'),
        userId: Meteor.user().username
      }).content;

      var replaceValue = /\\n/g;
      val = val.replace( replaceValue, "%%");

      var parsed = JSON.parse(val);
      var result = "";

      for ( var field in parsed ) 
        for ( var element in parsed[field] ) 
          result += element + parsed[field][element];

      replaceValue = /%%/g;
      result = result.replace( replaceValue, "<br />");  

      return result;
    }
    return "";
  }

  Template.circle.display = function(league) {
    return Session.get("loading") == true;
  };

  Template.upload.events({
    'change input': function(ev) {
      _.each(ev.target.files, function(file) {
        Meteor.saveFile(file);
      });
    }
  });

}


function addFile(filepath, user, assignment, course) {  
  var found = Repo.findOne({path: filepath});
  if (!found) {
    var file = new FS.File(filepath);
    file.path = filepath;
    file.username = user;
    file.assignment = assignment;
    file.course = course;
    file.name(course+"_"+assignment+"_"+user);
    Repo.insert(file, function(error, file) {
    });
    return file;
  }
  return found;
}

var fs = Npm.require('fs');
var path = Npm.require('path');

function getCourseRoots() {
  var list = fs.readFileSync('/etc/vmchecker/config.list').toString();
  var lines = list.split('\n');
  var dict = {};
  for (var i in lines) {
    var pair = lines[i].split(':');
    if (pair[0].length == 0)
      continue;
    dict[ pair[0] ] = path.dirname(pair[1]);
  }
  return dict;
}

function readRepo() {
  var roots = getCourseRoots();
  for (var course in roots) {
    var repoPath = path.join(roots[course], "repo");
    console.log(course+":"+repoPath);
    var assignments = fs.readdirSync(repoPath);
    for (var i=0; i<assignments.length; i++) {
      if (!assignments[i] || assignments[i][0] == '.')
        continue;
      var assignmentPath = path.join(repoPath, assignments[i]);
      console.log(assignmentPath);
      var users = fs.readdirSync(assignmentPath);
      console.log(users);
      for (var j=0; j<users.length; j++) {
        if (users[j][0] == '.')
          continue;
        var userPath = path.join(assignmentPath, users[j]);
        var archivePath = path.join(userPath,"current/archive.zip");
        console.log(archivePath);
        try {
          fs.statSync(archivePath); // to make sure the file exists
          addFile(archivePath, users[j], assignments[i], course);
        } catch (e) {
          //console.log(e);
        }
      }
    }
  }
}

//var folder_path = '/home/vmchecker/vmchecker';

function readDir(dirpath) {
  var fs = Meteor.require('fs');
  var path = Meteor.require('path');
  var allFiles = [dirpath];
  try {
    var files = fs.readdirSync(dirpath);
  } catch (e) {
    console.log(e);
    return allFiles;
  }
  for (var i=0; i<files.length; i++) {
    var newpath = path.join(dirpath, files[i]);
    var res = readDir(newpath);
    allFiles = allFiles.concat(res);
  }
  console.log("--- Files Lenght: " + files.length);
  return allFiles;
}

function GetFileTree( node_path ) {
  fs = Meteor.require('fs');
  var path = Meteor.require('path');
  var fileList = readDir(node_path);

  var tree = [];
  console.log("Lenght = " + fileList.length);
  for (var i=0;i<fileList.length;i++) {
    var file_path = fileList[i];
    var file_dir = path.dirname(file_path);
    if (file_dir == path.dirname(node_path))
      file_dir = "#";
    var file_name = path.basename(file_path);
    tree.push({"id":file_path, "parent":file_dir, "text":file_name, state: {"opened": true}});
  }

  return JSON.stringify(tree);
}

function GetAssignmentPath( username, courseId, assignmentId ) {

  var fs = Npm.require('fs');
  var folderPath = '/etc/vmchecker/config.list';
  var assignmentArchivePath = fs.readFileSync(folderPath);

  assignmentArchivePath = assignmentArchivePath.toString();

  // getting the assignment folder path
  var position = assignmentArchivePath.indexOf(courseId + ":") + courseId.length + 1;
  assignmentArchivePath = assignmentArchivePath.substr(position);
  position = assignmentArchivePath.indexOf('\n');
  assignmentArchivePath = assignmentArchivePath.substr(0, position).replace( /config/g, "repo") 
                      + "/" + assignmentId + "/" + username + "/current";

  return assignmentArchivePath;
}

if (Meteor.isServer) {

  // We need this to avoid using the cfs-filesystem packages
  FS.TempStore.Storage = new FS.Store.FileSystemRO('_tempstore', { internal: true });

  var dir_path = "/home/vmchecker/Desktop";

  //Meteor.users.remove({});
  Meteor.startup(function() {
    console.log("Started server");

    readRepo();

    Repo.allow({
      insert: function(userId, doc) {
        return false;
      },
      update: function(userId, doc, fieldNames, modifier) {
        return false;
      },
      remove: function(userId, doc) {
        return false;
      },
      download: function(userId, doc) {

        var username = Meteor.users.findOne({ _id : userId}).username;

        if ( ! userId )
          return false;

        console.log( "File match: " + doc.path.indexOf(username) );

        if ( doc.path.indexOf(username) == -1 )
          return false;

        return true;
      }
    });

    FS.HTTP.publish(Repo, function () {
      // TODO: Publish only files that the user has access to
      console.log(this.userId)
      if (this.userId) {
        return Repo.find({});
      } else {
        this.ready();
      }
    });


    Meteor.publish('myRepoFiles', function() {
      // TODO: Publish only files that the user has access to
      if (this.userId) {
        return Repo.find({});
      } else {
        this.ready();
      }
    });

    Meteor.publish("grades", function() {
      return Grades.find({});
    });
    Meteor.publish("courses", function() {
      return Courses.find({});
    });
    Meteor.publish("assignments", function() {
      return Assignments.find({});
    });
    // Meteor.publish("userData", function () {
    //   return Meteor.users.find({});
    // });
    Meteor.publish("results", function() {
      return Results.find({});
    });

    //allow any connected client to listen on the stream
    Notifications.permissions.read(function(userId, eventName) {
      return true;
    });

    Notifications.permissions.write(function(userId, eventName) {
      return true;
    });

    Notifications.on('start', function() {
      var tree = GetFileTree(dir_path);
      //console.log( " FileTree : \n" + tree);
      Notifications.emit('filetree', tree);
    });

    Notifications.on('getfile', function(filename) {
      fs.readFile(filename, function (err, data) {
        if (err) {
          console.log(err)
          return;
        }
        Notifications.emit('message', data.toString(), filename);
      });
    });

    Notifications.on('changetree', function(username, courseId, assignmentId) {
      var path = GetAssignmentPath( username, courseId, assignmentId );
      var tree = GetFileTree(path);
      Notifications.emit('filetree', tree);
    });

    Meteor.autorun( function() {
      var tree = GetFileTree(dir_path);
      //console.log( " FileTree : \n" + tree);
      Notifications.emit('filetree', tree);
    })

    /// ===>>> SERVER METHODS

    // the result from calling getCourses
    var getCoursesStaticResults;

    // last update time
    var getCoursesLastUpdateTime = 0;

    /// Time in Miliseconds
    var getCoursesTimeTreshold = 6000;

    Meteor.methods({
      getCourses: function() {
        this.unblock();
        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }

        // the code only calls the getCourses method on the server only if an amount of time has elapsed from the last call
        // the amount of time is specified by the $getCoursesLastUpdateTime variable
        var currentTime = (new Date()).getTime();
        console.log("---Current Time:" + currentTime);
        console.log("---LastTime:" + getCoursesLastUpdateTime);
        console.log("---Difference:" + (currentTime - getCoursesLastUpdateTime));

        if ( typeof getCoursesStaticResults === 'undefined' || currentTime - getCoursesLastUpdateTime > getCoursesTimeTreshold ) {
          console.log("Query to Boss");
          getCoursesStaticResults = HTTP.get("http://localhost/services/services.py/getCourses?null", options);
          getCoursesLastUpdateTime = currentTime;

          var res = getCoursesStaticResults;

          var names = JSON.parse(res.content);
          console.log(names);
          //Courses.remove({});
          for (var i = 0; i < names.length; i++) {
            Courses.update({
              id: names[i].id
            }, {
              id: names[i].id,
              title: names[i].title
            }, {
              upsert: true
            });
        }
        }
      },
      getAssignments: function(courseId) {
        this.unblock();
        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getAssignments?courseId=" + courseId, options);

        var assignments = JSON.parse(res.content);
        for (var i = 0; i < assignments.length; i++) {
          Assignments.update({
            courseId: courseId,
            assignmentId: assignments[i].assignmentId
          }, {
            courseId: courseId,
            assignmentId: assignments[i].assignmentId,
            assignmentTitle: assignments[i].assignmentTitle,
            deadline: assignments[i].deadline,
            statementLink: assignments[i].statementLink,
            assignmentStorage: assignments[i].assignmentStorage
          }, {
            upsert: true
          });
        }
      },
      getAllGrades: function(courseId) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getAllGrades?courseId=" + courseId, options);
        var students = JSON.parse(res.content);
        for (var i = 0; i < students.length; i++) {
          for (var assignmentId in students[i].results) {
            Grades.update({
              courseId: courseId,
              studentId: students[i].studentId,
              assignmentId: assignmentId
            }, {
              courseId: courseId,
              studentId: students[i].studentId,
              assignmentId: assignmentId,
              grade: students[i].results[assignmentId]
            }, {
              upsert: true
            });
          }
        }
      },
      getUserResults: function(courseId, assignmentId, username) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getUserResults?courseId=" +
          courseId + "&assignmentId=" + assignmentId + "&username=" + username, options);

        var value = res.content;
        Results.upsert({
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username
        }, {
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username,
          content: value
        });

      },
      getUserUploadedMd5: function(courseId, assignmentId, username) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getUploadedMd5?courseId=" +
          courseId + "&assignmentId=" + assignmentId, options);
        var value = res.content;

        Results.upsert({
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username
        }, {
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username,
          content: value
        });
      },
      getUserStorageDirContents: function(courseId, assignmentId, username) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getStorageDirContents?courseId=" +
          courseId + "&assignmentId=" + assignmentId, options);
        var value = res.content;

        Results.upsert({
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username
        }, {
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username,
          content: value
        });
      },
      getUserAssignmentFiles: function(courseId, assignmentId, username) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }

        // Get the files of the user
        var fs = Npm.require('fs');
        var folderPath = '/etc/vmchecker/config.list';
        var assignmentArchivePath = fs.readFileSync(folderPath);

        assignmentArchivePath = assignmentArchivePath.toString();

        // getting the assignment folder path
        var position = assignmentArchivePath.indexOf(courseId + ":") + courseId.length + 1;
        assignmentArchivePath = assignmentArchivePath.substr(position);
        position = assignmentArchivePath.indexOf('\n');
        assignmentArchivePath = assignmentArchivePath.substr(0, position).replace( /config/g, "repo") 
                            + "/" + assignmentId + "/" + username + "/current/archive.zip";

        console.log(assignmentArchivePath);

        Files.upsert({
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username
        },{
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username,
          content: fs.readFileSync(assignmentArchivePath)
        }
        );
      },
      getUserRepo : function ( userID, courseID, assignmentID) {
        this.unblock();

        var username = Meteor.users.find( {
          _id: this.userId
        }).profile.name;

        console.log(username);
      }
    });

    /// <<<=== END SERVER METHODS

  });
}