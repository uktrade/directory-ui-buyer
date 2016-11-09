(function(){
  var menuToggleClass = 'js-header-nav-menu-toggle-button';
  var menuShowClass = 'js-header-nav-menu';
  var menuHideClass = menuShowClass + ' js-header-nav-menu-hide';
  var menuElement = document.querySelectorAll('.' + menuShowClass)[0];
  var menuToggleButton = document.querySelectorAll('.' + menuToggleClass)[0];
  var state = {
    showmenu: menuElement.className === menuShowClass,
  };

  function addEventListener(element, listener) {
    // for IE8 compatibility
    if (element.addEventListener) {
      element.addEventListener('click', listener, false);
    } else {
      element.attachEvent('onclick', listener);
    }
  }

  function showMenu() {
    menuElement.className = menuShowClass;
    state.showmenu = true;
  }

  function hideMenu() {
    menuElement.className = menuHideClass;
    state.showmenu = false;
  }

  function handleMenuToggle() {
    if (state.showmenu === true) {
      hideMenu();
    } else {
      showMenu();
    }
  }

  addEventListener(menuToggleButton, handleMenuToggle);

})();
