from django.urls import path,include
from . import views

urlpatterns = [
    #ToDos
    path('todo/',views.todos,name = "view_all_todos"),
    path('todo/create',views.ToDoCreateView.as_view(),name = "create_todo"),
    path('todo/<int:pk>/<slug:slug>/view',views.tododetailview,name = "view_detailed_todo"),
    path('todo/<int:pk>/<slug:slug>/update',views.ToDoUpdateView.as_view(),name = "update_todo"),
    path("todo/<int:pk>/<slug:slug>/delete",views.ToDoDeleteView.as_view(),name = "delete_todo")
    #Notes
    #HomeWorks
]
