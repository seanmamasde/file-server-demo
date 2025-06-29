CREATE TABLE
  IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    mime_type TEXT,
    content BYTEA NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW ()
  );
