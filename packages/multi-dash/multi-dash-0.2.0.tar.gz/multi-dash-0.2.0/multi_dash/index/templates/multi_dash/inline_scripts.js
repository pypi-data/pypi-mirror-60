window.onload = function() {
  //Attach events to the Menu
  var menuItems = document.querySelectorAll("a[data-page-slug]");
  Array.prototype.map.call(menuItems, function(element) {
    element.onclick = function(e) {
      e.preventDefault();
      e.stopPropagation();

      var current_slug = e.currentTarget.getAttribute("data-page-slug");
      var dashboard = dashboards.find(function(page) {
        return page.slug == current_slug;
      });
      showDashboard(dashboard);
    };
  });

  function updateTitleAndHistory(dashboard) {
    // Idempotently update the title and history
    document.title = "Dashboard | " + dashboard.title;
    document.getElementById("page-title").innerText = dashboard.title;
    if (!history.state || dashboard.slug != history.state.slug) {
      console.log("push", dashboard);
      history.pushState(dashboard, dashboard.title, dashboard.url);
    }
  }

  // Triggered on user triggered actions, like using the back button.
  window.onpopstate = function(event) {
    const dashboard = event.state;
    if (dashboard && dashboard.dash_url) {
      showDashboard(dashboard);
    } else {
      window.location = document.location;
    }
  };

  function showDashboard(dashboard) {
    // Find the iframe, and render the dashboard in there if we can,
    // if not then just use regular page transition.
    const viewport = document.getElementById("content-frame");
    if (viewport) {
      viewport.src = dashboard.page_url;
      updateTitleAndHistory(dashboard);
    } else {
      window.location = dashboard.url;
    }
  }

  // We reset the title and the url when the IFrame changes
  var contentFrame = document.getElementById("content-frame");
  contentFrame.onload = function() {
    var path = contentFrame.contentDocument.location.pathname.replace(
      /\/$/,
      ""
    );

    var dashboard = window.dashboards.find(function(item) {
      return item.page_url == path;
    });

    if (dashboard) {
      updateTitleAndHistory(dashboard);
    }
  };
};
