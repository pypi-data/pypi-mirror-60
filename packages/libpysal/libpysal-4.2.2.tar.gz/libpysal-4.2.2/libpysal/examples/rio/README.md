# rio grande do sul

## Description
Cities of the Brazilian State of Rio Grande do Sul


## Files

* 43MUE250GC_SIR.dbf: attribute data (k=2)
* 43MUE250GC_SIR.shp: Polygon shapefile (n=499)
* 43MUE250GC_SIR.shx: spatial index
* 43MUE250GC_SIR.cpg: encoding file 
* 43MUE250GC_SIR.prj: projection information 
* map_RS_BR.dbf: attribute data (k=3)
* map_RS_BR.shp: Polygon shapefile (no lakes) (n=497)
* map_RS_BR.prj: projection information
* map_RS_BR.shx: spatial index



## Reference
Renan Xavier Cortes <renanxcortes@gmail.com>  
Reference: https://github.com/pysal/pysal/issues/889#issuecomment-396693495


## Remote

* url: https://github.com/sjsrey/rio_grande_do_sul/archive/master.zip
* checksum: e5629e782e77037912cbfc40d3738f4752e27b5bdfc99a95368b232047b53ff3



## Example
```
import geopandas
import libpysal
pth = libpysal.examples.get_path('43MUE250GC_SIR.shp')
gdf = geopandas.read_file(pth)
gdf.head()

```
