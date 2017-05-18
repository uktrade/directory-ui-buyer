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
    var param = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var qs = document.location.search.replace("&amp;", "&");
    var regex = new RegExp("[\\?&]" + param + "=([^&#]*)");
    var results = regex.exec(qs);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  }
  
  /* Try to dynamically generate a unique String value.
   **/
  this.uniqueString = function() {
    return "_" + ((new Date().getTime()) + "_" + Math.random().toString()).replace(/[^\w]*/mig, "");
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
  var utils = GOVUK.utils;
  
  this.set = function() {
    // params = [utm_campaign|utm_content|utm_medium|utm_source\utm_term]
    var params = document.location.search.match(/utm_[a-z]+/g) || [];
    var domain = document.getElementById("utmCookieDomain");
    var config = { days: 7 };
    var data = {};
    var json, value;
    
    if(domain) {
      config.domain = domain.getAttribute("value");
    }
    
    // 1. Does not add empty values.
    for(var i=0; i<params.length; ++i) {
      value = utils.getParameterByName(params[i]);
      if(value) {
        data[params[i]] = value;
      }
    }
    
    json = JSON.stringify(data);
    if(json.length > 2) { // ie. not empty
      GOVUK.cookie.set("ed_utm", json, config);
    }
  }

  this.get = function() {
    var cookie = GOVUK.cookie.get("ed_utm");
    return cookie ? JSON.parse(cookie) : null;
  }
  
});


/* 
  General data storage and display methods
  ======================================== */
GOVUK.data = {}
GOVUK.data.companiesHouse = (new function() {

  /* Performs a lookup of companies by name.
   **/
  this.getByNameData = {}; // Stores results
  this.getByNameRequest = null; // Allow access to request
  this.getByName = function(term) {
    if(this.getByNameRequest) this.getByNameRequest.abort();
    this.getByNameRequest = $.ajax({
      url: "/api/internal/companies-house-search/",
      data: "term=" + term,
      method: "GET",
      success: function(data) {
        GOVUK.data.companiesHouse.getByNameData = data;
      }
    });
    
    return this.getByNameRequest;
  }
  
});

/* 
  General effects
  ======================= */
