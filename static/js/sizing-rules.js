/* 经验估算，不是压测。单位：月访问量为次/月，峰值请求为次/秒，内存输出为 MB。 */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.SizingRules = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  var FLOORS = {
    static: { vcpu: 1, ramMb: 1024 },
    cms: { vcpu: 1, ramMb: 2048 },
    api: { vcpu: 2, ramMb: 2048 }
  };

  function parseOptionalInt(raw) {
    if (raw == null) return { empty: true };
    var text = String(raw).trim();
    if (text === "") return { empty: true };
    if (!/^\d+$/.test(text)) return { error: "not-integer" };
    return { value: Number(text) };
  }

  function estimate(input) {
    var workload = input && input.workload;
    if (!FLOORS[workload]) return { ok: false, error: "workload" };
    var views = parseOptionalInt(input.pageviews);
    if (views.error) return { ok: false, error: "pageviews" };
    var rps = parseOptionalInt(input.rps);
    if (rps.error) return { ok: false, error: "rps" };
    if (!views.empty && views.value > 10000000) return { ok: false, error: "pageviews-range" };
    if (!rps.empty && rps.value > 1000) return { ok: false, error: "rps-range" };

    var vcpu = FLOORS[workload].vcpu;
    var ramMb = FLOORS[workload].ramMb;
    var notes = ["floor"];
    if (workload === "static" && !views.empty && views.value > 100000) {
      ramMb = Math.max(ramMb, 2048);
      notes.push("static-views");
    }
    if (workload === "cms" && !views.empty && views.value > 50000) {
      vcpu = Math.max(vcpu, 2);
      ramMb = Math.max(ramMb, 4096);
      notes.push("cms-views");
    }
    if (workload === "api" && !views.empty) notes.push("api-ignores-views");
    if (workload === "api" && !rps.empty && rps.value > 20) {
      vcpu = Math.max(vcpu, 2);
      ramMb = Math.max(ramMb, 4096);
      notes.push("api-rps-20");
    }
    if (workload === "api" && !rps.empty && rps.value > 100) {
      vcpu = 4;
      ramMb = 8192;
      notes.push("api-top");
    }
    return { ok: true, vcpu: vcpu, ramMb: ramMb, ramGb: ramMb / 1024, notes: notes };
  }

  return { estimate: estimate, floors: FLOORS };
});
