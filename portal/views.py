from django.views import generic
from django.urls import reverse_lazy,reverse
from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import render,get_object_or_404
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
    fields = ['title','memo','important']
    template_name = "protal/todos/UpdateToDo.html"
    def get_object(self):
        todo = super(ToDoUpdateView, self).get_object()
        if todo.user != self.request.user:
            raise Http404
        return todo
    def get_success_url(self):
        pk = self.kwargs["pk"]
        slug = self.kwargs["slug"]
        messages.success(self.request,'Updated Successfully')
        return reverse("view_detailed_todo", kwargs={"slug":slug,"pk": pk})
class ToDoDeleteView(generic.DeleteView):
    model = ToDo
    slug_field = ToDo.slug
    fields = ['title','memo','important']
    template_name = "protal/todos/DeleteToDo.html"
    success_url = reverse_lazy("view_all_todos")
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
    return render(request,'portal/todos/viewtodos.html',{'todos':todos})
def tododetailview(request,pk,slug):
    todo = get_object_or_404(ToDo,user = request.user,id = pk,slug = slug)
    return render(request,'portal/todos/viewAtodo.html',{'todo':todo})
    
    