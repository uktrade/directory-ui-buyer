var GOVUK = GOVUK || {};

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
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  }

  /* Merge two objects (obj2 into obj1) - overwrites existing values.
   * @obj1 (Object) Object to be altered
   * @obj2 (Object) Object containing properties to add
   * e.g.
   * GOVUK.utils.merge({foo:'foo'}, {bar:'bar'});
   * returns {foo:'foo', bar:'bar'}
   **/
  this.merge = function(obj1, obj2) {
    for(var o in obj2) {
      if(obj2.hasOwnProperty(o)) {
        obj1[o] = obj2[o];
      }
    }
    return obj1;
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
    var opts = GOVUK.utils.merge({
      domain: null // Set a domain value (e.g. exclude sub domain).
    }, options || {});
    
    var cookieString = name + "=" + value + "; path=/";
    var domain, domainSplit;

    if (opts.days) {
      var date = new Date();
      date.setTime(date.getTime() + (opts.days * 24 * 60 * 60 * 1000));
      cookieString = cookieString + "; expires=" + date.toGMTString();
    }

    if(opts.domain) {
      cookieString += ";domain=" + opts.domain + ";path=/"
    }
  
    if (document.location.protocol == 'https:'){
      cookieString = cookieString + "; Secure";
    }
  
    document.cookie = cookieString;
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
  GOVUK.cookie.set();

  Reading stored values:
  GOVUK.cookie.get();
*/
GOVUK.utm = (new function() {
  var COOKIE_NAME = "ed_utm";
  var UTILS = GOVUK.utils;
  
  /* Store the data
   * @options (Object) Configurable information.
   **/
  this.set = function(options) {
    var opts = UTILS.merge({
      days: 7 // Defatult days to keep the cookie.
    }, options || {});
    
    var utmData = {
      utm_campaign: UTILS.getParameterByName("utm_campaign"),
      utm_content: UTILS.getParameterByName("utm_content"),
      utm_medium: UTILS.getParameterByName("utm_medium"),
      utm_source: UTILS.getParameterByName("utm_source"),
      utm_term: UTILS.getParameterByName("utm_term")
    };

    var domain = document.getElementById("utmCookieDomain");
    if(domain) {
      opts.domain = domain.getAttribute("value");
    }
    
    GOVUK.cookie.set(COOKIE_NAME, JSON.stringify(utmData), opts);
  }

  this.get = function() {
    return GOVUK.cookie.get(COOKIE_NAME);
  }
  
});

// Run immediately.
if(GOVUK) {
  GOVUK.utm.set();
}
