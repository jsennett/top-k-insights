-- paperauths
select pa.paperid, pa.authid, v.year as year
from paperauths pa, papers p, venue v
WHERE pa.paperid = p.id
AND p.venue = v.id
AND v.year between 1990 AND 2015;