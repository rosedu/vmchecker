"use strict";

var Courses = new Meteor.Collection("courses");
var Assignments = new Meteor.Collection("assignments");
var Grades = new Meteor.Collection("grades");
var Results = new Meteor.Collection("results");

// Restricts creating accounts on the client
Accounts.config({forbidClientAccountCreation: true});


if (Meteor.isClient) {

    i18n.init(
      {
        lng: Cookie.get("i18next") || "en",
        debug: true,
        preload: ['en', 'ro'],
        fallbackLng: 'en',
        useLocalStorage: true,
        load: 'current',
        getAsync: false
      },
      function(t) {
        console.log("got lng:" + Cookie.get("i18next") || "en");

        Handlebars.registerHelper('t', function(i18n_key) {
          var result = i18n.t(i18n_key);
          console.log("---"+result);
          return new Handlebars.SafeString(result);
        });

        Handlebars.registerHelper('tt', function(i18n_key) {
          var result = '"'+i18n.t(i18n_key)+'"';
          console.log("---"+result);
          return new Handlebars.SafeString(result);
        });
      }
    );


  Deps.autorun(function () {
    Meteor.subscribe("courses");
    Meteor.subscribe("assignments");
    Meteor.subscribe("grades");
    Meteor.subscribe("userData");
    Meteor.subscribe("results");
  });

  Meteor.call('getCourses', function() {
    var firstCourse = Courses.findOne({});
    Session.setDefault("courseId", firstCourse.courseId);
  });


  Template.courses.courses = function () {
    return Courses.find({}, {sort: {id: -1, title: 1}});
  };

  Template.courses.events({
    'change' : function (event) {
      var elem = event.currentTarget;
      Session.set("courseId", elem.value);
      Meteor.call('getAssignments', Session.get("courseId"));
      Meteor.call('getAllGrades', Session.get("courseId"));
    }
  });

  Template.changeLang.events({
    'change' : function (event) {
      if (Cookie.get("i18next") != event.currentTarget.value) {
        Cookie.set("i18next",event.currentTarget.value);
        history.go(0);
      }
    }
  });

  Template.changeLang.languages = function() {
    // TODO: use database maybe?
    return [
      {
        "code": "ro",
        "name": "Romana",
        "selected": (Cookie.get('i18next')=="ro" ? "selected" : "")
      },
      {
        "code":"en",
        "name":"Engleza",
        "selected": (Cookie.get('i18next')=="en" ? "selected" : "")
      }
    ];
  }

  Template.assignments.assignments = function() {
    return Assignments.find({courseId: Session.get("courseId")});
  };

  Template.assignments.events({
    'click': function (event) {
      var text = event.currentTarget.id;
      Session.set("assignmentId", text.trim());
      Meteor.call(
        'getUserResults',
        Session.get('courseId'),
        Session.get('assignmentId'),
        Meteor.user().username
      );
      console.log("---"+Session.get("assignmentId"));
    }
  });


  Template.assignmentInfo.content = function() {
    return Assignments.find({
      courseId: Session.get("courseId"),
      assignmentId: Session.get("assignmentId")
    });
  }

  Template.grades.grades = function() {
    return Grades.find(
      {courseId: Session.get("courseId")},
      {sort: {studentId: -1}, limit: 10}
    );
  }

  Template.grades.display = function() {
    return Session.get("assignmentId") == "";
  }

  Template.result.content = function() {
    if (Meteor.user()) {
      var val = Results.findOne({
        courseId: Session.get('courseId'),
        assignmentId: Session.get('assignmentId'),
        userId: Meteor.user().username
      }).content;
      console.log(val);
      return JSON.stringify(val);
    }
    return "";
  }

Template.login.events({
    'submit #login-form' : function(e, t){
      e.preventDefault();
      // retrieve the input field values
      var email = t.find('[name=email]').value
        , password = t.find('[name=password]').value;

        // Trim and validate your fields here.... 

        console.log(JSON.stringify(Meteor.users.find({username: email})));
        Session.set('loading', true);
        Meteor.call('validateUser', email, password);

        setTimeout(function() {
          Meteor.loginWithPassword(email, password, function(err){
          Session.set('loading', false);
          if (err)
            console.log(JSON.stringify(err));
            // The user might not have been found, or their passwword
            // could be incorrect. Inform the user that their
            // login attempt has failed. 
          else
            console.log("no error");
            // The user has been logged in.
          });
        }, 3000);
        // If validation passes, supply the appropriate fields to the
        // Meteor.loginWithPassword() function.
        
         return false;
      }
  });

Template.circle.display = function (league) {
  return Session.get("loading") == true;
};

}