GOVUK.components = (new function() {
  
  /* Performs a data lookup and displays multiple choice results
   * to populate the input value (or specificed alternative field)
   * with user choice. 
   *
   * @$input (jQuery node) Target input element
   * @request (Function) Returns reference to the jqXHR requesting data
   * @content (Function) Returns content to populate the dropdown 
   *
   * TODO - Add some Aria attributes...
   **/
  this.SelectiveLookup = SelectiveLookup;
  function SelectiveLookup($input, request, content, options) {
    var instance = this;
    
    // Configure options.
    opts = $.extend({
      lookupOnCharacter: 4, // (Integer) At what character input to trigger the request for data
    }, options || {});
    
    // Some inner variable requirement.
    instance._private = {
      content: content,
      request: request,
      $display: $("<div class=\"SelectiveLookupDisplay\"></div>"),
      $input: $input
    }
    
    // Will not have arguments if being inherited for prototype
    if(arguments.length >= 3) {
      
      // Bind main event.
      $input.on("input.SelectiveLookup", function() {
        if(this.value.length >= opts.lookupOnCharacter) {
          instance.search(this.value);
        }
      });
    
      // Add display element
      $(document.body).append(instance._private.$display);
    
      // Register the instance
      SelectiveLookup.instances.push(this);
      
      // A little necessary visual calculating.
      $(window).on("resize", function() {
        instance.setSizeAndPosition();
      });
    }
    
  }
  
  SelectiveLookup.prototype = {};
  SelectiveLookup.prototype.bindContentEvents = function() {
    var instance = this;
    instance._private.$display.off("click.SelectiveLookupContent");
    instance._private.$display.on("click.SelectiveLookupContent", function(event) {
      instance._private.$input.val($(event.target).text());
    });
  }
  SelectiveLookup.prototype.close = function() {
    // TODO: Add Aria stuff...
    this._private.$display.css({
      display: "none"
    });
  }  
  SelectiveLookup.prototype.search = function(params) {
    var instance = this;
    instance._private.request(params).done(function() {
      instance.setContent(instance._private.content());
      instance.bindContentEvents();
      instance.open();
    });
  }
  SelectiveLookup.prototype.setContent = function(content) {
    this._private.$display.empty().append(content);
  }
  SelectiveLookup.prototype.setSizeAndPosition = function() {
    var position = this._private.$input.offset();
    this._private.$display.css({
      left: parseInt(position.left) + "px",
      position: "absolute",
      top: (parseInt(position.top) + this._private.$input.outerHeight()) + "px",
      width: this._private.$input.outerWidth() + "px"
    });
  }
  SelectiveLookup.prototype.open = function() {
    // TODO: Add Aria stuff...
    this.setSizeAndPosition();
    this._private.$display.css({
      display: "block"
    });
  }
  
  
  SelectiveLookup.instances = [];
  SelectiveLookup.closeAll = function() {
    for(var i=0; i<SelectiveLookup.instances.length; ++i) {
      SelectiveLookup.instances[i].close();
    }
  }
  
  $(document.body).on("click.SelectiveLookupCloseAll", SelectiveLookup.closeAll);
  
  
  /* Extends SelectiveLookup to perform specific requirements
   * for Companies House company search by name, and resulting
   * form field population.
   **/
  this.CompaniesHouseNameLookup = CompaniesHouseNameLookup;
  function CompaniesHouseNameLookup($input, $field) {
    SelectiveLookup.call(this, 
      $input,
      GOVUK.data.companiesHouse.getByName,
      function() {
        var data = GOVUK.data.companiesHouse.getByNameData;
        var content = "<ul>";
        if(data) {
          for(var i=0; i<data.length; ++i) {
            content += "<li data-company-number=\"" + data[i].company_number + "\">" + data[i].title + "</li>";
          }
        }
        content += "</ul>";
        return content;
      }
    );
    
    // Some inner variable requirement.
    this._private.$field = $field || $input; // Allows a different form field to receive value.
  }
  CompaniesHouseNameLookup.prototype = new SelectiveLookup;
  CompaniesHouseNameLookup.prototype.bindContentEvents = function() {
    var instance = this;
    instance._private.$display.off("click.SelectiveLookupContent");
    instance._private.$display.on("click.SelectiveLookupContent", function(event) {
      var $selected = $(event.target);
      instance._private.$input.val($selected.text());
      instance._private.$field.val($selected.attr("data-company-number"));
    });
  }
});


/* 
  General effects
  ======================= */
