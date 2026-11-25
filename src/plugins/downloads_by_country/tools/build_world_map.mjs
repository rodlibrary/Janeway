/*
 * Builds data/world_map.json, the country shapes used by the
 * Downloads by Country page. You only need to re-run this to change the
 * map's projection, size or level of detail.
 *
 *   mkdir /tmp/mapbuild && cd /tmp/mapbuild
 *   npm init -y && npm install world-atlas@2 topojson-client@3 d3-geo@3 i18n-iso-countries@7
 *   cp <this file> . && node build_world_map.mjs > world_map.json
 *   cp world_map.json <repo>/src/plugins/downloads_by_country/data/
 *
 * Shapes come from Natural Earth (public domain) via the world-atlas package.
 * Countries too small to draw at 1:110m (e.g. Singapore, Malta, Bahrain) are
 * taken from the 1:50m data and drawn as dots, so their downloads still show.
 */
import { readFileSync } from "node:fs";
import { feature } from "topojson-client";
import { geoNaturalEarth1, geoPath, geoCentroid } from "d3-geo";
import countries from "i18n-iso-countries";

const WIDTH = 960;
const load = (f) => JSON.parse(readFileSync(`node_modules/world-atlas/${f}`, "utf8"));
const toFeatures = (topo) => feature(topo, topo.objects.countries).features;

// Natural Earth gives some places without an ISO numeric id.
const NAME_TO_ALPHA2 = { Kosovo: "XK", "N. Cyprus": "CY", Somaliland: "SO" };

function alpha2(f) {
  if (f.id) {
    const code = countries.numericToAlpha2(f.id);
    if (code) return code;
  }
  return NAME_TO_ALPHA2[f.properties.name] || null;
}

const large = toFeatures(load("countries-110m.json")).filter((f) => alpha2(f) !== "AQ");
const detailed = toFeatures(load("countries-50m.json"));

const projection = geoNaturalEarth1().fitWidth(WIDTH, { type: "FeatureCollection", features: large });
const path = geoPath(projection);
const [[, y0], [, y1]] = path.bounds({ type: "FeatureCollection", features: large });
const height = Math.ceil(y1 - y0 + 2);
projection.translate([projection.translate()[0], projection.translate()[1] - y0 + 1]);

const round = (d) => d.replace(/(\d+\.\d)\d+/g, "$1");

const shapes = {};
for (const f of large) {
  const code = alpha2(f);
  if (!code) continue;
  const d = round(path(f));
  shapes[code] = shapes[code] ? { ...shapes[code], d: shapes[code].d + d } : { code, name: f.properties.name, d };
}

const dots = [];
for (const f of detailed) {
  const code = alpha2(f);
  if (!code || code === "AQ" || shapes[code]) continue;
  const [x, y] = projection(geoCentroid(f));
  if (Number.isFinite(x) && Number.isFinite(y)) {
    dots.push({ code, name: f.properties.name, x: +x.toFixed(1), y: +y.toFixed(1) });
  }
}

process.stdout.write(
  JSON.stringify({
    source: "Natural Earth via world-atlas 2 (public domain); Natural Earth projection",
    width: WIDTH,
    height,
    shapes: Object.values(shapes).sort((a, b) => a.code.localeCompare(b.code)),
    dots: dots.sort((a, b) => a.code.localeCompare(b.code)),
  })
);
