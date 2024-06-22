from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView

# Create your views here.
from .models import *

from django.contrib.auth.mixins import LoginRequiredMixin




class CustomLoginView( LoginView):
    template_name= 'todo/login.html'
    fields= '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('tasks')



class RegisterPage(FormView):
    template_name = 'todo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)





from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView

class UserLogoutView(LogoutView):

    def get(self, request):
        logout(request)
        return redirect('login')


'''from django.contrib.auth import logout


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')'''


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context
    

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    fields= ['title','description']
    context_object_name = 'task'
    template_name = 'todo/task.html'



class TaskCreate(LoginRequiredMixin, CreateView):
    model= Task
    fields = ['title','description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model=Task
    fields= ['title','description', 'complete']
    success_url= reverse_lazy('tasks')

"""class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)
    """


def deleteTask(request, pk):
    item= Task.objects.get(id=pk)

    if request.method == 'POST':
        item.delete()
        return redirect('/')
    
    context={'item':item}
    return render(request, 'todo/delete.html', context)