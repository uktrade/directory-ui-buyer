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
  General data storage and services
  =================================== */
GOVUK.data = (new function() {

  function Service(url, configuration) {
    var service = this;
    var config = $.extend({
      url: url,
      method: "GET",
      success: function(response) {
        service.response = response;
      }
    }, configuration || {});
    
    var listeners = [];
    var request; // Reference to active update request
    
    service.response = {}; // What we get back from an update
    
    /* Gets a fresh response
     * @params (String) Specify params for GET or data for POST
     **/
    service.update = function(params) {
      if(request) request.abort(); // abort if there's something in play
      config.data = params || "";
      request = $.ajax(config);
      request.done(function() {
        // Activate each listener task
        for(var i=0; i<listeners.length; ++i) {
          listeners[i]();
        }
      })
    }
    
    /* Specify data processing task after response
     * @task (Function) Do something after service.response has been updated
     **/
    service.listener = function(task) {
      listeners.push(task);
    }
  }

  
  // Create service to fetch Company from name lookup on Companies House API
  this.getCompanyByName = new Service("/api/internal/companies-house-search/");
  
});


/* 
  General reusable component classes
  ==================================== */
GOVUK.components = (new function() {
  
  /* Performs a data lookup and displays multiple choice results
   * to populate the input value with user choice. 
   *
   * @$input (jQuery node) Target input element
   * @request (Function) Returns reference to the jqXHR requesting data
   * @content (Function) Returns content to populate the dropdown 
   * @options (Object) Allow some configurations
   **/
  this.SelectiveLookup = SelectiveLookup;
  function SelectiveLookup($input, service, options) {
    var instance = this;
    var popupId = GOVUK.utils.uniqueString();
    
    // Configure options.
    opts = $.extend({
      lookupOnCharacter: 4, // (Integer) At what character input to trigger the request for data
    }, options || {});
    
    // Some inner variable requirement.
    instance._private = {
      active: false, // State management to isolate the listener.
      service: service, // Service that retrieves and stores the data
      $list: $("<ul class=\"SelectiveLookupDisplay\" style=\"display:none;\" id=\"" + popupId + "\" role=\"listbox\"></ul>"),
      $input: $input
    }
    
    // Will not have arguments if being inherited for prototype
    if(arguments.length >= 2) {
      
      // Bind lookup event.
      $input.attr("autocomplete", "off"); // Because it interferes with results display. 
      $input.on("focus", function() { instance._private.active = true; });
      $input.on("blur", function() { instance._private.active = false; });
      $input.on("input.SelectiveLookup", function() {
        if(this.value.length >= opts.lookupOnCharacter) {
          instance.search();
        }
      });
      
      /* Bind events to allow keyboard navigation of component.
       * Using keydown event because works better with Tab capture.
       * Supports following keys:
       * 9 = Tab
       * 13 = Enter
       * 27 = Esc
       * 38 = Up
       * 40 = Down
       */
      $input.on("keydown.SelectiveLookup", function(e) {
        switch(e.which) {
          
          // Esc to close when on input
          case 27: 
            instance.close();
            break;
            
          // Tab or arrow from input to list
          case  9: 
          case 40: 
            if(!e.shiftKey) {
              e.preventDefault();
              instance._private.$list.find("li:first-child").focus();
            }
        }
      });
      
      instance._private.$list.on("keydown", "li", function(e) {
        var $current = $(e.target);
        switch(e.which) {
          
          // Arrow movement between list items
          case 38:
            e.preventDefault();
            $current.prev("li").focus();
            break;
          case 40:
            e.preventDefault();
            $current.next("li").focus();
            break;
            
          // Esc to close when on list item (re-focus on input)
          case 27:
            instance.close();
            $input.focus();
            break;
            
          // Enter key item selection  
          case 13:
            $current.click();
        }
      });
      
      // Tab or arrow movement from list to input
      instance._private.$list.on("keydown", "li:first-child", function(e) {
        if(e.shiftKey && e.which === 9 || e.which === 38) {
          e.preventDefault();
          $input.focus();
        }
      });
      
      // Bind service update listener
      instance._private.service.listener(function() {
        if(instance._private.active) {
          instance.setContent();
          instance.bindContentEvents();
          instance.open();
        }
      });
      
      // Add some accessibility support
      $input.attr("aria-autocomplete", "list");
      $input.attr("role", "combobox");
      $input.attr("aria-expanded", "false");
      $input.attr("aria-owns", popupId);
    
      // Add display element
      $(document.body).append(instance._private.$list);
    
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
    instance._private.$list.off("click.SelectiveLookupContent");
    instance._private.$list.on("click.SelectiveLookupContent", function(event) {
      var $eventTarget = $(event.target);
      if($eventTarget.attr("data-value")) {
        instance._private.$input.val($eventTarget.attr("data-value"));
      }
    });
  }
  SelectiveLookup.prototype.close = function() {
    this._private.$list.css({ display: "none" });
    this._private.$input.attr("aria-expanded", "false");
  }  
  SelectiveLookup.prototype.search = function() {
   this._private.service.update(this.param());
  }
  SelectiveLookup.prototype.param = function() {
    // Set param in separate function to allow easy override.
    return this.$input.attr("name") + "=" + this.$input.value;
  }
  /* Uses the data set on associated service to build HTML
   * result output. Since data keys are quite likely to vary
   * across services, you can pass through a mappingn object
   * to avoid the default/expected key names.
   * @datamapping (Object) Allow change of required key name
   **/
  SelectiveLookup.prototype.setContent = function(datamapping) {
    var data = this._private.service.response;
    var $list = this._private.$list;
    var map = datamapping || { text: "text", value: "value" };
    $list.empty();
    if(data && data.length) {
      for(var i=0; i<data.length; ++i) {
        // Note: 
        // Only need to set a tabindex attribute to allow focus. 
        // The value is not important here.
        $list.append("<li role=\"option\" tabindex=\"1000\" data-value=\"" + data[i][map.value] + "\">" + data[i][map.text] + "</li>");
      }
    }
    else {
      $list.append("<li role=\"option\">No results found</li>");
    }
  }
  SelectiveLookup.prototype.setSizeAndPosition = function() {
    var position = this._private.$input.offset();
    this._private.$list.css({
      left: parseInt(position.left) + "px",
      position: "absolute",
      top: (parseInt(position.top) + this._private.$input.outerHeight()) + "px",
      width: this._private.$input.outerWidth() + "px"
    });
  }
  SelectiveLookup.prototype.open = function() {
    this.setSizeAndPosition();
    this._private.$list.css({ display: "block" });
    this._private.$input.attr("aria-expanded", "true");
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
   * @$input (jQuery node) Target input element
   * @$field (jQuery node) Alternative element to populate with selection value
   **/
  this.CompaniesHouseNameLookup = CompaniesHouseNameLookup;
  function CompaniesHouseNameLookup($input, $field) {
    SelectiveLookup.call(this, 
      $input,
      GOVUK.data.getCompanyByName
    );

    // Some inner variable requirement.
    this._private.$field = $field || $input; // Allows a different form field to receive value.
  }
  CompaniesHouseNameLookup.prototype = new SelectiveLookup;
  CompaniesHouseNameLookup.prototype.bindContentEvents = function() {
    var instance = this;
    instance._private.$list.off("click.SelectiveLookupContent");
    instance._private.$list.on("click.SelectiveLookupContent", function(event) {
      var $eventTarget = $(event.target);
      if($eventTarget.attr("data-value")) {
        instance._private.$input.val($eventTarget.text());
        instance._private.$field.val($eventTarget.attr("data-value"));
      }
    });
  }
  CompaniesHouseNameLookup.prototype.param = function() {
    return "term=" + this._private.$input.val();
  }
  CompaniesHouseNameLookup.prototype.setContent = function() {
    SelectiveLookup.prototype.setContent.call(this, {
      text: "title",
      value: "company_number"
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
    $(".register-company-number-form").each(function() {
      var $input = $("input[name='company-number-company_number']", this);
      var $field = $("<input type=\"hidden\" name=\"company_number\" />");
      var $label = $(".label", this);
      
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
