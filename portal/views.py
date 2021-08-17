from django.views import generic
from django.utils import timezone
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import render,get_object_or_404,redirect
from . models import ToDo

# Create your views here.
#ToDo
class ToDoCreateView(generic.CreateView):
    model = ToDo
    fields = ['title','memo','important']
    template_name = "portal/todos/CreateToDo.html"
    success_url = reverse_lazy("view_all_todos")
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(ToDoCreateView, self).form_valid(form)
class ToDoUpdateView(generic.UpdateView):
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
#Function Based Views
def home(request):
    return render(request,'portal/home.html')
def todos(request):
    todos = ToDo.objects.filter(user = request.user)
    count = ToDo.objects.filter(user = request.user,is_completed = False).count()
    search_input = request.GET.get('search') or ''
    if search_input:
        todos = ToDo.objects.filter(user = request.user,title__contains = search_input)
    return render(request,'portal/todos/viewtodos.html',{'todos':todos,'count':count,'search_input':search_input})
def deletetodo(request,pk,slug):
    todo = get_object_or_404(ToDo,user = request.user,id = pk, slug = slug)
    if request.method == "POST":
        todo.delete()
        messages.success(request,"ToDo Deleted Sucessfully")
        return redirect('view_all_todos')
