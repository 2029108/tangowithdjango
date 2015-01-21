from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("<html><title>Greg Thomson - 2029108</title><body><p>Rango " +
                        "says hey there world! <a href= about/>about page</a><br>" +
                        "This tutorial has been put together by Greg Thomson, 2029108" +
                        "<p/></body></html>")

def about(request):
    return HttpResponse("<html><title>Greg Thomson - 2029108</title><body><p>Rango" +
                        " says here is the about page. <a href= http://127.0.0.1:8000/" +
                        "rango/ >index page</a><br>This tutorial has been put together" +
                        "by Greg Thomson, 2029108<p/></body></html>")
