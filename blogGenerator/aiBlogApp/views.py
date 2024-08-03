from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube
from django.conf import settings
import os
import assemblyai as aai
from groq import Groq
import subprocess
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
from .models import BlogPost


load_dotenv()

@login_required
def index(request):
    return render(request,'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)


        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)


        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': " Failed to generate blog article"}, status=500)

        # save blog article to database
        new_blog_article = BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )
        new_blog_article.save()

        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

# def download_audio(link):
#     yt = YouTube(link)
#     video = yt.streams.filter(only_audio=True).first()
#     out_file = video.download(output_path=settings.MEDIA_ROOT)
#     base, ext = os.path.splitext(out_file)
#     new_file = base + '.mp3'
#     os.rename(out_file, new_file)
#     return new_file

def download_audio_yt_dlp(link, output_path):
    try:
        os.makedirs(output_path, exist_ok=True)

        # Use a timestamp to create a unique filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_template = os.path.join(output_path, f'%(title)s_{timestamp}.%(ext)s')

        yt_dlp_cmd = [
            'yt-dlp',
            '-x', '--audio-format', 'mp3',
            '-o', output_template,
            link
        ]
        subprocess.run(yt_dlp_cmd, check=True)

        # Find the newly downloaded file
        for file in os.listdir(output_path):
            if file.endswith('.mp3') and timestamp in file:
                return os.path.join(output_path, file)

        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def download_audio(link):
    return download_audio_yt_dlp(link, settings.MEDIA_ROOT)
           
def get_transcription(link):
    audio_file = download_audio(link)
    
    AAI_key = getenv('AAI')
    aai.settings.api_key = AAI_key

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    
    return transcript.text
def generate_blog_from_transcription(transcription):
    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a YouTube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"
    
    client = Groq(api_key=getenv('GROQ_API_KEY'),)
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    generated_content = "".join(chunk.choices[0].delta.content or "" for chunk in completion)

    return generated_content


def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')   
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        password = request.POST.get('password')
        if not username or not password:
            error_message = "Username and password are required"
            return render(request, 'login.html', {'error_message': error_message})
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Username or password is incorrect"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')


def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeatPassword = request.POST.get('repeatPassword')

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username,email,password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = "username already exists"
                return render(request,'signup.html',{'error_message':error_message})

        else:
            error_message = "passwords do not match"
            return render(request,'signup.html',{'error_message':error_message})
    return render(request,'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')
    

 