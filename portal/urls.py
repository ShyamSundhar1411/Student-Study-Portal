from django.urls import path,include
from . import views

urlpatterns = [
    #ToDos
    path('todos/',views.todos,name = "view_all_todos"),
    path('todo/create',views.ToDoCreateView.as_view(),name = "create_todo"),
    path('todo/<int:pk>/<slug:slug>/update',views.ToDoUpdateView.as_view(),name = "update_todo"),
    path("todo/<int:pk>/<slug:slug>/delete",views.deletetodo,name = "delete_todo"),
    #Notes
    path('notes/',views.notes,name = "view_all_notes"),
    path('note/create',views.NoteCreateView.as_view(),name = "create_note"),
    path('note/<int:pk>/<slug:slug>/update',views.NoteUpdateView.as_view(),name = "update_note"),
    path('note/<int:pk>/<slug:slug>/view',views.NoteDetailView.as_view(),name = "view_detailed_note"),
    path('note/<int:pk>/<slug:slug>/delete',views.NoteDeleteView.as_view(),name = "delete_note"),
    path('note/<int:pk>/render/to/pdf/<slug:slug>/download',views.render_to_pdf_and_download,name = "render_to_pdf_and_download"),
    path('note/<int:pk>/render/to/pdf/<slug:slug>/send/mail',views.render_to_pdf_and_send_mail,name = "render_to_pdf_and_mail"),
    #Dictionary
    path('dictionary/',views.dictionary,name = "dictionary"),
    path('books/',views.books,name = "books"),
]
