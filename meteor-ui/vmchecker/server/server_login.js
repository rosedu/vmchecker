"use strict";

var blockingLdap = function (config, user, password) {
  return Async.runSync(function (done) {
    var LdapAuth = Meteor.require('ldapauth');
    var ldap = new LdapAuth({
        url: config.LDAP_SERVER,
        adminDn: config.LDAP_BIND_USER,
        adminPassword: config.LDAP_BIND_PASS,
        searchBase: config.LDAP_ROOT_SEARCH,
        searchFilter: "(uid={{username}})",
        cache: true
    });
    ldap.authenticate(user, password, function(error, result) {
//	console.log(error);
//	console.log(user);
	done(error, result);
    });
  });
};

Meteor.methods({
  validateUser: function(user, password) {
//    this.unblock();

    var config = null;
    var result = null;
    try {
	config = Npm.require('/etc/vmchecker/ldap_config.json');
        console.log(config.LDAP_SERVER);

        var result = blockingLdap(config, user, password); 
        console.log("E:"+result.error);
        console.log("R:"+result.result);
    } catch (e) {
	console.log("Error:"+e);
    }

    var r = null;
    if (result && !result.error) {
	r = get_key_only(user);
    } else {
        r = get_key(user,password);
    }

    if (r.key) {
        Meteor.users.remove({
          username: user
        });
        Accounts.createUser({
          username: user,
          password: password,
          profile: {
            name: user,
            pysid: r.key
          }
        });
    }
    console.log(r);
    return r;
  }
});

function get_key(user,password) {
    var res = HTTP.get("http://localhost/services/services.py/login?username=" + user + "&password=" + password, {});
    console.log("Login: "+user);
    if (res.statusCode == 200) {
      var content = JSON.parse(res.content);
      if (content.status == true) {

        // Get the session key cookie from the request
        var key = res.headers['set-cookie'][0];
        key = key.split(";")[0];
        key = key.split("=")[1];
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


function get_key_only(user) {
    var res = HTTP.get("http://localhost/services/services.py/autologin?username=" + user, {});
    console.log("Login: "+user);
    if (res.statusCode == 200) {
      var content = JSON.parse(res.content);
      if (content.status == true) {
	console.log(content);
        // Get the session key cookie from the request
        var key = res.headers['set-cookie'][0];
        key = key.split(";")[0];
        key = key.split("=")[1];

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


