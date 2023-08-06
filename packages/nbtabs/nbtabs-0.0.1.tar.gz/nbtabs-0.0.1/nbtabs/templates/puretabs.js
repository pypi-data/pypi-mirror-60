(function(exports) {

  var $ = document.querySelectorAll.bind(document);

  exports.pureTabs = {

    toggle: function(e) {
      var activeClassName = this.activeClassName,
          oldSection = $('[data-puretabs="' + this.className + '"]')[0],
          newSection = $(e.currentTarget.hash)[0];

      removeClass($(this.className + activeClassName)[0], activeClassName.substr(1));
      addClass(e.currentTarget, activeClassName.substr(1));

      oldSection.style.display = 'none';
      oldSection.removeAttribute('data-puretabs');

      newSection.style.display = 'block';
      newSection.setAttribute('data-puretabs', this.className);
    },

    init: function(className, activeClassName) {
      var self = {};
      self.toggle = this.toggle;

      self.className = '.' + className || '.puretabs';
      self.activeClassName = '.' + activeClassName || '.puretabs--active';

      var links = [].slice.call($(self.className));

      links.forEach(function(link) {

        if (!containsClass(link, self.activeClassName.substr(1))) {
          $(link.hash)[0].style.display = 'none';
        } else {
          $(link.hash)[0].setAttribute('data-puretabs', self.className);
        }

        link.addEventListener('click', function(e) {
          e.preventDefault();
          self.toggle.call(self, e)
        });

      });
    }

  };


  //  Helpers
  function addClass(e, c) {
    var re = new RegExp("(^|\\s)" + c + "(\\s|$)", "g");
    if (re.test(e.className)) return;
    e.className = (e.className + " " + c).replace(/\s+/g, " ").replace(/(^ | $)/g, "")
  }

  function removeClass(e, c) {
    var re = new RegExp("(^|\\s)" + c + "(\\s|$)", "g");
    e.className = e.className.replace(re, "$1").replace(/\s+/g, " ").replace(/(^ | $)/g, "");
  }

  function containsClass(e, c) {
    var re = new RegExp("(^|\\s)" + c + "(\\s|$)", "g");
    return re.test(e.className) ? true : false;
  }

})(window);
