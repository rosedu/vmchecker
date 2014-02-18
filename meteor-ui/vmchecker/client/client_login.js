"use strict";

Template.login.events({
  'submit #login-form': function(e, t) {
    e.preventDefault();
    // retrieve the input field values
    var username = t.find('[name=username]').value,
      password = t.find('[name=password]').value;

    // Trim and validate your fields here.... 

    console.log(JSON.stringify(Meteor.users.find({
      username: username
    })));
    Session.set('loading', true);

    Meteor.call('validateUser', username, password, function(error, result) {
      if (error) {
        console.log("Login error:" + result);
      } else {
        if (result.result == true)
          console.log("Key: " + result.key);
      }

      Meteor.loginWithPassword(username, password, function(err) {
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
    });

    return false;
  }
});