# Test Data Catalog

| File | S3 URL | Description | Size | MD5 | Vars | Groups | Depth | Dtype | Shape | Chunks | Chunk Size | Compression |
|------|--------|-------------|------|-----|------|--------|-------|-------|-------|--------|------------|-------------|
| [`float32_2d_zlib_chunked_10mb_cloud_optimized.nc`](netcdf4_generated/data/float32_2d_zlib_chunked_10mb_cloud_optimized.nc) | `-` | Cloud-optimized HDF5 with 10 MB chunks and metadata consolidated in a single block | 162 MB | `6977eac5912213f89ab9a044c94fd7b4` | 4 | 0 | 1 | float32 | (100, 512, 1024) | (5, 512, 1024) | 10 MB | gzip(4) |
| [`float32_2d_zlib_chunked_10mb_fragmented.nc`](netcdf4_generated/data/float32_2d_zlib_chunked_10mb_fragmented.nc) | `-` | Non-optimized HDF5 with 10 MB chunks and metadata scattered throughout the file | 161 MB | `3df93847a438931a484249e744d1fff6` | 4 | 0 | 1 | float32 | (100, 512, 1024) | (5, 512, 1024) | 10 MB | gzip(4) |
| [`float32_2d_zlib_chunked_cloud_optimized.nc`](netcdf4_generated/data/float32_2d_zlib_chunked_cloud_optimized.nc) | `-` | Cloud-optimized HDF5 with metadata consolidated in a single block for efficient remote access | 162 MB | `35454c4a50d8c071b443281f29dda43e` | 4 | 0 | 1 | float32 | (100, 512, 1024) | (1, 128, 256) | 128 KB | gzip(4) |
| [`float32_2d_zlib_chunked_fragmented.nc`](netcdf4_generated/data/float32_2d_zlib_chunked_fragmented.nc) | `-` | Non-optimized HDF5 with metadata scattered throughout the file | 161 MB | `36404e3b5fd080e0c1235b41a88de69a` | 4 | 0 | 1 | float32 | (100, 512, 1024) | (1, 128, 256) | 128 KB | gzip(4) |
