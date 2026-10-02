Includes data from

https://source.coop/dataforcanada

## User-defined Oblique Stereographic CRS

New Brunswick Stereographic, equivalent to EPSG:2953, but stored as a
user-defined projected CRS (`ProjectedCSTypeGeoKey = 32767`) with
`ProjCoordTransGeoKey = 16` (`CT_ObliqueStereographic`). The projection origin
is stored in `ProjNatOriginLatGeoKey`, `ProjNatOriginLongGeoKey` and
`ProjScaleAtNatOriginGeoKey`, not the `ProjCenter*` keys.

See https://github.com/source-cooperative/cog-viewer/issues/40.

`listgeo -no_norm O2308000_7586000_cog.tif`:

```
   Keyed_Information:
      GTModelTypeGeoKey (Short,1): ModelTypeProjected
      GTRasterTypeGeoKey (Short,1): RasterPixelIsArea
      GTCitationGeoKey (Ascii,42): "NAD83(CSRS) / New Brunswick Stereographic"
      GeographicTypeGeoKey (Short,1): User-Defined
      GeogCitationGeoKey (Ascii,43): "GCS Name = NAD83(CSRS)|Primem = Greenwich|"
      GeogGeodeticDatumGeoKey (Short,1): Code-6140 (NAD83 Canadian Spatial Reference System)
      GeogAngularUnitsGeoKey (Short,1): Angular_Degree
      GeogSemiMajorAxisGeoKey (Double,1): 6378137
      GeogInvFlatteningGeoKey (Double,1): 298.257222101
      GeogPrimeMeridianLongGeoKey (Double,1): 0
      ProjectedCSTypeGeoKey (Short,1): User-Defined
      ProjectionGeoKey (Short,1): User-Defined
      ProjCoordTransGeoKey (Short,1): CT_ObliqueStereographic
      ProjLinearUnitsGeoKey (Short,1): Linear_Meter
      ProjNatOriginLongGeoKey (Double,1): -66.5
      ProjNatOriginLatGeoKey (Double,1): 46.5
      ProjFalseEastingGeoKey (Double,1): 2500000
      ProjFalseNorthingGeoKey (Double,1): 7500000
      ProjScaleAtNatOriginGeoKey (Double,1): 0.999912
      End_Of_Keys.
```

GDAL identifies the source CRS as EPSG:2953 by name when reading, so a plain
`gdal_translate` writes `ProjectedCSTypeGeoKey = 2953` instead. Assigning the
same WKT without the `PROJCS` and `GEOGCS` authority codes makes GDAL write the
same user-defined geo keys as the source file:

```bash
pixi run gdal_translate \
  -srcwin 0 0 128 128 \
  -a_srs 'PROJCS["NAD83(CSRS) / New Brunswick Stereographic",GEOGCS["NAD83(CSRS)",DATUM["NAD83_Canadian_Spatial_Reference_System",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6140"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]],PROJECTION["Oblique_Stereographic"],PARAMETER["latitude_of_origin",46.5],PARAMETER["central_meridian",-66.5],PARAMETER["scale_factor",0.999912],PARAMETER["false_easting",2500000],PARAMETER["false_northing",7500000],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]' \
  -of COG \
  -co BLOCKSIZE=128 \
  /vsicurl/https://data.source.coop/dataforcanada/test/O2308000_7586000_cog.tif \
  O2308000_7586000_cog.tif
```
