"""Build cities.tsv.gz from GeoNames cities5000.txt (CC-BY 4.0, geonames.org).
Usage: python build_cities.py /path/cities5000.txt
Rows: name<TAB>display<TAB>country<TAB>lat<TAB>lon<TAB>tz<TAB>population<TAB>alt1|alt2|...
"""
import gzip, sys, os
src = sys.argv[1]
out = os.path.join(os.path.dirname(__file__), "cities.tsv.gz")
with open(src, encoding="utf-8") as f, gzip.open(out, "wt", encoding="utf-8") as o:
    for line in f:
        p = line.rstrip("\n").split("\t")
        alts = [a for a in p[3].split(",") if a and len(a) <= 60 and not a.isupper()]
        o.write("\t".join([p[1], p[2], p[8], p[4], p[5], p[17], p[14] or "0", "|".join(alts)]) + "\n")
