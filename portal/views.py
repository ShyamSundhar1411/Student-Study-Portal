import os
import requests
import wikipediaapi
from io import BytesIO
from xhtml2pdf import pisa
from youtubesearchpython import VideosSearch
from django.conf import settings
from django.views import generic
from django.utils import timezone
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import Http404,HttpResponse,JsonResponse
from django.template.loader import get_template
from django.shortcuts import render,get_object_or_404,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from . models import ToDo,Note
from . tasks import send_requested_pdf, send_requested_pdf_on_delete
from . forms import SearchForm,UserForm,ProfileForm

# Create your views here.
#ToDo
class ToDoCreateView(LoginRequiredMixin,generic.CreateView):
    model = ToDo
    fields = ['title','memo','important']
    template_name = "portal/todos/CreateToDo.html"
    success_url = reverse_lazy("view_all_todos")
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(ToDoCreateView, self).form_valid(form)
class ToDoUpdateView(LoginRequiredMixin,generic.UpdateView):
    model = ToDo
    slug_field = ToDo.slug
    fields = ['title','memo','important','is_completed']
    template_name = "portal/todos/UpdateToDo.html"
    success_url = reverse_lazy('view_all_todos')
    def get_object(self):
        todo = super(ToDoUpdateView, self).get_object()
        if todo.user != self.request.user:
            raise Http404
        return todo
#Notes
class NoteCreateView(LoginRequiredMixin,generic.CreateView):
    model  = Note
    fields = ['title','subject','notes','important']
    template_name = "portal/notes/CreateNote.html"
    success_url = reverse_lazy("view_all_notes")
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(NoteCreateView,self).form_valid(form)
class NoteDetailView(LoginRequiredMixin,generic.DetailView):
    model = Note
    slug_field = Note.slug
    template_name = "portal/notes/NoteDetail.html"
class NoteUpdateView(LoginRequiredMixin,generic.UpdateView):
    model = Note
    slug_field = Note.slug
    fields = ['title','subject','notes','important']
    template_name = "portal/notes/UpdateNote.html"
    def get_object(self):
        note = super(NoteUpdateView,self).get_object()
        if note.user != self.request.user:
            raise Http404
        return note
    def get_success_url(self):
        pk = self.kwargs["pk"]
        slug = self.kwargs["slug"]
        messages.success(self.request,'Updated Successfully')
        return reverse("view_detailed_note", kwargs={"slug":slug,"pk": pk})
class NoteDeleteView(LoginRequiredMixin,generic.DeleteView):
    model = Note
    slug_field = Note.slug
    template_name = "portal/notes/DeleteNote.html"
    def get_object(self):
        note = super(NoteDeleteView,self).get_object()
        if note.user != self.request.user:
            raise Http404
        return note
    def get_success_url(self):
        note = super(NoteDeleteView,self).get_object()
        render_pdf_send_mail_on_delete(self.request,note.id)
        return reverse('view_all_notes')
#Function Based Views
def home(request):
    return render(request,'portal/home.html')
@login_required
def todos(request):
    todos = ToDo.objects.filter(user = request.user)
    count = ToDo.objects.filter(user = request.user,is_completed = False).count()
    search_input = request.GET.get('search') or ''
    if search_input:
        todos = ToDo.objects.filter(user = request.user,title__contains = search_input)
    return render(request,'portal/todos/viewtodos.html',{'todos':todos,'count':count,'search_input':search_input})
@login_required
def deletetodo(request,pk,slug):
    todo = get_object_or_404(ToDo,user = request.user,id = pk, slug = slug)
    if request.method == "POST":
        todo.delete()
        messages.success(request,"ToDo Deleted Sucessfully")
        return redirect('view_all_todos')
@login_required
def notes(request):
    note = Note.objects.filter(user = request.user).order_by('-updated_on')
    page = request.GET.get('page', 1)
    paginator = Paginator(note,3)
    note_count = paginator.count
    search_input = request.GET.get('search') or ''
    try:
        notes = paginator.page(page)
    except PageNotAnInteger :
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)
    if search_input:
        notes = Note.objects.filter(user = request.user,title__contains = search_input)
    return render(request,'portal/notes/viewnotes.html',{"Notes":notes,'note_count':note_count,'input':search_input})
