from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.home.models import Artist
from main.settings.development import PROJECT_ROOT


@login_required
# @ensure_csrf_cookie
def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/profile/{0}'.format(request.user.artist.id))

@login_required
def profile(request,id):
    context={}
    try:
        artist=Artist.objects.get(id=id)
        try:
            projects=artist.project_set.all().order_by('-created')
        except:
            projects=None
        context['artist']=artist
        context['projects']=projects
    except:
        return Http404('Artist not found')
    return render(request,'home/index.html',context)


@api_view(['POST','PUT'])
def project_title_image(request,id,proj_id):
    if request.method == 'POST':
        project=request.user.artist.project_set.create(artist=request.user.artist)
        proj_id=project.id
        project.created=timezone.now()
    elif request.method =='PUT':
        project=request.user.artist.project_set.get(id=proj_id)
    else:
        return Http404('Can not access')
    image = request.FILES.get('image')
    path=PROJECT_ROOT+'/static/uploads/images/'
    ext =request.POST.get('ext')
    fullname = '{0}{1}_{2}_project_thumb.{3}'.format(path,id,proj_id,ext)
    handle_uploaded_file(fullname,image)
    url='/static/uploads/images/{0}_{1}_project_thumb.{2}'.format(id,proj_id,ext)
    project.thumbnail=url
    project.save()
    return Response({'id': request.user.artist.id, 'proj_id': proj_id, 'url': url})


@api_view(['POST','PUT'])
def project_update(request,id,proj_id):
    if request.method == 'POST':
        project=request.user.artist.project_set.create(artist=request.user.artist)
        proj_id=project.id
        project.created=timezone.now()
    elif request.method =='PUT':
        project=request.user.artist.project_set.get(id=proj_id)
    else:
        return Http404('Can not access')
    print request.data
    title=request.data.get('title',None)
    description=request.data.get('description',None)
    proj_type=request.data.get('type',None)
    project.title=title
    project.description=description
    project.type=proj_type
    project.save()
    return Response({'id': request.user.artist.id, 'proj_id': proj_id, 'title': project.title})


@api_view(['POST'])
def profile_image(request,id):
    if request.method == 'POST':
        image = request.FILES.get('image')
        path=PROJECT_ROOT+'/static/uploads/images/'
        ext =request.POST.get('ext')
        fullname = path+id+'_profile_pic.'+ext
        handle_uploaded_file(fullname,image)
        a=Artist.objects.get(user=id)
        a.profile_pic='/static/uploads/images/'+id+'_profile_pic.'+ext
        a.save()
        return Response({'id': request.user.artist.id, 'url': a.profile_pic})


@api_view(['POST'])
def profile_cover_image(request,id):
    if request.method == 'POST':
        image = request.FILES.get('image')
        path=PROJECT_ROOT+'/static/uploads/images/'
        ext =request.POST.get('ext')
        fullname = path+id+'_profile_cover_pic.'+ext
        handle_uploaded_file(fullname,image)
        artist=Artist.objects.get(user=id)
        artist.cover_pic='/static/uploads/images/'+id+'_profile_cover_pic.'+ext
        artist.save()
        return Response({'id': request.user.artist.id, 'url': artist.cover_pic})


@api_view(['POST'])
def update_user_info(request,id):
    about_me=request.data.get('about_me',None)
    name=request.data.get('name',None)
    name_list=name.rsplit(" ",1)
    artist=Artist.objects.get(user=id)
    artist.about_me=about_me
    artist.user.first_name=name_list[0]
    artist.user.last_name=name_list[1]
    artist.save()
    artist.user.save()
    return HttpResponse('updated')


def handle_uploaded_file(fullname,f):
    with open(fullname, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)