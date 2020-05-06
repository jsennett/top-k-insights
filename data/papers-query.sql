-- papers
select pa.paperid as paperid, v.name as venue_name, v.year as year, v.school as school, v.type as venue_type
FROM papers p, venue v
WHERE pa.paperid = p.id
AND p.venue = v.id
AND v.year between 1990 AND 2015
LIMIT 10;
