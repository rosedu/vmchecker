"use strict";

Meteor.methods({
  validateUser: function(user, password) {
    this.unblock();

    var res = HTTP.get("http://localhost/services/services.py/login?username=" + user + "&password=" + password, {});
    console.log("Login: "+user);
    if (res.statusCode == 200) {
      var content = JSON.parse(res.content);
      if (content.status == true) {

        // Get the session key cookie from the request
        var key = res.headers['set-cookie'][0];
        key = key.split(";")[0];
        key = key.split("=")[1];

        Meteor.users.remove({
          username: user
        });
        Accounts.createUser({
          username: user,
          password: password,
          profile: {
            name: content.username,
            pysid: key
          }
        });

        return {
          "result": true,
          "key": key
        };
      }
      console.log(content);
    }

    console.log(res);
    return {
      "result": true,
      "key": null
    };
  }
});