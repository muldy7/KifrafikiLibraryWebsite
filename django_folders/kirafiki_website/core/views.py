from django.shortcuts import render


# simple views for different parts of my core website like about and home
# honestly in this app I could add a model for like version number and basic app stuff like that for future use
# if something doesn't have a home it can go in core
# these guys are lower case since they are functions

def about_view(request):
    # can add more stuff here later if I want to
    context = {
        'project_name': 'Kirafiki Learning',
        'version_num': '0.1'
    }
    return render(request, 'core/about.html', context)

def home_view(request):

    context = {
        'project_name': 'Kirafiki Learning',
        'version_num': '0.1'
    }
    return render(request, 'core/home.html', context)
