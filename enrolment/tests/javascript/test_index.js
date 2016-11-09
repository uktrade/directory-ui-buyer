var jsdom = require('jsdom').jsdom;
var expect = require('chai').expect;

var html = '\
<!doctype html> \
<html> \
  <body> \
    <div> \
      <span class="js-header-nav-menu-toggle-button">toggle</span> \
      <span class="js-header-nav-menu js-header-nav-menu-hide">menu contents</span> \
    </div> \
  </body> \
</html> \
';
var menuShowClass = 'js-header-nav-menu';
var menuHideClass = menuShowClass + ' js-header-nav-menu-hide';

function requireUncached(module){
    delete require.cache[require.resolve(module)]
    return require(module)
}

describe('menu toggle', function() {

  beforeEach(function() {
    global.document = jsdom(html);
    requireUncached('../../static/javascripts/index.js');

    menuElement = document.querySelectorAll('.js-header-nav-menu')[0];
    menuToggleButton = document.querySelectorAll('.js-header-nav-menu-toggle-button')[0];
  });

  it('should show the menu if currently hidden', function() {

    // given the menu element is hidden on page load
    expect(menuElement.className).to.equal(menuHideClass);
    // when I click the menu toggle button
    menuToggleButton.click();
    // then the menu element becomes visible
    expect(menuElement.className).to.equal(menuShowClass);
  });

  it('should hide the menu if currently visible', function() {
    // given the menu element is visible on page load
    menuToggleButton.click();
    expect(menuElement.className).to.equal(menuShowClass);
    // when I click the menu toggle button
    menuToggleButton.click();
    // then the menu element becomes hidden
    expect(menuElement.className).to.equal(menuHideClass);
  });
});