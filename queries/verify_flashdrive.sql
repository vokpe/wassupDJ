-- ===== Verify library + history ingest from flash drive =====

-- 1) Basic table sanity
PRAGMA table_info(tracks);
PRAGMA table_info(transitions);

-- 2) Overall counts
SELECT COUNT(*) AS total_tracks FROM tracks;
SELECT COUNT(*) AS total_transitions FROM transitions;

-- 3) How many tracks came specifically from your flash drive
--    Change the path if your volume name differs
SELECT COUNT(*) AS tracks_from_flashdrive
FROM tracks
WHERE file_path LIKE '/Volumes/!spidz%';

-- 4) Sample recently inserted tracks (show path prefix to confirm)
SELECT
  title,
  artist,
  COALESCE(bpm_serato, bpm_tag) AS bpm,
  COALESCE(key_serato, key_tag) AS key_text,
  substr(file_path, 1, 80) AS file
FROM tracks
ORDER BY id DESC
LIMIT 20;

-- 5) Random sample FROM the flash drive
SELECT
  title,
  artist,
  substr(file_path, 1, 80) AS file
FROM tracks
WHERE file_path LIKE '/Volumes/!spidz%'
ORDER BY RANDOM()
LIMIT 10;

-- 6) Top repeated transitions (most frequent pairs in your history)
SELECT
  t1.title || ' → ' || t2.title AS transition,
  COUNT(*) AS freq
FROM transitions tr
JOIN tracks t1 ON tr.prev_track_id = t1.id
JOIN tracks t2 ON tr.next_track_id = t2.id
GROUP BY t1.title, t2.title
ORDER BY freq DESC
LIMIT 10;

-- 7) 10 most recent transitions with timestamps (if available)
SELECT
  t1.title || ' → ' || t2.title AS transition,
  tr.played_at
FROM transitions tr
JOIN tracks t1 ON tr.prev_track_id = t1.id
JOIN tracks t2 ON tr.next_track_id = t2.id
ORDER BY tr.id DESC
LIMIT 10;
