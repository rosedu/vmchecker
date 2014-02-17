i18n.init({
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
      console.log("---" + result);
      return new Handlebars.SafeString(result);
    });

    Handlebars.registerHelper('tt', function(i18n_key) {
      var result = '"' + i18n.t(i18n_key) + '"';
      console.log("---" + result);
      return new Handlebars.SafeString(result);
    });
  }
);