GOVUK.effects = (new function() {
  
  /* Takes a target element and will populate with
   * a count from zero (opts.start) to end. 
   * @$target (jQuery node) Target element
   * @end (Number) Limit of counter
   * @options (Object) See defaults for what can be configured.
   **/
  this.Counter = Counter;
  function Counter($target, end) {
    var COUNTER = this;
    var limit = Number(end.replace(/[^\d]/, ""));
    
    function increment() {
      COUNTER.value += 33;
    }
    
    function update() {
      if(COUNTER.value > 999) {
        $target.text(String(COUNTER.value).replace(/(\d*)(\d{3})/, "$1,$2"));
      }
      else {
        $target.text(COUNTER.value);
      }
    }
    
    function activate() {
      var interval = setInterval(function() {
        increment();
        update();
        if(COUNTER.value >= limit) {
          clearInterval(interval);
          COUNTER.value = limit;
          update();
        }
      }, 10);
    }

    // If element exists start the effect.
    if($target.length) {
      COUNTER.value = 1;
      update();
      (new ScrollIntoViewStart($target, activate, true)).init();
    }
  }
  
  
  /* Scrolls element into view if not already visible.
   * @$element (jQuery node) Element to make visible
   * @offset (Number) Added to current left position to hide element offscreen
   * @leftToRight (Boolean) Whether elements come from left, or right.
   **/ 
  this.SlideIntoView = SlideIntoView;
  function SlideIntoView($element, offset, leftToRight) {
    var property = leftToRight ? "left": "right";
    var originalPosition = getPosition();
    function update(pos) {
      $element.css(property, pos + "px");
    }
    
    function getPosition() {
      return Number($element.css(property).replace("px", ""));
    }
    
    function activate() {
      var speed = 10;
      var increment = 10;
      var currentPosition = getPosition();
      var interval = setInterval(function() {
        if(originalPosition > currentPosition) {
          currentPosition += increment;
        }
        else {
          clearInterval(interval);
          currentPosition = originalPosition;
          $(window).on("resize", function() {
            // Reset to fall back to stylesheet
            // now we're done moving it.
            $element.get(0).style[property] = ""; 
          });
        }
        
        update(String(currentPosition));
      }, speed);
      
      $element.animate({
        opacity: 1
      });
    }
    
    // If element exists, then initially set 
    // it offscreen and start effect.
    if($element.length) {
      update(originalPosition - offset);
      (new ScrollIntoViewStart($element, activate, true)).init();
    }
  }
  
  
  /* Delays an action until the passed element is expected 
   * to be visible in the viewport.
   * @$element (jQuery node) Element that should be visible
   * @action (Function) What should happen if/when visible.
   **/
  function ScrollIntoViewStart($element, action) {
    var disabledScrollActivator = false; // In case element is not visible on start.
    var done = false; // It's run one time only.
    var unique = GOVUK.utils.uniqueString();
    
    
    // Test to see if can activate action.
    function tryToRun() {
      if(!done) {
        if(isVisible()) {
          $(window).off("scroll.event" + unique);
          done = true;
          action();
        }
        else {
          if(!disabledScrollActivator) {
            disabledScrollActivator = true;
            $(window).on("scroll.event" + unique, function() {
              tryToRun();
            });
          }
        }
      }
    }
    
    // Figure out if we can see enough of the element.
    function isVisible() {
      var visibleBase = window.scrollY + $(window).innerHeight();
      var elementBase = $element.offset().top + $element.height();
      // 40 is arbitrary number that should be small
      // enough difference to guess element is visible. 
      return elementBase - visibleBase < 40;
    }
    
    // Control kick off.
    this.init = function() {
      tryToRun();
    }
  }
  
});



/* In test mode we don't want the code to 
 * run immediately because we have to compensate
 * for not having a browser environment first.
 **/ 
GOVUK.page = (new function() {
  
  // What to run on every page (called from <body>).
  this.init = function() {
    captureUtmValue();
    setupFactCounterEffect();
    setupHomeScreenshotEffect();
    setupCompaniesHouseLookup();
  }
  
  /* Attempt to capture UTM information if we haven't already
   * got something and querystring is not empty.
   **/
  function captureUtmValue() {
    var captured = GOVUK.utm.get();
    if(!captured && document.location.search.substring(1)) {
      GOVUK.utm.set();
    }
  }
  
  /* Gets any fact element and turns into a dynamic
   * counter effect to rapidly count up to the amount.
   **/
  function setupFactCounterEffect() {
    var $fact = $(".fact");
    var $figure = $fact.find(".figure");
    new GOVUK.effects.Counter($figure, $figure.text());
  }
  
  /* Find and apply a scroll in effect to specified element.
   **/
  function setupHomeScreenshotEffect() {
    new GOVUK.effects.SlideIntoView($("#fabhome-screenshot"), 550);
  }
  
  /* Add Companies House name lookup AJAX functionality.
   **/
  function setupCompaniesHouseLookup() {
    // TODO: refactor ED-1411
    $(".register-company-number-form").each(function() {
      var $input = $("input[name='company-number-company_number']", this);
      var $field = $("<input type=\"hidden\" name=\"company_number\" />");
      var $label = $(".label", this);
      // Posting to the current page to run validation.
      // Server will redirect to the single step enrolment form if validation passes.
      $(this).attr("action", "");

      // Some content updates.
      $input.attr("placeholder", "Companies name");
      $label.text("Enter your company name");
      
      // Some structural changes to form.
      $input.attr("name", "company_name");
      $("input[name='enrolment_view-current_step']", this).remove();
      $(this).prepend($field);
      
      // Now apply JS lookup functionality.
      new GOVUK.components.CompaniesHouseNameLookup($input, $field);
    });
  }

});
