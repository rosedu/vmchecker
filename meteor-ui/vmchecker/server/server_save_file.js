/**
 * TODO support other encodings:
 * http://stackoverflow.com/questions/7329128/how-to-write-binary-data-to-a-file-using-node-js
 */
Meteor.methods({
  saveFile: function(blob, courseId, assignmentId, userId, encoding) {
    this.unblock();

    if (this.userId == null)
      return;

    var key = Meteor.users.findOne({
      _id: this.userId
    }).profile.pysid;

    var d = new Date();
    var time = d.getTime();


    var random = Math.floor(Math.random() * 10000 + 1);
    var name = 'submission_' + random.toString(16) + "_" + time + ".zip";
    var path = Npm.require('path'),
      name = cleanName(name || 'file'),
      encoding = encoding || 'binary',
      chroot = Meteor.chroot || 'public';
    // Clean up the path. Remove any initial and final '/' -we prefix them-,
    // any sort of attempt to go to the parent directory '..' and any empty directories in
    // between '/////' - which may happen after removing '..'
    var fs = Npm.require('fs');
    __ROOT_APP_PATH__ = fs.realpathSync('.');
    console.log(__ROOT_APP_PATH__);
    var filepath = path.join("/tmp", name);
    // // TODO Add file existance checks, etc...
    fs.writeFileSync(filepath, blob, encoding);

    console.log('The file ' + name + ' (' + encoding + ') was saved to ' + filepath);

    var options = {
      headers: {
        Cookie: "pysid=" + key
      }
    }
    var res = HTTP.get("http://localhost/services/services.py/uploadedFile?courseId=" +
      courseId + "&assignmentId=" + assignmentId + "&tmpname=" + filepath, options);

    var value = res.content;
    console.log(value);

    fs.unlinkSync(filepath);


    function cleanPath(str) {
      if (str) {
        return str.replace(/\.\./g, '').replace(/\/+/g, '').
        replace(/^\/+/, '').replace(/\/+$/, '');
      }
    }

    function cleanName(str) {
      return str.replace(/\.\./g, '').replace(/\//g, '');
    }
  }
});