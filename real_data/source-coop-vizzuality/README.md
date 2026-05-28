Includes data from

https://source.coop/vizzuality

## Custom CRS

```
    Crs:              PROJCS["unknown",GEOGCS["unknown",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mollweide"],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]
```

```bash
pixi run gdal_translate \
  -srcwin 0 0 128 128 \
  -of COG \
  -co BLOCKSIZE=128 \
  /vsicurl/https://data.source.coop/vizzuality/hfp-100/hfp_2017_100m_v1-2_cog.tif \
  hfp_2017_100m_v1-2_cog.tif
```
