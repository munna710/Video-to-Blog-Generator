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
from transformers import pipeline
import logging
# Create your views here.

# Configure logging
logging.basicConfig(level=logging.DEBUG)
@login_required
def index(request):
    return render(request,'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            logging.debug(f"Received YouTube link: {yt_link}")
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        # get yt title
        try:
            title = yt_title(yt_link)
            logging.debug(f"Retrieved YouTube title: {title}")
        except Exception as e:
            logging.error(f"Error retrieving YouTube title: {e}")
            return JsonResponse({'error': 'Failed to retrieve YouTube title'}, status=500)

        # get transcript
        try:
            transcription = get_transcription(yt_link)
            logging.debug(f"Retrieved transcription: {transcription}")
            if not transcription:
                return JsonResponse({'error': 'Transcription failed'}, status=500)
        except Exception as e:
            logging.error(f"Error retrieving transcription: {e}")
            return JsonResponse({'error': 'Failed to retrieve transcription'}, status=500)

        # generate blog
        try:
            blog_content = generate_blog_from_transcription(transcription)
            logging.debug(f"Generated blog content: {blog_content}")
            if not blog_content:
                return JsonResponse({'error': 'Blog generation failed'}, status=500)
        except Exception as e:
            logging.error(f"Error generating blog content: {e}")
            return JsonResponse({'error': 'Failed to generate blog content'}, status=500)

        # save blog
        try:
            new_blog_article = BlogPost.objects.create(
                user=request.user,
                youtube_title=title,
                youtube_link=yt_link,
                generated_content=blog_content,
            )
            new_blog_article.save()
            logging.debug(f"Saved new blog article: {new_blog_article.id}")
        except Exception as e:
            logging.error(f"Error saving blog article: {e}")
            return JsonResponse({'error': 'Failed to save blog article'}, status=500)

        # return blog
        return JsonResponse({'content': blog_content})

    else:
        return JsonResponse({'error': 'Invalid Request'}, status=405)
def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)
    logging.debug(f"Downloaded audio file: {audio_file}")
    
    aai.settings.api_key = "your_assemblyai_api_key"
    transcriber = aai.Transcriber()
    
    try:
        # Upload the audio file to AssemblyAI
        upload_url = transcriber.upload(audio_file)
        logging.debug(f"Uploaded audio file URL: {upload_url}")

        # Transcribe the uploaded audio file
        transcript = transcriber.transcribe(upload_url)
        logging.debug(f"Transcription result: {transcript}")
        return transcript.text
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        raise
def generate_blog_from_transcription(transcription):
    generator = pipeline('text-generation', model='gpt-2')
    prompt = f"Generate a blog post based on the following transcription:\n\n{transcription}"
    blog_content = generator(prompt, max_length=1024, num_return_sequences=1)[0]['generated_text']
    return blog_content

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
    

 