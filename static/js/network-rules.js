/* 只映射本站线路页已经写明的对应关系，不估计延迟或带宽。 */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.NetworkRules = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function lookup(input) {
    var isp = input && input.isp;
    var audience = input && input.audience;
    var knownIsp = { telecom: 1, unicom: 1, mobile: 1, overseas: 1, unknown: 1 };
    var knownAudience = { china: 1, overseas: 1 };
    if (!knownIsp[isp] || !knownAudience[audience]) return { ok: false, error: "choice" };
    if (isp === "unknown") return { ok: true, id: "unknown" };
    if (isp === "overseas" || audience === "overseas") return { ok: true, id: "no-china-line" };
    if (isp === "telecom") return { ok: true, id: "cn2-gia" };
    if (isp === "unicom") return { ok: true, id: "as9929" };
    if (isp === "mobile") return { ok: true, id: "cmin2" };
    return { ok: false, error: "choice" };
  }
  return { lookup: lookup };
});
