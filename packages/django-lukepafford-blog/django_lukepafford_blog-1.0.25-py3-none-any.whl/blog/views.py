from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Posts
from .forms import UploadPostForm
from .markdown_parser import parse_yaml_post
from .date_conversions import extract_date_from_title


# Create your views here.
class HomeView(TemplateView):
    template_name = "_base.html"


class PostList(ListView):
    model = Posts
    context_object_name = "posts"
    paginate_by = 10


class PostDetail(DetailView):
    model = Posts
    context_object_name = "post"


class PostUpload(LoginRequiredMixin, DetailView):
    def get(self, request):
        form = UploadPostForm
        return render(request, "blog/post_upload.html", {"form": form})

    def post(self, request):
        form = UploadPostForm(request.POST, request.FILES)
        if form.is_valid():
            parsed_data = parse_yaml_post(form.cleaned_data["file"])

            # Don't allow an upload if the name of the post doesn't have
            # the date in the beginning of the filename
            try:
                created_on = extract_date_from_title(request.FILES["file"].name)
            except ValueError as e:
                response = HttpResponse(e)
                response.status_code = 422
                return response

            # Overwrite existing post if title is the same
            try:
                post = Posts.objects.get(title=parsed_data["title"])
            except Posts.DoesNotExist:
                post = Posts()

            post.title = parsed_data["title"]
            post.body = parsed_data["body"]
            post.created_on = created_on
            post.author = request.user
            post.save()
        return redirect("posts_list")
