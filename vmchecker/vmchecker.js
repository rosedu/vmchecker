Courses = new Meteor.Collection("courses");
Assignments = new Meteor.Collection("assignments");
Grades = new Meteor.Collection("grades");


// Restricts creating accounts on the client
Accounts.config({forbidClientAccountCreation: true});

if (Meteor.isClient) {

  Meteor.call('getCourses');
  Template.courses.courses = function () {
    return Courses.find({}, {sort: {id: -1, title: 1}});
  };


  Template.hello.greeting = function () {
    return "Welcome to vmchecker.";
  };

  Template.hello.events({
    'click' : function () {
      // template data, if any, is available in 'this'
      Meteor.call('getAssignments', Session.get("courseId"));
    }
  });

  Template.courses.events({
    'change' : function (event) {
      var elem = event.currentTarget;
      Session.set("courseId", elem.value);
      Meteor.call('getAssignments', Session.get("courseId"));
      Meteor.call('getAllGrades', Session.get("courseId"));
    }
  });

  Template.assignments.assignments = function() {
    return Assignments.find({courseId: Session.get("courseId")});
  };

  Template.assignments.events({
    'click': function (event) {
      var text = event.currentTarget.innerHTML;
      // TODO this is not actual text, but a html object
      // Fixme!!!
      Session.set("assignmentId", String.trim(text));
      console.log(Session.get("assignmentId"));
    }
  });

  Template.assignmentInfo.content = function() {
    return Assignments.find({courseId: Session.get("courseId"), assignmentId: Session.get("assignmentId")});
  }

  Template.grades.grades = function() {
    return Grades.find({courseId: Session.get("courseId")}, {sort: {studentId: -1}});
  }

Template.login.events({
    'submit #login-form' : function(e, t){
      e.preventDefault();
      // retrieve the input field values
      var email = t.find('#login-email').value
        , password = t.find('#login-password').value;

        // Trim and validate your fields here.... 
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
            console.log("error");
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
  Meteor.startup(function () {
    console.log("Started server");

/// ===>>> SERVER METHODS

var do_rpc = function(method, args, callback) {
  console.log("Calling "+method+"("+args+")");
  var xmlrpc = Meteor.require("xmlrpc");
  var client = new xmlrpc.createClient({ host: 'vmchecker.cs.pub.ro', port: 9090, path: '/'});
  client.methodCall(method, args, Meteor.bindEnvironment(
    callback,
    function(e) {
      console.log("Error in calling: "+method+"("+args+")");
    }));
}

Meteor.methods({
  validateUser: function(user, password) {
    do_rpc('login', [user, password], function(error, value) {
      var result = JSON.parse(value);
      if (result.status)
        Accounts.createUser({ username: user, password: password });
      else
        console.log("Login result: "+value);
    });
  },
  getCourses: function() {
    do_rpc('getCourses', [], function(error,value) {
        console.log(value);
        var names = JSON.parse(value);
        // TODO: handle error json
        for (var i = 0; i < names.length; i++) {
          Courses.update({ id: names[i].id }, { id: names[i].id, title: names[i].title }, { upsert: true });
          console.log("adding "+names[i].id);
        }
      });
  },
  getAssignments: function(courseId) {
    do_rpc('getAssignments', [courseId], function(error, value) {
      console.log(courseId);
      console.log(value);
      var assignments = JSON.parse(value);
      for (var i = 0; i < assignments.length; i++) {
        Assignments.update({ courseId: courseId, assignmentId: assignments[i].assignmentId}, 
                          { courseId: courseId, assignmentId: assignments[i].assignmentId, assignmentTitle: assignments[i].assignmentTitle, deadline: assignments[i].deadline, statementLink: assignments[i].statementLink, assignmentStorage: assignments[i].assignmentStorage}, { upsert: true });
      }
    });
  },
  getAllGrades: function(courseId) {
    do_rpc('getAllGrades', [courseId], function(error, value) {
      console.log(courseId);
      console.log(value);
      var students = JSON.parse(value);
      for (var i = 0; i < students.length; i++)
        for (var assignmentId in students[i].results)
          Grades.update({courseId: courseId, studentId: students[i].studentId, assignmentId: assignmentId},
            {courseId: courseId, studentId: students[i].studentId, assignmentId: assignmentId, grade: students[i].results[assignmentId]},
            { upsert: true });
    });
  }
});

/// <<<=== END SERVER METHODS

  });
}
