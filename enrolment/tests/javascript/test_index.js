var jsdom = require('jsdom').jsdom;
var expect = require('chai').expect;
var assert = require('chai').assert;
var url = "http://buyer.trade.great.dev";
var port = ":8001";
var querystring = "?utm_campaign=test1&utm_content=test2&utm_medium=test3&utm_source=test4&utm_term=test5";
var html = "\
<!doctype html> \
<html> \
  <body> \
    <div> \
    </div> \
  </body> \
</html> \
";

// TODO: jsDom Documentation indicates HTML can be fetched. 
var GOVUK = require('../../static/javascripts/index.js');
var window = jsdom(html, { 
  url: url + port + querystring 
}).defaultView;

global.document = window.document;
global.document.tdd = true;


describe('GOVUK', function() {
  it('should exist', function() {
    assert.ok(GOVUK);
  });

  it('should contain utils', function() {
    assert.ok(GOVUK.utils);
  });

  it('should contain cookie', function() {
    assert.ok(GOVUK.cookie);
  });

  it('should contain utm', function() {
    assert.ok(GOVUK.utm);
  });
});
    

describe('GOVUK.utils', function() {
  
  describe('getParameterByName', function() {
    it('should exist', function() {
      assert.ok(GOVUK.utils.getParameterByName);
    });

    it('should retrieve value from single param', function() {
      assert.equal(GOVUK.utils.getParameterByName('utm_campaign'), 'test1');
    });

    it('should retrieve different values from different params', function() {
      assert.equal(GOVUK.utils.getParameterByName('utm_campaign'), 'test1');
      assert.equal(GOVUK.utils.getParameterByName('utm_content'), 'test2');
      assert.equal(GOVUK.utils.getParameterByName('utm_medium'), 'test3');
    });

  });

});


describe('GOVUK.cookie', function() {
  
  describe('set', function() {
    it('should exist', function() {
      assert.ok(GOVUK.cookie.set);
    });
    
    it('should write cookie by name', function() {
      GOVUK.cookie.set("foo", "bar");
      assert.equal(GOVUK.cookie.value, "foo=bar; path=/");
    });
    
    it('should write cookie with expiry', function() {
      GOVUK.cookie.set("foo", "bar", {
        days: 2
      });
      
      // Not doing anything complicated. Adding a date would put
      // the 'expires' in cookie string so just checking exists.
      assert.ok(GOVUK.cookie.value.includes("expires"));
    });
    
    it('should write cookie domain', function() {
      GOVUK.cookie.set("foo", "bar", {
        domain: "trade.great.dev"
      });
      assert.ok(GOVUK.cookie.value.includes("domain=trade.great.dev"));
    });
    
    /* TODO: Need to alter the location.protocol
    it('should write cookie protocol', function() {
      document.location.protocol = 'https:';
      GOVUK.cookie.set("foo", "bar");
      console.log("GOVUK.cookie.value: ", GOVUK.cookie.value)
      assert.ok(GOVUK.cookie.value.includes("Secure"));
    });
    */
  });

  describe('get', function() {
    it('should exist', function() {
      assert.ok(GOVUK.cookie.get);
    });
    
    it('should read cookie by name', function() {
      var cookie = GOVUK.cookie.get("foo");
      assert.equal(cookie, "bar");
    });
  });

});

describe('GOVUK.utm', function() {
  
  describe('set', function() {
    it('should exist', function() {
      assert.ok(GOVUK.utm.set);
    });
    
    it('should store utm param values', function() {
      GOVUK.utm.set();
      
      assert.ok(document.cookie.includes("utm_campaign"));
      assert.ok(document.cookie.includes("utm_content"));
      assert.ok(document.cookie.includes("utm_medium"));
      assert.ok(document.cookie.includes("utm_source"));
      assert.ok(document.cookie.includes("utm_term"));
    });

  });

  describe('get', function() {
    it('should exist', function() {
      assert.ok(GOVUK.utm.get);
    });
    
    it('should return stored utm param values', function() {
      var data = GOVUK.utm.get();
      
      assert.equal(data.utm_campaign, "test1");
      assert.equal(data.utm_content, "test2");
      assert.equal(data.utm_medium, "test3");
      assert.equal(data.utm_source, "test4");
      assert.equal(data.utm_term, "test5");
    });
  });

});

