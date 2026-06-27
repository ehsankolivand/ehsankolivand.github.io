/* Ehsan.log — progressive enhancement for the static blog.
 * Ported from the original design's interaction logic (dc-script) to dependency-free
 * vanilla JS that operates on the already-rendered static DOM. It renders NO content:
 * every post, link, and piece of text is present in the HTML without this file
 * (Constitution Principle I). Honors prefers-reduced-motion and touch. */
(function () {
  "use strict";
  function init() {
    var root = document.getElementById("blog-root");
    if (!root) return;
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var isTouch = window.matchMedia("(hover: none), (pointer: coarse)").matches;
    var EASE = "cubic-bezier(0.2,0,0,1)";
    function mkEl(tag, css, html) { var e = document.createElement(tag); if (css) e.style.cssText = css; if (html != null) e.innerHTML = html; return e; }

    /* ---------- safety net: never leave a compose-in hero invisible ---------- */
    var revealHeroNow = function () {
      Array.prototype.forEach.call(root.querySelectorAll("section *"), function (el) {
        if (getComputedStyle(el).animationName.indexOf("composeIn") > -1) {
          el.style.animation = "none"; el.style.opacity = "1"; el.style.transform = "none"; el.style.filter = "none";
        }
      });
    };
    if (reduce) revealHeroNow(); else setTimeout(revealHeroNow, 2200);
    document.addEventListener("visibilitychange", function () { if (document.visibilityState === "visible") setTimeout(revealHeroNow, 1400); });

    /* ---------- ink ripple (delegated) ---------- */
    root.addEventListener("pointerdown", function (e) {
      var t = e.target.closest("[data-ripple]"); if (!t) return;
      var r = t.getBoundingClientRect(); var d = Math.max(r.width, r.height);
      var ink = document.createElement("span");
      ink.style.cssText = "position:absolute;border-radius:50%;pointer-events:none;background:rgba(255,255,255,0.30);width:" + d + "px;height:" + d + "px;left:" + (e.clientX - r.left - d / 2) + "px;top:" + (e.clientY - r.top - d / 2) + "px;transform:scale(0);opacity:.7;animation:rippleExp .62s ease-out forwards;z-index:0;";
      if (getComputedStyle(t).position === "static") t.style.position = "relative";
      t.appendChild(ink); setTimeout(function () { ink.remove(); }, 640);
    });

    /* ---------- magnetic custom cursor (desktop) ---------- */
    if (!isTouch && !reduce) {
      var cur = root.querySelector("[data-cursor]"), dot = root.querySelector("[data-cursor-dot]");
      if (cur && dot) {
        cur.style.display = "block"; dot.style.display = "block";
        var mx = window.innerWidth / 2, my = window.innerHeight / 2, cx = mx, cy = my;
        window.addEventListener("pointermove", function (e) { mx = e.clientX; my = e.clientY; });
        (function loop() {
          cx += (mx - cx) * 0.18; cy += (my - cy) * 0.18;
          cur.style.transform = "translate(" + (cx - 17) + "px," + (cy - 17) + "px)";
          dot.style.transform = "translate(" + (mx - 2.5) + "px," + (my - 2.5) + "px)";
          requestAnimationFrame(loop);
        })();
        var grow = function () { cur.style.width = "58px"; cur.style.height = "58px"; cur.style.background = "rgba(52,230,160,0.10)"; cur.style.borderColor = "rgba(231,210,166,0.8)"; };
        var shrink = function () { cur.style.width = "34px"; cur.style.height = "34px"; cur.style.background = "transparent"; cur.style.borderColor = "rgba(52,230,160,0.7)"; };
        root.addEventListener("pointerover", function (e) { if (e.target.closest("a,button,[data-magnetic],[data-card]")) grow(); });
        root.addEventListener("pointerout", function (e) { if (e.target.closest("a,button,[data-magnetic],[data-card]")) shrink(); });
      }
    }

    /* ---------- scroll reveals (rect-based) ---------- */
    var reveal = function (el) { el.style.opacity = "1"; el.style.transform = "none"; el.style.filter = "none"; el.setAttribute("data-shown", ""); };
    if (reduce) {
      Array.prototype.forEach.call(root.querySelectorAll("[data-reveal]"), reveal);
    } else {
      var revealCheck = function () {
        var vh = window.innerHeight || document.documentElement.clientHeight;
        Array.prototype.forEach.call(root.querySelectorAll("[data-reveal]:not([data-shown])"), function (el) {
          var b = el.getBoundingClientRect();
          if (b.top < vh * 0.94 && b.bottom > 0) reveal(el);
        });
      };
      var rafR = 0;
      window.addEventListener("scroll", function () { if (!rafR) rafR = requestAnimationFrame(function () { rafR = 0; revealCheck(); }); }, { passive: true });
      window.addEventListener("resize", revealCheck);
      revealCheck(); requestAnimationFrame(revealCheck); setTimeout(revealCheck, 160);
    }

    /* ---------- magnetic pull + card hover ---------- */
    if (!isTouch && !reduce) {
      Array.prototype.forEach.call(root.querySelectorAll("[data-magnetic]"), function (el) {
        el.addEventListener("pointermove", function (e) { var r = el.getBoundingClientRect(); var x = e.clientX - r.left - r.width / 2, y = e.clientY - r.top - r.height / 2; el.style.transform = "translate(" + x * 0.25 + "px," + y * 0.3 + "px)"; });
        el.addEventListener("pointerleave", function () { el.style.transition = "transform .5s " + EASE; el.style.transform = "translate(0,0)"; setTimeout(function () { el.style.transition = ""; }, 500); });
      });
    }
    Array.prototype.forEach.call(root.querySelectorAll("[data-card]"), function (card) {
      var glow = card.querySelector("[data-cardglow]"), arrow = card.querySelector("[data-cardarrow]");
      card.addEventListener("pointerenter", function () { card.style.transform = "translateY(-5px)"; card.style.boxShadow = "0 26px 64px rgba(0,0,0,0.5)"; card.style.borderColor = "rgba(52,230,160,0.4)"; if (glow) glow.style.opacity = "1"; if (arrow) arrow.style.transform = "translate(3px,-1px)"; if (card.style.background.indexOf("255,255,255,0.025") > -1) card.style.background = "rgba(52,230,160,0.06)"; });
      card.addEventListener("pointerleave", function () { card.style.transform = "none"; card.style.boxShadow = ""; card.style.borderColor = ""; if (glow) glow.style.opacity = "0"; if (arrow) arrow.style.transform = "none"; if (card.style.background.indexOf("52,230,160,0.06") > -1) card.style.background = "rgba(255,255,255,0.025)"; });
    });

    /* ---------- category nav: active state + filtering (index = progressive enhancement) ---------- */
    var isIndex = !!root.querySelector('[data-screen-label="Blog Index"]');
    // IMPORTANT: only the header nav carries filter links. Post cards also have
    // data-cat (for filtering) but must NOT be treated as nav links, or their click
    // would be intercepted and their styling overwritten.
    var navLinks = Array.prototype.slice.call(root.querySelectorAll("[data-topcats] [data-cat]"));
    var cards = Array.prototype.slice.call(root.querySelectorAll('main [data-card][data-cat]'));
    // Remember each card's layout display (grid for featured, flex for grid cards) so
    // filtering can restore it. Blanking style.display would erase the inline layout.
    cards.forEach(function (card) { card.__display = card.style.display; });
    var currentFilter = "All";
    function syncCats(f) {
      navLinks.forEach(function (b) { var on = b.getAttribute("data-cat") === f; b.style.color = on ? "#34E6A0" : "#9FB0AA"; b.style.background = on ? "rgba(52,230,160,0.08)" : "transparent"; });
    }
    function applyFilter(f) {
      currentFilter = f;
      cards.forEach(function (card) {
        var show = (f === "All" || card.getAttribute("data-cat") === f);
        card.style.display = show ? card.__display : "none";
      });
      syncCats(f);
    }
    navLinks.forEach(function (b) {
      b.addEventListener("pointerenter", function () { if (b.getAttribute("data-cat") !== currentFilter) { b.style.color = "#EDF2EF"; b.style.background = "rgba(255,255,255,0.05)"; } });
      b.addEventListener("pointerleave", function () { syncCats(currentFilter); });
      if (isIndex) {
        b.addEventListener("click", function (e) {
          e.preventDefault();
          var f = b.getAttribute("data-cat");
          applyFilter(f);
          try { history.replaceState(null, "", f === "All" ? location.pathname : (location.pathname + "#cat=" + encodeURIComponent(f))); } catch (_) {}
        });
      }
    });
    if (isIndex) {
      var hm = /[#&]cat=([^&]+)/.exec(location.hash || "");
      applyFilter(hm ? decodeURIComponent(hm[1]) : "All");
    }

    /* ---------- "Home" link (back to portfolio) hover ---------- */
    var homeLink = root.querySelector("[data-home]");
    if (homeLink) {
      homeLink.addEventListener("pointerenter", function () {
        homeLink.style.color = "#EDF2EF"; homeLink.style.background = "rgba(255,255,255,0.07)";
        homeLink.style.borderColor = "rgba(52,230,160,0.35)";
      });
      homeLink.addEventListener("pointerleave", function () {
        homeLink.style.color = "#9FB0AA"; homeLink.style.background = "rgba(255,255,255,0.04)";
        homeLink.style.borderColor = "rgba(255,255,255,0.10)";
      });
    }

    /* ---------- reading-progress bar ---------- */
    (function readingBar() {
      var se = document.scrollingElement || document.documentElement;
      var bar = mkEl("div", "position:fixed; top:0; left:0; right:0; height:3px; z-index:121; background:rgba(255,255,255,0.06); pointer-events:none;");
      var fill = mkEl("div", "height:100%; width:0%; background:linear-gradient(90deg,#18A06A,#34E6A0,#7DF0C2); box-shadow:0 0 10px rgba(52,230,160,0.7);"); bar.appendChild(fill);
      var pill = mkEl("div", "position:fixed; top:10px; left:50%; transform:translateX(-50%) translateY(-160%); z-index:121; display:flex; align-items:center; gap:7px; padding:6px 13px; border-radius:999px; background:rgba(8,12,11,0.92); border:1px solid rgba(52,230,160,0.22); -webkit-backdrop-filter:blur(8px); backdrop-filter:blur(8px); font-family:'JetBrains Mono',monospace; font-size:11.5px; color:#9FB0AA; opacity:0; transition:opacity .3s, transform .45s cubic-bezier(.2,0,0,1), color .3s, border-color .3s; pointer-events:none; white-space:nowrap;", "<span data-rb-ic>▾</span><span data-rb-txt>0%</span>");
      root.appendChild(bar); root.appendChild(pill);
      var ic = pill.querySelector("[data-rb-ic]"), txt = pill.querySelector("[data-rb-txt]");
      var raf = 0, done = false;
      var update = function () {
        raf = 0; var docH = se.scrollHeight - se.clientHeight; var p = docH > 0 ? Math.min(1, Math.max(0, se.scrollTop / docH)) : 0; var pct = Math.round(p * 100);
        fill.style.width = (p * 100) + "%";
        var show = se.scrollTop > 40; pill.style.opacity = show ? "1" : "0"; pill.style.transform = "translateX(-50%) " + (show ? "translateY(0)" : "translateY(-160%)");
        if (pct >= 100) { if (!done) { done = true; ic.textContent = "✓"; txt.textContent = "End of note"; pill.style.color = "#34E6A0"; pill.style.borderColor = "rgba(52,230,160,0.5)"; } }
        else { if (done) { done = false; ic.textContent = "▾"; pill.style.color = "#9FB0AA"; pill.style.borderColor = "rgba(52,230,160,0.22)"; } txt.textContent = pct + "%"; }
      };
      window.addEventListener("scroll", function () { if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
      window.addEventListener("resize", function () { if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
      update();
    })();

    /* ---------- scroll-reactor companion ---------- */
    var reactorEl = root.querySelector("[data-reactor]");
    if (reactorEl && !reduce) {
      var fillR = reactorEl.querySelector("[data-reactor-fill]");
      var rider = reactorEl.querySelector("[data-reactor-bot]");
      var head = reactorEl.querySelector("[data-reactor-head]");
      var eL = reactorEl.querySelector('[data-reactor-eye="l"]'), eR = reactorEl.querySelector('[data-reactor-eye="r"]');
      var mouth = reactorEl.querySelector("[data-reactor-mouth]");
      var aL = reactorEl.querySelector('[data-reactor-arm="l"]'), aR = reactorEl.querySelector('[data-reactor-arm="r"]');
      var shout = reactorEl.querySelector("[data-reactor-shout]");
      var spd = reactorEl.querySelector("[data-reactor-speed]");
      var sweat = reactorEl.querySelector("[data-reactor-sweat]");
      var SHOUTS = ["eep!", "wheee!", "wobble!", "so fast!", "aaa~", "hold on!", "catch me!"];
      var lastY = window.scrollY, rawv = 0, sv = 0, blink = 0, rx = 0;
      window.addEventListener("scroll", function () { var y = window.scrollY; rawv = y - lastY; lastY = y; }, { passive: true });
      (function loop() {
        sv += (rawv - sv) * 0.22; rawv *= 0.55;
        var docH = document.documentElement.scrollHeight - window.innerHeight;
        var prog = docH > 0 ? Math.min(1, Math.max(0, window.scrollY / docH)) : 0;
        var vh = window.innerHeight, top = 0.15, span = 0.70;
        rider.style.top = ((top + prog * span) * vh) + "px";
        fillR.style.height = (prog * span * vh) + "px";
        var inst = Math.min(1, Math.abs(sv) / 44);
        rx = Math.max(inst, rx * 0.988);
        var s = rx, dir = sv >= 0 ? 1 : -1;
        var jit = s > 0.42 ? (Math.random() - 0.5) * s * 5 : 0;
        var wob = Math.sin(performance.now() / 85) * s;
        head.style.transform = "translateX(" + jit.toFixed(2) + "px) rotate(" + (dir * s * 15 + wob * 6).toFixed(2) + "deg) scale(" + (1 + Math.abs(wob) * 0.12).toFixed(3) + ")";
        sweat.style.opacity = s > 0.34 ? String(Math.min(1, (s - 0.34) * 2.6)) : "0";
        mouth.style.opacity = s > 0.16 ? "1" : "0";
        mouth.style.transform = "translateX(-50%) scaleY(" + (0.2 + s * 1.1) + ") scaleX(" + (0.7 + s * 0.4) + ")";
        aL.style.transform = "rotate(" + (-22 - s * 78) + "deg)";
        aR.style.transform = "rotate(" + (22 + s * 78) + "deg)";
        spd.style.opacity = String(Math.max(0, s - 0.2) * 1.7);
        if (s > 0.4) { shout.style.opacity = "1"; shout.style.transform = "translateX(-50%) translateY(" + (-2 - s * 5) + "px) scale(" + (0.9 + s * 0.3) + ")"; if (!shout.dataset.lock) { shout.textContent = SHOUTS[Math.floor(Math.random() * SHOUTS.length)]; shout.dataset.lock = "1"; } }
        else { shout.style.opacity = "0"; shout.dataset.lock = ""; }
        if (s > 0.08) { var es = 1 + s * 1.5, ew = Math.sin(performance.now() / 70) * s * 0.12; eL.style.transform = "scale(" + (es + ew).toFixed(3) + ")"; eR.style.transform = "scale(" + (es - ew).toFixed(3) + ")"; }
        else { blink++; var b = blink % 210; var sq = (b > 203) ? " scaleY(0.12)" : ""; eL.style.transform = "scale(1)" + sq; eR.style.transform = "scale(1)" + sq; }
        requestAnimationFrame(loop);
      })();
    }

    /* ---------- companion 'Bit': hover handshake (index hero) ---------- */
    (function bit() {
      if (reduce || isTouch) return;
      var comp = root.querySelector("[data-companion]"); if (!comp) return;
      var body = comp.querySelector("div"); if (!body) return;
      comp.style.pointerEvents = "auto"; body.style.cursor = "pointer";
      var bub = mkEl("div", "position:absolute; bottom:54px; right:0; width:164px; transform:translateY(8px) scale(0); transform-origin:bottom right; text-align:center; line-height:1.3; padding:7px 11px; border-radius:13px 13px 4px 13px; background:rgba(16,23,21,0.97); border:1px solid rgba(52,230,160,0.35); color:#34E6A0; font-family:'JetBrains Mono',monospace; font-weight:600; font-size:11px; box-shadow:0 12px 30px rgba(0,0,0,0.5); opacity:0; transition:opacity .25s, transform .4s cubic-bezier(.34,1.56,.64,1); pointer-events:none; z-index:9;");
      comp.appendChild(bub);
      var show = function (t) { bub.textContent = t; bub.style.opacity = "1"; bub.style.transform = "translateY(0) scale(1)"; };
      var hide = function () { bub.style.opacity = "0"; bub.style.transform = "translateY(8px) scale(0)"; };
      comp.addEventListener("pointerenter", function () { show("👋 I'm Bit — hello!"); });
      comp.addEventListener("pointerleave", hide);
    })();

    /* ---------- easter egg: tap the logo x5 -> confetti ---------- */
    (function party() {
      var logo = root.querySelector("[data-logo]"); if (!logo) return;
      var clicks = 0, ct = null;
      var toast = function (msg) { var t = mkEl("div", "position:fixed; left:50%; bottom:40px; transform:translateX(-50%) translateY(16px) scale(.96); z-index:320; padding:12px 18px; border-radius:14px; background:linear-gradient(135deg,#34E6A0,#18A06A); color:#04130D; font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:14px; box-shadow:0 16px 40px rgba(52,230,160,0.4); opacity:0; transition:opacity .3s, transform .45s cubic-bezier(.34,1.56,.64,1); pointer-events:none;", msg); document.body.appendChild(t); requestAnimationFrame(function () { t.style.opacity = "1"; t.style.transform = "translateX(-50%) translateY(0) scale(1)"; }); setTimeout(function () { t.style.opacity = "0"; setTimeout(function () { t.remove(); }, 360); }, 2300); };
      function go() {
        toast("🎉 Party mode unlocked!");
        var amb = root.querySelector("[data-ambient]"); if (amb && !reduce) { amb.style.animation = "partyHue 6s linear"; setTimeout(function () { amb.style.animation = ""; }, 6200); }
        if (reduce) return;
        var palette = ["#34E6A0", "#7DF0C2", "#E7D2A6", "#46a8e0", "#ff9ec4", "#b388ff", "#ffd166"];
        var layer = mkEl("div", "position:fixed; inset:0; z-index:130; pointer-events:none; overflow:hidden;"); document.body.appendChild(layer);
        for (var i = 0; i < 48; i++) { var c = palette[i % palette.length]; var sz = 7 + Math.random() * 8; var piece = mkEl("span", "position:absolute; top:-20px; left:" + (Math.random() * 100) + "%; width:" + sz + "px; height:" + (sz * 0.6) + "px; background:" + c + "; border-radius:2px; opacity:0; animation:confettiFall " + (2.4 + Math.random() * 2.2) + "s cubic-bezier(.3,.1,.4,1) " + (Math.random() * 1.2) + "s forwards;"); piece.style.setProperty("--cr", (Math.random() * 720 - 360) + "deg"); layer.appendChild(piece); }
        setTimeout(function () { layer.remove(); }, 5400);
      }
      logo.addEventListener("click", function () { clicks++; clearTimeout(ct); ct = setTimeout(function () { clicks = 0; }, 1400); if (clicks >= 5) { clicks = 0; go(); } });
    })();

    /* responsive: hide scroll-reactor on mobile / reduced motion */
    var applyResp = function () { var m = window.innerWidth <= 760; if (reactorEl) reactorEl.style.display = (m || reduce) ? "none" : "block"; };
    applyResp(); window.addEventListener("resize", applyResp);
  }

  if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
