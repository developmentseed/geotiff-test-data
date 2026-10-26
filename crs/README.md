# GeoKey-to-CRS conformance corpus

GeoTIFF files describe their coordinate reference system with GeoKeys. A reader that builds a CRS from those keys has to make the same choices libgeotiff and GDAL make: which projection method a `ProjCoordTransGeoKey` code means, which of several equivalent keys holds each parameter, what units the values are in, and how the datum, ellipsoid and prime meridian combine. This directory pins those choices down as data.

GDAL/PROJ is the oracle. For every case, GDAL writes the file and then reads it back; the manifest records both the raw GeoKeys GDAL wrote and the CRS GDAL/PROJ reads from them. A reader is conformant when, for every tested fixture, the CRS it builds equals the one in the manifest.

Consumers today: [async-geotiff](https://github.com/developmentseed/async-geotiff) (Python, pyproj) and the GeoTIFF package in [deck.gl-raster](https://github.com/developmentseed/deck.gl-raster) (TypeScript, no PROJ database). The design, including the decisions behind the manifest and table schemas and the findings about GDAL and PROJ that shaped them, is in [dev-docs/specs/2026-10-26-geokey-crs-conformance-design.md](../dev-docs/specs/2026-10-26-geokey-crs-conformance-design.md); its later sections describe the async-geotiff builder that consumes this corpus.

## Layout

```
crs/
  cases.py                  # the case list (data only)
  generate_crs.py           # writes fixtures/, manifest.json, fills epsg/
  geokeys.py                # GeoKey id table, raw decoder and encoder
  normalize.py              # name-free CRS core and the test point
  geotiff-ct-methods.json   # CT code -> PROJ method table (see below)
  manifest.json             # one row per fixture
  fixtures/<name>.tif       # 8x8 uint8, plain GTiff, no compression
  epsg/<code>.json          # cached https://epsg.io/<code>.json for coded cases
```

## Regenerating

```bash
pixi run generate-crs                  # rewrites fixtures/ and manifest.json
pixi run generate-crs --refresh-epsg   # also refetches epsg/*.json
```

The generator is deterministic for the pinned GDAL/PROJ versions in `pixi.lock`; `scripts/check.sh` runs it in CI and fails on any diff. It only touches the network for an `epsg/<code>.json` that is missing. `manifest.json` records the GDAL, PROJ, rasterio and pyproj versions under `generator`; those are the oracle. The line citations in the CT table refer to the versions named in its `sources`, which may be slightly older.

## Cases

Each `Case` in `cases.py` has a `kind`:

- `proj`: a PROJ string. GDAL turns it into user-defined GeoKeys. This is the code path the corpus exists to test. Parameters are chosen so GDAL does not recognise an EPSG CRS and write only its code.
- `epsg`: an authority code such as `EPSG:32633` (or `ESRI:54009`). GDAL writes coded keys. The `epsg.io` response is cached next to the fixture so readers without a PROJ database can test offline.
- `wkt`: a WKT1 string, for inputs a PROJ string cannot express (a named prime meridian in degrees, grads with Greenwich, Polar Stereographic variants, ESRI names).
- `geokeys`: a raw GeoKey dictionary written with tifffile, for key arrangements GDAL never produces itself (an EPSG-coded prime meridian).

The case list covers every `ProjCoordTransGeoKey` code GDAL can write, each distinct key arrangement GDAL emits for it, US survey feet and international feet, grads, EPSG-coded and user-defined datums, EPSG-coded ellipsoids with and without explicit axes, a sphere, TOWGS84, Greenwich and non-Greenwich prime meridians, `ProjectionGeoKey` without a CT code, `ESRI PE String` citations, and one method (Equal Earth) GDAL cannot encode at all.

## Manifest schema

`manifest.json` is `{"schema_version": 1, "generator": {...}, "cases": [...]}` with `cases` sorted by `name`. Each row:

| field | meaning |
|---|---|
| `name` | the case name; the fixture is `fixtures/<name>.tif` |
| `file` | path relative to `crs/` |
| `input` | `{"kind", "value"}` as given in `cases.py` |
| `note` | why the case exists or why it is flagged; free text |
| `tags` | free-form labels (`ct:9`, `linear:9003`, `pm:paris`, ...) for filtering |
| `geokeys` | exactly what GDAL wrote, keyed by GeoTIFF key name without the `GeoKey` suffix (`ProjCoordTrans`, `GeogTOWGS84`). SHORT values are integers, a single DOUBLE is a number, several DOUBLEs are a list, ASCII values are strings with the trailing `\|` terminator removed. `{}` when GDAL wrote no keys. |
| `gdal.projjson` | the CRS GDAL/PROJ reads from the file, as PROJJSON; `null` when GDAL reads no CRS |
| `gdal.proj4` | the same CRS as a PROJ string; `null` when PROJ cannot export it |
| `gdal.roundtrip` | whether the input CRS equals the read-back CRS (PROJ's `EQUIVALENT` comparison); `null` for `geokeys` cases |
| `core` | a name-free summary of `gdal.projjson`, see below; `null` when `gdal.projjson` is |
| `point` | `{"lon", "lat", "x", "y"}`: a lon/lat in degrees from Greenwich near the projection origin and its projected coordinates; `null` when `gdal.proj4` is |
| `epsg_json` | `epsg/<code>.json` for `epsg` cases, else `null` |

**Which rows to test.** A row with `gdal.projjson == null` or `gdal.proj4 == null` is flagged: GDAL could not encode the CRS (Equal Earth) or PROJ cannot operate on what it read (Polar Stereographic off the pole with a scale factor). Readers skip those rows; `note` says why. Every other row is a conformance case, including rows whose `gdal.roundtrip` is `false`: the oracle is what GDAL reads, not what was written.

**`core`.** Readers with PROJ compare `gdal.projjson` with PROJ's equivalence test. Readers without it compare `core`, which drops every name and id and converts every value to degrees, metres and unity:

```jsonc
{
  "type": "ProjectedCRS",                       // ProjectedCRS | GeographicCRS | BoundCRS
  "method": {"name": "Lambert Conic Conformal (2SP)", "epsg": 9802},   // null for geographic; epsg null for PROJ-only methods
  "parameters": [{"epsg": 8821, "name": "Latitude of false origin", "value": 40.16667}, ...],  // degrees / metres / unity
  "ellipsoid": {"a": 6378137.0, "rf": 298.257222101, "b": null},         // b set and rf null for a sphere
  "prime_meridian_deg": 0.0,
  "angular_unit_deg": 1.0,                       // size of the geographic CS unit in degrees (0.9 for grads)
  "linear_unit_m": 0.3048006096012192,           // size of the projected CS unit in metres; null for geographic
  "axes": ["east", "north"],                     // axis directions in order, see below
  "towgs84": null                                // 3 or 7 numbers for BoundCRS rows
}
```

`axes` is `["east", "north"]` for most projected rows, `["west", "south"]` for Transverse Mercator (South Orientated), and for Polar Stereographic (CT 15, every variant) `["south", "south"]` when the resolved latitude is positive and `["north", "north"]` when it is negative: that is how PROJ imports WKT1 `Polar_Stereographic` without axis nodes, and GDAL's reading carries it. Geographic rows are `["north", "east"]` (latitude first). EPSG-coded rows carry whatever the registry says (`epsg_2065` Krovak is `["south", "west"]`).

**Comparing `core`.** Match parameters by EPSG code, or by name when `epsg` is null. A table parameter missing from `core.parameters` means PROJ dropped a zero-valued parameter (`Latitude of natural origin` for Equidistant Cylindrical, see the CT 17 note); treat it as 0. Compare numbers with a tolerance: values such as `299999.9999999998` (feet converted to metres) and `46.800000000000104` (grads converted to degrees) are the result of unit conversion, so use a relative tolerance of about `1e-9` with an absolute floor of `1e-6`.

**`point`.** `(lon, lat)` is projected with a transformer from a degree, Greenwich longlat CRS on the row's own ellipsoid to the read-back CRS, so no datum shift is involved. `x` and `y` are rounded to millimetres, and the generator keeps the committed value when a regeneration moves it by less than a millimetre, because PROJ's last digits differ between platforms (macOS arm64 and Linux x86_64 disagree by a few micrometres). Compare with a tolerance of at least a millimetre. For geographic rows the transform still runs, so `(x, y)` is in the row's own angular unit and prime meridian. A reader checks its CRS by projecting the same `(lon, lat)` the same way and comparing to `(x, y)`; it is a cheap smoke test, not a substitute for the CRS comparison.

## CT method table

`geotiff-ct-methods.json` says, for each `ProjCoordTransGeoKey` code, which PROJ/EPSG method it becomes and how each parameter is read from the GeoKeys. It is transcribed from libgeotiff's `GTIFFetchProjParms` (`geo_normalize.c`) and GDAL's `GTIFGetOGISDefn` (`gt_wkt_srs.cpp`); the `sources` object pins the commit and tag, and every row cites its lines. Implementations interpret the table; nothing in it is meant to be re-typed by hand.

```jsonc
{
  "schema_version": 1,
  "sources": {"libgeotiff": "...", "gdal": "...", "proj": "..."},
  "units": {                                   // unit normalization is applied once, outside the table
    "angular_keys": [...],                     // keys scaled by the GeogAngularUnits factor into degrees
    "linear_keys": [...],                      // keys scaled by the ProjLinearUnits factor into metres
    "source": "geo_normalize.c#L2227-L2277"
  },
  "methods": {
    "<ct code>": {
      "ct_name": "CT_TransverseMercator",
      "libgeotiff": "geo_normalize.c#L1774-L1816",
      "unsupported": "reason",                 // only for 2, 5, 6; no other fields then
      "variants": [                            // first variant whose `when` matches wins; the last has no `when`
        {
          "when": {...},                       // see below; omitted on the default variant
          "method": {"name": "Transverse Mercator", "epsg": 9807, "proj": "tmerc"},
          "axes": ["east", "north"],           // optional; CT 27 is ["west", "south"]; CT 15 is sign-dependent, see below
          "parameters": [
            {
              "name": "Latitude of natural origin",   // PROJ/EPSG parameter name
              "epsg": 8801,                            // EPSG parameter code; null for PROJ-only methods
              "proj": "lat_0",                         // PROJ string key
              "kind": "angular",                       // angular | linear | scale | azimuth
              "keys": ["ProjNatOriginLat", "ProjFalseOriginLat", "ProjCenterLat"],  // first present wins
              "default": 0.0
            }
          ],
          "gdal": "gt_wkt_srs.cpp#L1440-L1443"
        },
        {"unrepresentable": "reason"}          // a variant PROJ has no operation for
      ]
    }
  }
}
```

How to read a method: resolve the union of all its variants' parameters (they share raw inputs; a rule may name a parameter that only another variant lists) by taking the first key in `keys` that is present in the directory (a value of `0` counts as present), else `default`; scale `angular` values by the angular unit factor and `linear` values by the linear unit factor, and leave `scale` and `azimuth` untouched (libgeotiff does not convert `ProjAzimuthAngle`); then evaluate each variant's `when` in order and build the first that matches.

`when` grammar:

```jsonc
{"present": "ProjStdParallel1"}                                         // key present in the directory
{"abs_value": {"param": "Latitude of natural origin", "equals": 90}}    // |resolved value| equals
{"value": {"param": "Scale factor at natural origin", "equals": 1}}     // resolved value equals
{"any": [...]}  /  {"all": [...]}
```

The three rules in use:

- **CT 7 Mercator**: `ProjStdParallel1` present selects variant B (EPSG 9805), otherwise variant A (9804).
- **CT 15 Polar Stereographic**: PROJ decides from values (`io.cpp`, WKT1 `Polar_Stereographic` import). Scale factor exactly 1 selects variant B (9829) with the latitude as the standard parallel, even at the pole; otherwise a latitude at a pole selects variant A (9810); otherwise PROJ keeps a non-EPSG method it cannot operate on, which is the `unrepresentable` variant. Whichever variant applies, the projected axes are `["south", "south"]` for a positive latitude and `["north", "north"]` for a negative one (the table's `axes` field cannot express a sign rule, so this is stated here and pinned by a test).
- **CT 7 Mercator** reads its scale factor from `ProjScaleAtNatOrigin` only; the `ProjScaleAtCenter` fallback that Transverse Mercator, LCC 1SP and Oblique Stereographic have does not apply (`geo_normalize.c#L1739-L1747`).
- **CT 3, 9815 and 4** are separate codes for Hotine Oblique Mercator variant A, variant B and Laborde; they share keys but name their parameters differently. The rectified grid angle defaults to 90.

Codes 2, 5 and 6 (Modified Alaska, Rosenmund, spherical oblique Mercator) have no read case in GDAL and no fixture.

## Known GDAL and PROJ behaviours the corpus documents

- GDAL writes no GeoKeys for Equal Earth (it would write a `.aux.xml` sidecar, which the generator disables). Row `eqearth` is flagged.
- GDAL identifies some user-defined conversions: a Transverse Mercator matching a UTM zone is written as `ProjectionGeoKey = 160xx` with no CT code (`utm_bessel`).
- GDAL never writes `GeogPrimeMeridianGeoKey` codes, only `GeogPrimeMeridianLongGeoKey` plus a `Primem = <name>` citation entry (`lcc_1sp_paris_deg_wkt`); `lcc_1sp_pm_epsg_tifffile` is hand-written to cover the coded form libgeotiff reads.
- For `+pm=paris` input GDAL writes the geographic CRS in grads and a prime meridian longitude its own reader converts three times over (`lcc_1sp_paris_grad`, see the spec's Q3). The row is tested against GDAL's reading like any other; readers that follow libgeotiff's single conversion will not match it.
- Polar Stereographic off the pole with a scale factor other than 1 reads back as a non-EPSG `Polar_Stereographic` method with WKT1 parameter names that PROJ cannot export (`stere_polar_scaled_wkt`). Flagged.
- `ProjAzimuthAngleGeoKey` is never unit-converted by libgeotiff, unlike every other angular key.

## Tests

`tests/test_crs_*.py` check the helpers, that every fixture's raw GeoKeys match its manifest row, that no PROJ-string case collapsed to an EPSG code, that exactly the expected rows are flagged, and that the CT table and the manifest agree on method names and cover each other's codes.
