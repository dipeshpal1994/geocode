from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy

from .forms import BookForm
from .models import Book

import pandas as pd
import requests
import json

class Home(TemplateView):
    template_name = 'home.html'


def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
        update_file(uploaded_file)
    return render(request, 'upload.html', context)


def update_file(f):
    df = pd.read_excel(f)

    for i, row in df.iterrows():
        print(i,row)
        apiAddress = str(df.at[i, 'street']) + ',' + str(df.at[i, 'zip']) + ',' + str(df.at[i, 'city']) + ',' + str(
            df.at[i, 'country'])

        parameters = {
            "key": "Mention your mapquest key here",
            "location": apiAddress
        }
        response = requests.get("http://www.mapquestapi.com/geocoding/v1/address", params=parameters)
        print(response)
        data = response.text
        dataJ = json.loads(data)['results']
        lat = (dataJ[0]['locations'][0]['latLng']['lat'])
        lng = (dataJ[0]['locations'][0]['latLng']['lng'])
        print(lat, lng)

        df.at[i, 'lat'] = lat
        df.at[i, 'lng'] = lng

    df.to_excel('media\modified.xlsx')




def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {
        'books': books
    })


def upload_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'upload_book.html', {
        'form': form
    })


def delete_book(request, pk):
    if request.method == 'POST':
        book = Book.objects.get(pk=pk)
        book.delete()
    return redirect('book_list')


class BookListView(ListView):
    model = Book
    template_name = 'class_book_list.html'
    context_object_name = 'books'


class UploadBookView(CreateView):
    model = Book
    form_class = BookForm
    success_url = reverse_lazy('class_book_list')
    template_name = 'upload_book.html'
