<!-- # Supabase Setup Guide

## 1. Create Supabase Project

1. Go to [https://supabase.com/](https://supabase.com/) and sign up or log in
2. Create a new project
3. Note down your project URL and anon key from the API settings

## 2. Set Up Database Tables

Execute the following SQL in the Supabase SQL Editor:

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_email TEXT REFERENCES users(email),
  query TEXT NOT NULL,
  feedback TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Search history table
CREATE TABLE search_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_email TEXT REFERENCES users(email),
  query TEXT NOT NULL,
  num_results INTEGER NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_feedback_user_email ON feedback(user_email);
CREATE INDEX idx_search_history_user_email ON search_history(user_email);
```

## 3. Set Environment Variables

Create a `.env` file in your project root:
 -->