@login_required
def render_to_pdf_and_download(request,pk,slug):
    template_path = "portal/notes/note.html"
    note = get_object_or_404(Note,pk = pk, user = request.user,slug = slug)
    context = {"Note":note}
    links    = lambda uri, rel: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    response = HttpResponse(content_type = "application/pdf")
    response['Content-Disposition'] = 'attachment; filename = {}.pdf'.format(note.title)
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(
        html,dest = response,link_callback = links)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>"+html+"</pre>")
    return response
@login_required
def render_to_pdf_and_send_mail(request,pk,slug):
    template_path = "portal/notes/note.html"
    note = get_object_or_404(Note,pk = pk, user = request.user,slug = slug)
    context = {"Note":note}
    template = get_template(template_path)
    html = template.render(context)
    links    = lambda uri, rel: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),result,link_callback = links)
    pdf = result.getvalue()
    filename = str(note.title)+'.pdf'
    send_requested_pdf(filename,pdf,request.user.id)
    messages.info(request,"The requested PDF has been sent to the registered email.")
    return redirect('view_detailed_note',note.id,note.slug)
@login_required
def render_pdf_send_mail_on_delete(request,pk):
    template_path = "portal/notes/note.html"
    note = get_object_or_404(Note,pk = pk, user = request.user)
    context = {"Note":note}
    template = get_template(template_path)
    html = template.render(context)
    links    = lambda uri, rel: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),result,link_callback = links)
    pdf = result.getvalue()
    filename = str(note.title)+'(BackUp).pdf'
    send_requested_pdf_on_delete(filename,pdf,request.user.id)
    messages.info(request,"Deletion Successful.A backup of this note has been sent to the registered email.")
def dictionary(request):
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        search_input = request.POST['search']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/"+search_input
        response = requests.get(url)
        answer = response.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form' : form,
                'phonetics' : phonetics,
                'audio' : audio,
                'definition': definition,
                'example': example,
                'synonyms':synonyms,
                'input': search_input,
            }
        except:
            context = {
                'form':form,
                'input':''
            }
        return render(request,'portal/dictionary.html',context)
    else:
        return render(request,'portal/dictionary.html',{'form':form})
def books(request):
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        search_input = request.POST['search']
        url = "https://www.googleapis.com/books/v1/volumes?q="+search_input
        response = requests.get(url)
        answer = response.json()
        result_list = []
        for i in range (10):
            if answer['items'][i]['volumeInfo'].get('imageLinks') == None:
                thumbail = ''
            else:
                thumbnail = answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail')
            result_dict = {
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail': thumbnail,
                'preview':answer['items'][i]['volumeInfo'].get('previewLink'),

            }
            result_list.append(result_dict)
        context = {
            'form':form,
            'results': result_list
        }
        return render(request,'portal/books.html',context)
    else:
        return render(request,'portal/books.html',{"form":form})
@xframe_options_exempt
def youtube(request):
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        search_input = request.POST['search']
        video = VideosSearch(search_input,limit = 10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'title': i['title'],
                'thumbnail':i['thumbnails'][0]['url'],
                'link': i['link'],
                'id':i['id']
            }
            result_list.append(result_dict)
        context = {
            'form':form,
            'results':result_list,
            'input':search_input,
        }
        return render(request,'portal/youtube.html',context)
    else:
        return render(request,'portal/youtube.html',{"form":form})
def wiki(request):
    form = SearchForm()
    if request.method == "POST":
        wiki_wiki = wikipediaapi.Wikipedia('en')
        form = SearchForm(request.POST)
        search_input = str(request.POST['search'])
        #try:
        search = wiki_wiki.page(search_input)
        try:
            context = {
                "form":form,
                "title":search.title,
                "link":search.fullurl,
                "details":search.summary,
            }
            return render(request,'portal/wiki.html',context)
        except :
            messages.error(request,'Make Sure you searched it correctly.This portal does not support case-sensitive searches!!')
            return render(request,'portal/wiki.html',{'form':form})
    else:
        return render(request,'portal/wiki.html',{"form":form})
@login_required
def profile(request,slug):
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance = request.user)
        profile_form = ProfileForm(request.POST,request.FILES,instance = request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Profile Updated Successfully')
            return redirect('profile',slug = request.user.profile.slug)
        else:
            return render(request, 'account/profile.html', {'user_form':user_form,'profile_form':profile_form,'user_form_errors':user_form.errors,'profile_form_errors':profile_form.errors})
    else:
        user_form = UserForm(instance = request.user)
        profile_form = ProfileForm(instance = request.user.profile)
        return render(request,'account/profile.html',{'user_form':user_form,'profile_form':profile_form})
