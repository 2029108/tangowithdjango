from django.shortcuts import render
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserProfileForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime
from rango.bing_search import run_query
from django.shortcuts import redirect
from django.template import RequestContext
from rango.forms import UserProfileForm


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list }

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response



def about(request):
    if request.session.get('visits'):
        context_dict = {'visits': request.session.get('visits')}
    else:
        count = 0

    return render(request, 'rango/about.html', context_dict)


def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html',)


@login_required
def add_category(request):

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()

                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat, 'cat_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)


def track_url(request):

    page_id = None
    url = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

def register_profile(request):

    if request.method == 'POST':
        # retrieve data and files from form
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            profile = form.save(commit = False)
            profile.user = request.user
            profile.save()
            return index(request)
        else:
            print form.errors
    else:
        form = UserProfileForm()

    return render(request, 'rango/profile_registration.html', {'form': form})

@login_required
def profile(request, username):
    context_dict = {}

    try:
        user = User.objects.get(username = username)
        #userProfile = UserProfile.objects.get(user = user.id)
        context_dict['username'] = user
        context_dict['email'] = user.email
        userprofile = UserProfile.objects.get(user = user.id)
        context_dict['website'] = userprofile.website
        context_dict['picture'] = userprofile.picture
        #context_dict['user'] = user
        #context_dict['userprofile'] = userprofile
    except UserProfile.DoesNotExist:
        redirect("/rango/add_profile/")
    except User.DoesNotExist:
        redirect("/rango/add_profile/")

    return render(request, 'rango/profile.html', context_dict)

def users(request):
    context_dict = {}
    users = zip(User.objects.all(), UserProfile.objects.all())
    context_dict['users'] = users
    return render(request, 'rango/users.html', context_dict)

@login_required
def profile_update(request):
    if request.method == 'POST':
        userProfileForm = UserProfileForm(request.POST, request.FILES)
        if userProfileForm.is_valid():
            userProfile = UserProfile.objects.get(user_id = request.user.id)
            userProfileData = userProfileForm.cleaned_data
            newWebsite = userProfileData['website']
            newPicture = userProfileData['picture']

            if len(newWebsite) > 0:
                userProfile.website = newWebsite
            if newPicture is not None:
                userProfile.picture = newPicture

            userProfile.save()
            url = '/rango/profile/'+ str(request.user)
            return HttpResponseRedirect(url)
    else:
         userProfileForm = UserProfileForm()

    return render(request,"rango/profile_update.html", {'userProfileForm': userProfileForm, 'username': request.user})