CREATE TABLE IF NOT EXISTS subscribers (
  id SERIAL PRIMARY KEY,
  phone VARCHAR(15) UNIQUE NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add a trigger to automatically update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_subscribers_updated_at
    BEFORE UPDATE ON subscribers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 