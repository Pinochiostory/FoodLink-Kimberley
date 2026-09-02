/* =========================================================
   FOODLINK KIMBERLEY — shared UI behavior
   Pure progressive enhancement. No backend/data logic here.
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

  /* ---- Button loading state on form submit ----
     Works for regular (non-AJAX) POST forms: shows a spinner
     and disables the button while the browser processes the
     navigation, so the person always gets feedback. */
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function () {
      // If a confirm()-guarded submit was cancelled, this listener
      // simply never fires (submit event does not dispatch).
      var btn = form.querySelector('[type="submit"], .btn[type="submit"]');
      if (!btn) return;
      window.setTimeout(function () {
        btn.classList.add("btn-loading");
        btn.setAttribute("aria-disabled", "true");
        btn.disabled = true;
      }, 0);
    });
  });

  /* ---- Skeleton -> content reveal ----
     Sections marked with [data-loading] show a skeleton first,
     then swap to real (already-rendered) content shortly after
     paint, giving data-heavy pages a deliberate loading rhythm
     without needing a client-side data fetch. */
  var loaders = document.querySelectorAll("[data-loading]");
  loaders.forEach(function (el, i) {
    window.setTimeout(function () {
      el.removeAttribute("data-loading");
      el.setAttribute("data-reveal", "");
    }, 260 + i * 90);
  });

  /* ---- Mobile sidebar toggle ---- */
  var toggle = document.querySelector(".sidebar-toggle");
  var sidebar = document.querySelector(".sidebar");
  var scrim = document.querySelector(".sidebar-scrim");
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove("open");
    if (scrim) scrim.classList.remove("open");
  }
  if (toggle && sidebar) {
    toggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
      if (scrim) scrim.classList.toggle("open");
    });
  }
  if (scrim) scrim.addEventListener("click", closeSidebar);

  /* ---- Sliding login / register auth screens ----
     Both forms live in the same page (auth.html); clicking
     "Create an account" / "Log in" just slides the track and
     swaps the visible form instead of doing a full page reload,
     so the image panel animates smoothly between the two. The
     server still renders the correct mode on first load and on
     refresh (via the mode= the route passes in), so this is a
     progressive enhancement, not a requirement for the page to
     work. */
  var authTrack = document.getElementById("authTrack");
  if (authTrack) {
    document.querySelectorAll(".auth-switch").forEach(function (link) {
      link.addEventListener("click", function (e) {
        var target = link.getAttribute("data-target");
        if (!target) return;
        e.preventDefault();
        authTrack.setAttribute("data-mode", target);
        if (window.history && window.history.pushState) {
          window.history.pushState({ authMode: target }, "", link.href);
        }
        // Move focus to the newly-visible form's first field once
        // the slide finishes, for keyboard/screen-reader users.
        window.setTimeout(function () {
          var visibleScreen = authTrack.querySelector(
            ".auth-screen-" + target + " input"
          );
          if (visibleScreen) visibleScreen.focus();
        }, 340);
      });
    });

    window.addEventListener("popstate", function () {
      var mode = location.pathname.indexOf("register") !== -1
        ? "register"
        : "login";
      authTrack.setAttribute("data-mode", mode);
    });
  }

  /* ---- Auto-dismiss flash alerts ---- */
  document.querySelectorAll("[data-flash]").forEach(function (el) {
    window.setTimeout(function () {
      el.style.transition = "opacity " + 300 + "ms ease, transform 300ms ease";
      el.style.opacity = "0";
      el.style.transform = "translateY(-4px)";
      window.setTimeout(function () { el.remove(); }, 320);
    }, 5000);
  });
});
