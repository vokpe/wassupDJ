-- SQLite

SELECT title, artist, bpm_tag, key_tag, substr(file_path,1,80) AS file
FROM tracks
ORDER BY id DESC
LIMIT 20;

SELECT COUNT(*) 
FROM tracks
WHERE file_path LIKE '/Volumes/!spidz%';

SELECT title, artist, file_path
FROM tracks
WHERE file_path LIKE '/Volumes/!spidz%'
ORDER BY RANDOM()
LIMIT 10;

