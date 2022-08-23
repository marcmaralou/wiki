from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from . import util
from django import forms
import markdown2
from random import randint


class searchForm(forms.Form):
    query = forms.CharField(max_length=100)

class createForm(forms.Form):
    title = forms.CharField(label="Add Title")
    body = forms.CharField(label="Add Body", widget=forms.Textarea(attrs={"rows":1, "cols":10}))

class editForm(forms.Form):
    title = forms.CharField(label="Edit Title")
    body = forms.CharField(label="Edit Body", widget=forms.Textarea(attrs={"rows":1, "cols":10}))

def index(request):
    form = searchForm()
    return render(request, "encyclopedia/index.html", {"entries":util.list_entries(), "form":form})

def entry(request, title):
    entry = util.get_entry(title)
    if entry is None:
        form = searchForm()
        message = "The requested page was not found."
        return render(request, "encyclopedia/error.html", {"form":form, "message":message})
    else:
        form = searchForm()
        entryMarkdown = util.get_entry(title)
        entryHTML = markdown2.markdown(entryMarkdown)
        return render(request, "encyclopedia/entry.html", {"title":title, "content":entryHTML, "form":form})

def search(request):
    if request.method == "POST":
        form = searchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get("query")
            present = False
            for entry in util.list_entries():
                if query == entry:
                    entryMarkdown = util.get_entry(query)
                    entryHTML = markdown2.markdown(entryMarkdown)
                    present = True
                    break
            if present:
                return render(request, "encyclopedia/entry.html", {"content":entryHTML, "form":form, "title":query})
            else:
                results = []
                for entry in util.list_entries():
                    if query in entry:
                        results.append(entry)
                if len(results) == 0:
                    form = searchForm()
                    message = "No such page exists."
                    return render(request, "encyclopedia/error.html", {"message":message, "form":form})
                else:
                    return render(request, "encyclopedia/index.html", {"entries":results, "form":form})
    else:
        form = searchForm()
        error = "Search for a page in order to see results."
        return render(request, "encyclopedia/error.html", {"error":error, "form":form})

def create(request):
    if request.method == "POST":
        createform = createForm(request.POST)
        if createform.is_valid():
            title = createform.cleaned_data.get("title")
            body = createform.cleaned_data.get("body")
            present = False
            for entry in util.list_entries():
                if title == entry:
                    present = True
                    break
            if present:
                message = "This page already exists."
                form = searchForm()
                return render(request, "encyclopedia/error.html", {"form":form, "message":message})
            else:
                util.save_entry(title, body)
                form = searchForm()
                entryMarkdown = util.get_entry(title)
                entryHTML = markdown2.markdown(entryMarkdown)
                return render(request, "encyclopedia/entry.html", {"title":title, "content":entryHTML, "form":form})
    else:
        form = searchForm()
        createform = createForm()
        return render(request, "encyclopedia/create.html", {"form":form, "createform":createform})

def edit(request, title):
    if request.method == "POST":
        editform = editForm(request.POST)
        if editform.is_valid():
            title = editform.cleaned_data.get("title")
            body = editform.cleaned_data.get("body")
            util.save_entry(title, body)
            form = searchForm()
            entryHTML = markdown2.markdown(body)
            return render(request, "encyclopedia/entry.html", {"title":title, "content":entryHTML, "form":form})
    else:
        form = searchForm()
        editform = editForm({"title":title, "body": util.get_entry(title)})
        return render(request, "encyclopedia/edit.html", {"form":form, "editform":editform})

def random(request):
    entries = util.list_entries()
    amount = len(entries)
    entry = randint(0, amount-1)
    title = entries[entry]
    entryMarkdown = util.get_entry(title)
    entryHTML = markdown2.markdown(entryMarkdown)
    form = searchForm()
    return render(request, "encyclopedia/entry.html", {"form":form, "content":entryHTML, "title":title})