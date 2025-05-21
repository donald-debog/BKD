# BKD Photo Gallery

This is a Next.js application that displays photos from photo booth sessions stored in Supabase.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   # or
   yarn
   # or
   pnpm install
   ```

3. Create a `.env.local` file in the root directory with the following variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   ```

4. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser to see the result.

## Supabase Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Create a table called `photos` with the following columns:
   - `id` - UUID, primary key
   - `created_at` - timestamp with time zone, default: now()
   - `session_id` - text, not null
   - `url` - text, not null
   - Add any additional columns as needed

3. Set up storage buckets for the photos
4. Update the `next.config.js` file with your Supabase storage URL domain

## Deploying to Vercel

1. Push your code to a GitHub repository
2. Create a new project in Vercel and link to your repository
3. Set the environment variables in the Vercel project settings
4. Deploy! 