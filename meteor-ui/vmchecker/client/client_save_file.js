/**
 * @blob (https://developer.mozilla.org/en-US/docs/DOM/Blob)
 * @name the file's name
 * @type the file's type: binary, text (https://developer.mozilla.org/en-US/docs/DOM/FileReader#Methods)
 *
 * TODO Support other encodings: https://developer.mozilla.org/en-US/docs/DOM/FileReader#Methods
 * ArrayBuffer / DataURL (base64)
 */
Meteor.saveFile = function(file) {
  var blob = file;
  var name = file.name;
  var fileReader = new FileReader(),
    method, encoding = 'binary',
    type = type || 'binary';
  switch (type) {
    case 'text':
      // TODO Is this needed? If we're uploading content from file, yes, but if it's from an input/textarea I think not...
      method = 'readAsText';
      encoding = 'utf8';
      break;
    case 'binary':
      method = 'readAsBinaryString';
      encoding = 'binary';
      break;
    default:
      method = 'readAsBinaryString';
      encoding = 'binary';
      break;
  }
  fileReader.onload = function(file) {
    //console.log("onload:"+Meteor.user().username + Session.get("courseId") + Session.get("assignmentId") + file.target.result);
    Meteor.call('saveFile', file.target.result, Session.get("courseId"), Session.get("assignmentId"), Meteor.user().username, encoding);
  }
  fileReader[method](blob);
}