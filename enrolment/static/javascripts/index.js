var GOVUK = {};

/* 
  General utility methods
  ======================= */
GOVUK.utils = (new function() {

  /* Parse the URL to retrieve a value.
   * @name (String) Name of URL param
   * e.g.
   * GOVUK.utils.getParameterByName('a_param');
   **/
  this.getParameterByName = function(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&amp;]" + name + "=([^&amp;#]*)"),
        results = regex.exec(document.location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  }
});

/*
  Cookie methods
  ==============
  Setting a cookie:
  GOVUK.cookie.set('hobnob', 'tasty', { days: 30 });

  Reading a cookie:
  GOVUK.cookie.get('hobnob');

  Deleting a cookie:
  GOVUK.cookie.set('hobnob', null);
*/
GOVUK.cookie = (new function() {

  /* Set a cookie.
   * @name (String) Name of cookie
   * @value (String) Value to store
   * @options (Object) Optional configurations
   **/
  this.set = function(name, value, options) {
    var opts = options || {};
    var str = name + "=" + value + "; path=/";
    var domain, domainSplit;
    if (opts.days) {
      var date = new Date();
      date.setTime(date.getTime() + (opts.days * 24 * 60 * 60 * 1000));
      str += "; expires=" + date.toGMTString();
    }

    if(opts.domain) {
      str += "; domain=" + opts.domain;
    }

    if (document.location.protocol == 'https:'){
      str += "; Secure";
    }
    
    document.cookie = str;
  }
  
 /* Read a cookie
  * @name (String) Name of cookie to read.
  **/
  this.get = function(name) {
    var nameEQ = name + "=";
    var cookies = document.cookie.split(';');
    var value;

    for(var i = 0, len = cookies.length; i < len; i++) {
      var cookie = cookies[i];
      while (cookie.charAt(0) == ' ') {
        cookie = cookie.substring(1, cookie.length);
      }
      if (cookie.indexOf(nameEQ) === 0) {
        value = decodeURIComponent(cookie.substring(nameEQ.length));
      }
    }
    return value;
  }

  /* Delete a cookie.
   * @name (String) Name of cookie
   **/
  this.remove = function(name) {
    this.set(name, null);
  }

});

/*
  UTM value storage
  =================
  Store values from URL param:
  GOVUK.utm.set();

  Reading stored values:
  GOVUK.utm.get();
*/
GOVUK.utm = (new function() {
  var UTILS = GOVUK.utils;
  
  this.set = function() {
    var domain = document.getElementById("utmCookieDomain");
    var data = {
      utm_campaign: UTILS.getParameterByName("utm_campaign"),
      utm_content: UTILS.getParameterByName("utm_content"),
      utm_medium: UTILS.getParameterByName("utm_medium"),
      utm_source: UTILS.getParameterByName("utm_source"),
      utm_term: UTILS.getParameterByName("utm_term")
    };

    if(domain) {
      domain = domain.getAttribute("value");
    }
    
    GOVUK.cookie.set("ed_utm", JSON.stringify(data), { days: 7 });
  }

  this.get = function() {
    var cookie = GOVUK.cookie.get("ed_utm");
    var data = JSON.parse(cookie);
    return data;
  }
  
});

/* In test mode we don't want the code to 
 * run immediately because we have to compensate
 * for not having a browser environment first.
 **/ 
GOVUK.page = (new function() {
  
  // Run on every page (called from <body>).
  this.init = function() {
    GOVUK.utm.set();
  }
});

/* GOVUK is a global variable, so will be placed on
 * the window object in a browser environment. Since
 * we are using 'require()' in test environment, the
 * GOVUK will be scoped to the required module.
 * The (otherwise pointless) use of window.GOVUK 
 * statement will trigger the catch in test 
 * environment thus, ensuring the GOVUK will be 
 * exposed for testing purpose.
 **/
try {
  window.GOVUK = GOVUK;
}
catch(e) {
  module.exports = GOVUK;
}