if (Meteor.isServer) {
  Meteor.users.remove({});
  Meteor.startup(function () {
    console.log("Started server");

    Meteor.publish("grades", function () {
      return Grades.find({});
    });
    Meteor.publish("courses", function () {
      return Courses.find({});
    });
    Meteor.publish("assignments", function () {
      return Assignments.find({});
    });
    Meteor.publish("userData", function () {
      return Meteor.users.find({});
    });
    Meteor.publish("results", function () {
      return Results.find({});
    });

/// ===>>> SERVER METHODS

var do_rpc = function(method, args, callback) {
  console.log("Calling "+method+"("+args+")");
  var xmlrpc = Meteor.require("xmlrpc");
  var client = new xmlrpc.createClient({
    host: 'vmchecker.cs.pub.ro',
    port: 9090, path: '/'
  });
  client.methodCall(method, args, Meteor.bindEnvironment(
    callback,
    function(e) {
      console.log("Error in calling: "+method+"("+args+"):"+e);
    }));
}

Meteor.methods({
  validateUser: function(user, password) {
    this.unblock();
    do_rpc('login', [user, password], function(error, value) {
      var result = JSON.parse(value);
      if (result.status) {
        console.log(result);
        Meteor.users.remove({username: user});
        Accounts.createUser({
          username: user,
          password: password,
          profile: {name: result.username}
        });
      } else
        console.log("Login result: "+value);
    });
  },
  getCourses: function() {
    this.unblock();
    do_rpc('getCourses', [], function(error,value) {
        console.log(value);
        var names = JSON.parse(value);
        // TODO: handle error json
        for (var i = 0; i < names.length; i++) {
          Courses.update(
            {id: names[i].id},
            {id: names[i].id, title: names[i].title},
            {upsert: true}
          );
          console.log("adding "+names[i].id);
        }
      });
  },
  getAssignments: function(courseId) {
    this.unblock();
    do_rpc('getAssignments', [courseId], function(error, value) {
      console.log(courseId);
      console.log(value);
      var assignments = JSON.parse(value);
      for (var i = 0; i < assignments.length; i++) {
        Assignments.update(
          {
            courseId: courseId,
            assignmentId: assignments[i].assignmentId
          },
          {
            courseId: courseId,
            assignmentId: assignments[i].assignmentId,
            assignmentTitle: assignments[i].assignmentTitle,
            deadline: assignments[i].deadline,
            statementLink: assignments[i].statementLink,
            assignmentStorage: assignments[i].assignmentStorage
          },
          {
            upsert: true
          }
        );
      }
    });
  },
  getAllGrades: function(courseId) {
    this.unblock();
    do_rpc('getAllGrades', [courseId], function(error, value) {
      console.log(courseId);
      console.log(value);
      var students = JSON.parse(value);
      for (var i = 0; i < students.length; i++) {
        for (var assignmentId in students[i].results) {
          Grades.update(
            {
              courseId: courseId,
              studentId: students[i].studentId,
              assignmentId: assignmentId
            },
            {
              courseId: courseId,
              studentId: students[i].studentId,
              assignmentId: assignmentId,
              grade: students[i].results[assignmentId]
            },
            {
              upsert: true
            }
          );
        }
      }
    });
  },
  getUserResults: function(courseId, assignmentId, username) {
    this.unblock();
    do_rpc(
      'getUserResults',
      [courseId, assignmentId, username],
      function(error, value) {
        console.log(courseId);
        console.log(value);
        Results.upsert(
          {
            courseId: courseId,
            assignmentId: assignmentId,
            userId: username
          },
          {
            courseId: courseId,
            assignmentId: assignmentId,
            userId: username,
            content: value
          }
        );
        console.log(Results.find({}).count());
    });
  },
  getUserUploadedMd5: function(courseId, assignmentId, username) {
    this.unblock();
    do_rpc(
      'getUserUploadedMd5',
      [courseId, assignmentId, username],
      function(error, value) {
        console.log(courseId);
        console.log(value);
        Results.upsert(
          {
            courseId: courseId,
            assignmentId: assignmentId,
            userId: username
          },
          {
            courseId: courseId,
            assignmentId: assignmentId,
            userId: username,
            content: value
          }
        );
    });
  },
  getUserStorageDirContents: function(courseId, assignmentId, username) {
    this.unblock();
    console.log(value);
    do_rpc(
      'getUserStorageDirContents',
      [courseId, assignmentId, username],
      function(error, value) {
        Results.upsert(
          {
            courseId: courseId,
            assignmentId: assignmentId,
            userId: username
          },
          {
            courseId: courseId,
            assignmentId: assignmentId,
            userId: username,
            content: value
          }
        );
      }
    );
  }
});

/// <<<=== END SERVER METHODS

  });
}
