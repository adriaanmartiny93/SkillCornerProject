/* SkillCorner design-system visuals for ECharts 5. One file, shared by the Streamlit
   component (components/sc_chart/index.html) and the standalone export templates.
   Entry point: SC.render(rootEl, kind, payload, emit)
   payload = { data, labels, colours, title, options }   (see src/viz/payloads.py)
   emit(value) is called on click when the visual is interactive, else null. */
(function () {
  var T = { i950: '#101210', i900: '#161917', i850: '#1c1f1d', i800: '#232624', i750: '#2a2e2b', i700: '#323733', i600: '#424843', i500: '#5d645e', i400: '#858c86', i300: '#aab0ab', i200: '#cfd3d0', i50: '#f5f6f5', green: '#1fd655', glow: '#4cf07a' };
  var SERIES = ['#1fd655', '#33c3e8', '#f2b33d', '#f2665c', '#a191f2', '#aab0ab'];
  var HL = ['#ffffff', '#33c3e8', '#f2b33d'];
  var BODY = "'IBM Plex Sans',system-ui,sans-serif", MONO = "'IBM Plex Mono',ui-monospace,monospace", DISP = "'Saira',system-ui,sans-serif";

  function rgba(h, a) { h = h.replace('#', ''); return 'rgba(' + parseInt(h.slice(0, 2), 16) + ',' + parseInt(h.slice(2, 4), 16) + ',' + parseInt(h.slice(4, 6), 16) + ',' + a + ')'; }
  function pct(p) { return p >= 80 ? '#1fd655' : p >= 60 ? '#8fdc4a' : p >= 40 ? '#f2c53d' : p >= 20 ? '#f2913f' : '#f2665c'; }
  function fmt(v) { if (v == null || isNaN(v)) return ''; return Math.abs(v) >= 100 ? Math.round(v).toLocaleString('en-GB') : String(+(+v).toFixed(2)); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function opt(p) { return p.options || {}; }
  function cols(p) { return (p.colours && p.colours.length) ? p.colours : SERIES; }

  var CSS = [
    '.sc-card{background:' + T.i850 + ';border:1px solid ' + T.i750 + ';border-radius:6px;padding:20px;box-shadow:0 1px 0 rgba(255,255,255,.03) inset;color:' + T.i50 + ';font-family:' + BODY + ';box-sizing:border-box}',
    '.sc-eyebrow{font-family:' + DISP + ';font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:' + T.green + ';margin-bottom:4px}',
    '.sc-title{font-family:' + DISP + ';font-size:18px;font-weight:600;line-height:1.25;margin:0 0 14px}',
    '.sc-caption{font-size:12px;color:' + T.i400 + ';margin-top:10px}',
    '.sc-dist-row{margin-bottom:16px}',
    '.sc-dist-label{text-align:center;font-size:13px;color:' + T.i300 + ';margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
    '.sc-dist-label .v{font-family:' + MONO + '}.sc-dist-label .s{color:' + T.i500 + ';margin:0 6px}',
    '.sc-dist-track{position:relative;height:24px}',
    '.sc-dist-track:before{content:"";position:absolute;left:0;right:0;top:50%;border-top:1px solid ' + T.i700 + '}',
    '.sc-dot{position:absolute;top:50%;width:13px;height:13px;margin:-6.5px 0 0 -6.5px;border-radius:50%;background:' + rgba(T.green, .28) + ';transition:background 120ms}',
    '.sc-dot:hover{background:' + T.green + ';z-index:3}',
    '.sc-hex{position:absolute;top:50%;width:24px;height:24px;margin:-12px 0 0 -12px;clip-path:polygon(25% 5%,75% 5%,100% 50%,75% 95%,25% 95%,0 50%)}',
    '.sc-hex-glow{position:absolute;top:50%;width:24px;height:24px;margin:-12px 0 0 -12px;border-radius:50%;filter:blur(7px);opacity:.55}',
    '.sc-dist-axis{display:grid;grid-template-columns:1fr auto 1fr;font-size:12px;color:' + T.i400 + ';padding:4px 0 12px;border-bottom:1px solid ' + T.i750 + '}',
    '.sc-legend{display:flex;justify-content:center;gap:28px;flex-wrap:wrap;font-size:13px;color:' + T.i300 + ';padding-top:12px}',
    '.sc-legend span{display:inline-flex;align-items:center;gap:8px}',
    '.sc-tip{position:fixed;pointer-events:none;background:' + T.i800 + ';border:1px solid ' + T.i600 + ';border-radius:4px;padding:6px 9px;font:12px ' + MONO + ';color:' + T.i50 + ';box-shadow:0 12px 32px rgba(0,0,0,.45);z-index:10;display:none;white-space:nowrap}'
  ].join('\n');
  function injectCss() { if (document.getElementById('sc-css')) return; var s = document.createElement('style'); s.id = 'sc-css'; s.textContent = CSS; document.head.appendChild(s); }

  var tooltip = { backgroundColor: T.i800, borderColor: T.i600, borderWidth: 1, padding: [6, 9], textStyle: { color: T.i50, fontFamily: MONO, fontSize: 12 }, extraCssText: 'border-radius:4px;box-shadow:0 12px 32px rgba(0,0,0,.45)' };
  var legend = { bottom: 0, icon: 'roundRect', itemWidth: 10, itemHeight: 10, itemGap: 20, textStyle: { color: T.i300, fontFamily: BODY, fontSize: 12 } };
  function valueAxis(name) { return { type: 'value', name: name || '', nameTextStyle: { color: T.i400, fontFamily: MONO, fontSize: 11 }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: T.i750 } }, axisLabel: { color: T.i400, fontFamily: MONO, fontSize: 11, formatter: fmt } }; }

  function mount(el, h) {
    el.style.height = (h || 420) + 'px'; el.style.width = '100%';
    var c = echarts.init(el, null, { renderer: 'svg' });
    window.addEventListener('resize', function () { c.resize(); });
    return c;
  }

  /* ------------------------------------------------------------ radar
     data: [{name, values[0-100]}], labels: axes, options: {show_values, dashed:[names], height} */
  function radar(el, p, emit) {
    var o = opt(p), C = cols(p), S = p.data || [], dashed = o.dashed || [];
    var first = {}; (p.labels || []).forEach(function (a, i) { first[a] = S[0] ? S[0].values[i] : null; });
    // Long axis names are wrapped on word boundaries, otherwise they run past the edge of the canvas.
    function wrap(n) {
      var lines = [''];
      n.split(' ').forEach(function (w) {
        var k = lines.length - 1;
        if (lines[k] && (lines[k] + ' ' + w).length > 18) lines.push(w); else lines[k] = lines[k] ? lines[k] + ' ' + w : w;
      });
      return lines.join('\n');
    }
    var c = mount(el, o.height || 420);
    c.setOption({
      tooltip: Object.assign({ trigger: 'item' }, tooltip),
      legend: S.length > 1 ? legend : { show: false },
      radar: {
        indicator: (p.labels || []).map(function (a) { return { name: a, max: 100, min: 0 }; }),
        center: ['50%', S.length > 1 ? '47%' : '52%'], radius: '58%', splitNumber: 4, shape: 'polygon',
        axisName: {
          color: T.i300, fontFamily: DISP, fontSize: 11, fontWeight: 600,
          formatter: function (n) { var t = wrap(n.toUpperCase()); return o.show_values && first[n] != null ? t + '\n{v|' + Math.round(first[n]) + '}' : t; },
          rich: { v: { fontFamily: MONO, fontSize: 12, color: C[0], padding: [4, 0, 0, 0] } }
        },
        axisLine: { lineStyle: { color: T.i700 } },
        splitLine: { lineStyle: { color: [T.i700, T.i500, T.i700, T.i600] } },
        splitArea: { areaStyle: { color: [T.i850] } }
      },
      series: [{
        type: 'radar', symbol: 'circle', symbolSize: 6,
        data: S.map(function (s, i) {
          var col = s.colour || C[i % C.length];
          return {
            name: s.name, value: s.values,
            lineStyle: { color: col, width: i ? 1.5 : 2.2, type: dashed.indexOf(s.name) >= 0 ? 'dashed' : 'solid', shadowBlur: i ? 0 : 8, shadowColor: rgba(T.glow, .6) },
            itemStyle: { color: col, borderColor: T.i950, borderWidth: 1 },
            areaStyle: { color: rgba(col, i ? .08 : .2) }
          };
        })
      }]
    });
    if (emit) c.on('click', function (e) { emit({ kind: 'radar', name: e.name }); });
    return c;
  }

  /* ------------------------------------------------------------ bar
     data: [{name, values}], labels: categories,
     options: {unit, highlight, reference, reference_label, stacked, horizontal, height} */
  function bar(el, p, emit) {
    var o = opt(p), C = cols(p), S = p.data || [], H = !!o.horizontal;
    var cat = { type: 'category', data: p.labels, inverse: H, axisLine: { lineStyle: { color: T.i600 } }, axisTick: { show: false }, axisLabel: { color: T.i300, fontFamily: BODY, fontSize: 12 } };
    var c = mount(el, o.height || 320);
    c.setOption({
      tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow', shadowStyle: { color: rgba('#ffffff', .03) } }, valueFormatter: function (v) { return fmt(v) + (o.unit ? ' ' + o.unit : ''); } }, tooltip),
      legend: S.length > 1 ? legend : { show: false },
      grid: { left: 8, right: 16, top: 28, bottom: S.length > 1 ? 34 : 6, containLabel: true },
      xAxis: H ? valueAxis(o.unit) : cat, yAxis: H ? cat : valueAxis(o.unit),
      series: S.map(function (s, i) {
        var col = s.colour || C[i % C.length];
        var ser = {
          type: 'bar', name: s.name, stack: o.stacked ? 'total' : undefined, barMaxWidth: 44, barGap: '8%', barCategoryGap: '30%',
          data: s.values.map(function (v, j) {
            var on = o.highlight == null || p.labels[j] === o.highlight;
            return { value: v, itemStyle: { color: on ? col : rgba(col, .35), borderRadius: o.stacked ? 0 : (H ? [0, 2, 2, 0] : [2, 2, 0, 0]), shadowBlur: (o.highlight != null && on) ? 8 : 0, shadowColor: rgba(T.glow, .5) } };
          })
        };
        if (i === 0 && o.reference != null) ser.markLine = {
          symbol: 'none', silent: true, lineStyle: { color: T.i200, type: 'dashed', width: 1 },
          label: { formatter: (o.reference_label || 'Avg').toUpperCase() + ' ' + fmt(o.reference), color: T.i200, fontFamily: DISP, fontSize: 10, fontWeight: 600, position: 'insideEndTop' },
          data: [H ? { xAxis: o.reference } : { yAxis: o.reference }]
        };
        return ser;
      })
    });
    if (emit) c.on('click', function (e) { emit({ kind: 'bar', category: e.name, series: e.seriesName, value: e.value }); });
    return c;
  }

  /* ------------------------------------------------------------ scatter
     data: [{x, y, label, highlight, id}], labels: {x, y},
     options: {quadrants, quadrant_labels:[TR,TL,BL,BR], label_all, height} */
  function scatter(el, p, emit) {
    var o = opt(p), C = cols(p), pts = p.data || [], L = p.labels || {};
    var xs = pts.map(function (q) { return q.x; }), ys = pts.map(function (q) { return q.y; });
    function med(a) { var s = a.slice().sort(function (m, n) { return m - n; }); return s[Math.floor(s.length / 2)]; }
    function pad(a) { var lo = Math.min.apply(null, a), hi = Math.max.apply(null, a), s = (hi - lo) || 1; return [lo - s * .08, hi + s * .08]; }
    var xr = pad(xs), yr = pad(ys), mx = med(xs), my = med(ys), quad = o.quadrants !== false;
    function pt(q) { return { value: [q.x, q.y], name: q.label || '', id: q.id }; }
    var ax = function (name) { var a = valueAxis(); a.name = name ? name.toUpperCase() + '  →' : ''; a.nameLocation = 'middle'; a.nameTextStyle = { color: T.i300, fontFamily: DISP, fontSize: 10, fontWeight: 600 }; a.splitLine = { lineStyle: { color: T.i750 } }; return a; };
    var xA = ax(L.x), yA = ax(L.y);
    xA.min = xr[0]; xA.max = xr[1]; xA.nameGap = 28; yA.min = yr[0]; yA.max = yr[1]; yA.nameGap = 44;
    xA.axisLine = { show: true, lineStyle: { color: T.i600 } };
    var ql = o.quadrant_labels || [], g = { left: 64, right: 24, top: 16, bottom: 44 };
    var qtext = function (i, pos) { return Object.assign({ type: 'text', silent: true, style: { text: (ql[i] || '').toUpperCase(), fill: i === 0 ? T.green : T.i400, font: '600 10px ' + DISP } }, pos); };
    var c = mount(el, o.height || 420);
    c.setOption({
      tooltip: Object.assign({ trigger: 'item', formatter: function (e) { return (e.name ? '<b style="font-family:' + BODY + '">' + esc(e.name) + '</b><br>' : '') + fmt(e.value[0]) + ' · ' + fmt(e.value[1]); } }, tooltip),
      grid: g, xAxis: xA, yAxis: yA,
      graphic: quad && ql.length === 4 ? [qtext(0, { right: g.right + 8, top: g.top + 8 }), qtext(1, { left: g.left + 8, top: g.top + 8 }), qtext(2, { left: g.left + 8, bottom: g.bottom + 8 }), qtext(3, { right: g.right + 8, bottom: g.bottom + 8 })] : [],
      series: [{
        type: 'scatter', name: 'Peers', symbolSize: 8, cursor: emit ? 'pointer' : 'default',
        itemStyle: { color: rgba(T.i400, .55), borderColor: T.i900, borderWidth: 1 },
        emphasis: { itemStyle: { color: T.i200 } },
        label: { show: !!o.label_all, formatter: '{b}', position: 'right', color: T.i400, fontFamily: BODY, fontSize: 10 },
        data: pts.filter(function (q) { return !q.highlight; }).map(pt),
        markLine: quad ? { symbol: 'none', silent: true, label: { show: false }, lineStyle: { color: T.i500, type: 'dashed', width: 1 }, data: [{ xAxis: mx }, { yAxis: my }] } : undefined,
        markArea: quad ? { silent: true, itemStyle: { color: rgba(T.green, .05) }, data: [[{ coord: [mx, my] }, { coord: [xr[1], yr[1]] }]] } : undefined
      }, {
        type: 'scatter', name: 'Targets', symbolSize: 12, z: 5, cursor: emit ? 'pointer' : 'default',
        itemStyle: { color: C[0], borderColor: T.i950, borderWidth: 2, shadowBlur: 8, shadowColor: rgba(T.glow, .7) },
        label: { show: true, formatter: '{b}', position: 'right', distance: 8, color: T.i50, fontFamily: BODY, fontSize: 12, fontWeight: 600 },
        data: pts.filter(function (q) { return q.highlight; }).map(pt)
      }]
    });
    if (emit) c.on('click', function (e) { emit({ kind: 'scatter', id: e.data.id, label: e.data.name, x: e.value[0], y: e.value[1] }); });
    return c;
  }

  /* ------------------------------------------------------------ distribution (dot strip, plain HTML)
     data: [{label, unit, values:[number | {value, name, id}], highlights:[number], invert}],
     labels: names of the highlighted subjects (legend), colours: highlight colours,
     options: {peer_label, show_axis, show_legend} */
  function distribution(el, p, emit) {
    var o = opt(p), C = (p.colours && p.colours.length) ? p.colours : HL, rows = p.data || [];
    var tip = document.createElement('div'); tip.className = 'sc-tip';
    var html = rows.map(function (m, ri) {
      var vals = m.values.map(function (v) { return typeof v === 'object' ? v : { value: v }; });
      var hs = m.highlights || [];
      var nums = vals.map(function (v) { return +v.value; });
      var mean = nums.reduce(function (a, b) { return a + b; }, 0) / (nums.length || 1);
      var dev = Math.max.apply(null, nums.concat(hs).map(function (v) { return Math.abs(v - mean); })) || 1;
      var X = function (v) { return 50 + (m.invert ? -1 : 1) * (v - mean) / dev * 46; };
      var lab = esc(m.label) + (m.unit ? ' (' + esc(m.unit) + ')' : '') + hs.map(function (h, j) { return '<span class="s">·</span><span class="v" style="color:' + C[j % C.length] + '">' + fmt(h) + '</span>'; }).join('');
      var dots = vals.map(function (v, i) { return '<span class="sc-dot" data-r="' + ri + '" data-i="' + i + '" style="left:' + X(v.value) + '%"></span>'; }).join('');
      var hex = hs.map(function (h, j) { var col = C[j % C.length], l = X(h); return '<span class="sc-hex-glow" style="left:' + l + '%;background:' + col + ';z-index:' + (4 - j) + '"></span><span class="sc-hex" data-r="' + ri + '" data-h="' + j + '" style="left:' + l + '%;background:' + col + ';z-index:' + (5 - j) + '"></span>'; }).join('');
      m._vals = vals;
      return '<div class="sc-dist-row"><div class="sc-dist-label">' + lab + '</div><div class="sc-dist-track">' + dots + hex + '</div></div>';
    }).join('');
    if (o.show_axis !== false) html += '<div class="sc-dist-axis"><span>&larr; Worse</span><span>Average</span><span style="text-align:right">Better &rarr;</span></div>';
    if (o.show_legend !== false) html += '<div class="sc-legend"><span><i style="width:10px;height:10px;border-radius:50%;background:' + rgba(T.green, .6) + '"></i>' + esc(o.peer_label || 'Other players') + '</span>' +
      (p.labels || []).map(function (l, j) { return '<span><i style="width:14px;height:14px;background:' + C[j % C.length] + ';clip-path:polygon(25% 5%,75% 5%,100% 50%,75% 95%,25% 95%,0 50%)"></i>' + esc(l) + '</span>'; }).join('') + '</div>';
    el.innerHTML = html; el.appendChild(tip);
    function info(t) {
      var m = rows[+t.dataset.r]; if (!m) return null;
      if (t.dataset.h != null) { var j = +t.dataset.h; return { kind: 'distribution', metric: m.label, name: (p.labels || [])[j] || 'Selected', value: m.highlights[j], highlight: true }; }
      var v = m._vals[+t.dataset.i]; return { kind: 'distribution', metric: m.label, name: v.name || '', id: v.id, value: v.value, highlight: false };
    }
    el.addEventListener('mousemove', function (e) {
      var d = e.target.dataset && e.target.dataset.r != null ? info(e.target) : null;
      if (!d) { tip.style.display = 'none'; return; }
      tip.innerHTML = (d.name ? '<b style="font-family:' + BODY + '">' + esc(d.name) + '</b> · ' : '') + fmt(d.value);
      tip.style.display = 'block'; tip.style.left = (e.clientX + 12) + 'px'; tip.style.top = (e.clientY - 30) + 'px';
    });
    el.addEventListener('mouseleave', function () { tip.style.display = 'none'; });
    if (emit) { el.style.cursor = 'pointer'; el.addEventListener('click', function (e) { if (e.target.dataset && e.target.dataset.r != null) emit(info(e.target)); }); }
    return null;
  }

  var KINDS = { radar: radar, bar: bar, scatter: scatter, distribution: distribution };

  function render(root, kind, payload, emit) {
    injectCss();
    if (root._chart) { root._chart.dispose(); root._chart = null; }
    var o = opt(payload), head = '';
    if (o.eyebrow) head += '<div class="sc-eyebrow">' + esc(o.eyebrow) + '</div>';
    if (payload.title) head += '<h3 class="sc-title">' + esc(payload.title) + '</h3>';
    root.innerHTML = '<div class="sc-card">' + head + '<div class="sc-body"></div>' + (o.caption ? '<div class="sc-caption">' + esc(o.caption) + '</div>' : '') + '</div>';
    if (!KINDS[kind]) { root.querySelector('.sc-body').textContent = 'Unknown visual: ' + kind; return; }
    root._chart = KINDS[kind](root.querySelector('.sc-body'), payload, emit);
  }

  window.SC = { render: render, theme: T, series: SERIES, highlight: HL, pctColor: pct };
})();
