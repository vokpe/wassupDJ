-- SQLite

SELECT played_at, datetime(played_at, 'localtime') AS played_at_local
FROM transitions
ORDER BY id DESC
LIMIT 10;


