# AI Blog Generator

AI Blog Generator is a Django-based application that allows users to generate blog articles from YouTube videos. Users can sign up, log in, and generate blogs that are stored in their accounts for later access. The application includes an admin panel and uses PostgreSQL as the database.

## Features

- User authentication (signup, login)
- Generate blog articles from YouTube video links
- Store and access generated blogs in user accounts
- Admin panel for managing the application
- Uses `pytube` to get the title of the video 
- Uses `yt-dlp` to download the MP3 file of the YouTube video
- Uses `assembly.ai` for audio transcription
- Uses `llama3.1` from `groq.com` for blog generation
- Media files are stored in the media folder

**Note:** We can use `pytube` to download video in mp3 but at my time it was giving me error that's why i used `yt-dlp`.

## Prerequisites

- Python 3.11.7 or above 
- Django
- [PostgreSQL](https://www.postgresql.org/download/)
- `pytube`
- `yt-dlp`
- `assemblyai`
- `groq`

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/iammuhammadnoumankhan/AI-Blog-Generator.git
   ```

2. Navigate to the project directory where `manage.py` is located:
   ```sh
   cd AI-Blog-Generator
   ```

3. Create a virtual environment:
   ```sh
   python -m venv myenv
   ```

4. Activate the virtual environment:
   ```sh
   .\myenv\Scripts\activate
   ```

5. Install the dependencies:
   ```sh
   pip install django groq assemblyai pytube yt-dlp
   ```

6. Set up the PostgreSQL database and update the `DATABASES` setting in `settings.py` with your database configuration.

- First download and install PostgreSQL
- Open terminal
- activate: `psql -U postgres`
- Create PostgreSQL database: `CREATE DATABASE "BlogDatabase";`
- Create user: `CREATE USER myusername WITH PASSWORD 'mypassword';`
- Grant access to the user for particular database: `GRANT ALL PRIVILEGES ON DATABASE "BlogDatabase" TO myusername;`
- Grant Schema access:
    - ```\c "Blog Database"```
    - GRANT ALL ON SCHEMA public TO your_username;


7. Apply the migrations:
- `python manage.py makemigrations`
- `python manage.py migrate`

8. Create a superuser for the admin panel:
   ```sh
   python manage.py createsuperuser
   ```
9. In `.env` file provide credientials for database, assemblyai api, groq api.

10. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Usage

1. Sign up and log in to the application.
2. Enter a YouTube video link to generate a blog article.
3. Access your generated blogs from your account.

## Admin Panel

To access the admin panel, go to `/admin` and log in with the superuser credentials.

## API Keys

Make sure to set up your API keys for `assembly.ai` and `groq` in `.env`.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

### License
This project is licensed under the MIT License.

### Notes

- Ensure that [ffmpeg](https://ffmpeg.org/download.html) is installed and available in your system's PATH for `yt-dlp` to function correctly e.g: `C:\ffmpeg\bin`.
- Update the `MEDIA_ROOT` and `MEDIA_URL` settings in `settings.py` to configure media file storage.

```On default Media will be store in 'media' folder, make sure it is present in root directory where manage.py exist```

Thank You!!!

[Muhammad Nouman Khan](https://www.linkedin.com/in/muhammad-nouman-khan-248530233/)