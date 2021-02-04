from django.shortcuts import render, redirect, get_object_or_404
from crispy_forms.layout import Layout
from django import forms
from .forms import SearchForm, FilterForm
from .ES import EngineConnector
from .models import Blog, Video, SubCategory


fields = ['price', 'description', 'url', 'title', '_', '_', 'src']
engine = EngineConnector('http://192.168.1.154', 'bsbc', 'search-rqvc1sc1nwny461eficicu1m', fields=fields)


class FacetContainer:

    def __init__(self, name, facets=[]):
        self.name = name
        self.facets = facets


class Facet:

    def __init__(self, name, checked=False):
        self.name = name
        self.checked = checked


class Result:

    def __init__(self, title, description, image='', price=0, site="Unknown", url="errorpage"):
        self.title = title
        self.description = description
        self.image = image
        self.price_f = price
        self.price = "£{:.2f}".format(price)
        self.merchant = site
        self.errors = 0
        self.url = url
        self.error_classes = ""
        self.stat = ''

        if self.stat == '':
            self.error_classes += " no_stat"

        if not self.image:
            self.errors += 1
            self.image ="https://static.bhphoto.com/images/images500x500/microsoft_vgy_00001_13_5_multi_touch_surface_laptop_1570039800_1506703.jpg"


def index(request):
    form = SearchForm()
    return render(request, 'search/index.html', {'form': form})


def search(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
        headers = request.GET

        if form.is_valid():
            query = form.cleaned_data['search_term']
            products = list()

            output_facets = []
            facets = engine.get_facets_for(query)
            for facet in facets:
                container = FacetContainer(facet['name'], facets=[])
                for v in facet['values']:
                    if headers['submit'] == 'filter':
                        if v[0] not in headers:
                            container.facets.append(Facet(v[0]))
                        else:
                            container.facets.append(Facet(v[0], checked=True))
                    else:
                        container.facets.append(Facet(v[0], checked=True))
                output_facets.append(container)
            print(output_facets[0].facets[0])
            results = engine.search(query, facets_list=output_facets)
            for row in results:
                row = Result(row['title'], row['description'], row['src'],
                             row['price'], 'NONE', row['url'])
                products.append(row)

            context = {
                'query': query,
                'products': products,
                'form': form,
                'facets': output_facets
            }
            print(len(products))
            if len(products) <= 5:
                return render(request, 'search/no_results.html', context)
            else:
                return render(request, 'search/results.html', context)

    return redirect('search:index')


def privacy_policy(request):
    return render(request, 'search/privacy-policy.html')

        
def blogs(request):
    blog_id = 1
    blog = get_object_or_404(Blog, pk=blog_id)
    
    blog_2_id = blog_id + 1
    blog_2 = get_object_or_404(Blog, pk=blog_2_id)
    
    video = get_object_or_404(Video, pk=1)
    
    blog_title_list = Blog.objects.all()
    
    #s = Blog.objects.get(title = '17 Ways to Save Money During Covid-19')
    #print(s)
    return render(request, 'search/blogs.html', context={'blog': blog,
                                                         'blog_2': blog_2,
                                                         'video': video,
                                                         'blog_title_list': blog_title_list})


def blog_detail(request, slug_text):
    blog = get_object_or_404(Blog, slug=slug_text)
    return render(request, 'search/blog_detail.html', {'blog': blog})


def categories(request):
    l1_cats = SubCategory.objects.all().filter(parent_category='Empty')
    all_cats = SubCategory.objects.all()
    
    l2_cats = []
    for cat in all_cats:
        if cat.parent_category != 'Empty':
            l2_cats.append(cat)
    
    business_cats = SubCategory.objects.all().filter(parent_category='business')
    baby_cats = SubCategory.objects.all().filter(parent_category='baby')
    computing_cats = SubCategory.objects.all().filter(parent_category='computing')
    books_cats = SubCategory.objects.all().filter(parent_category='books')
    hobbies_cats = SubCategory.objects.all().filter(parent_category='hobbies')
    phones_cats = SubCategory.objects.all().filter(parent_category='phones')
    home_cats = SubCategory.objects.all().filter(parent_category='home')
    sport_cats = SubCategory.objects.all().filter(parent_category='sport')
    photography_cats = SubCategory.objects.all().filter(parent_category='photography')
    music_cats = SubCategory.objects.all().filter(parent_category='musical_instruments')
    games_cats = SubCategory.objects.all().filter(parent_category='gaming')
    health_cats = SubCategory.objects.all().filter(parent_category='health')
    personal_electronics_cats = SubCategory.objects.all().filter(parent_category='personal_electronics')
    pet_cats = SubCategory.objects.all().filter(parent_category='pet')
    jewellery_cats = SubCategory.objects.all().filter(parent_category='jewellery')
    clothing_cats = SubCategory.objects.all().filter(parent_category='clothing')

    context = {'all_cats': all_cats,
               'l1_cats': l1_cats,
               'l2_cats': l2_cats,
               'business_cats': business_cats,
               'baby_cats': baby_cats,
               'computing_cats': computing_cats,
               'books_cats': books_cats,
               'hobbies_cats': hobbies_cats,
               'phones_cats': phones_cats,
               'home_cats': home_cats,
               'sport_cats': sport_cats,
               'photography_cats': photography_cats,
               'music_cats': music_cats,
               'games_cats': games_cats,
               'health_cats': health_cats,
               'personal_electronics_cats': personal_electronics_cats,
               'pet_cats': pet_cats,
               'jewellery_cats': jewellery_cats,
               'clothing_cats': clothing_cats
                }
    
    return render(request, 'search/categories.html', context=context)


def categories_results(request, slug_text):
    category = get_object_or_404(SubCategory, slug=slug_text)
    ebay_cat = category.mapping
    # for ES
    query = ebay_cat
    
    parent_mapping = {'business': 'Business',
                      'baby': 'Baby and Childcare',
                      'computing': 'Computing and Networks',
                      'books': 'Books',
                      'hobbies': 'Hobbies',
                      'phones': 'Mobile Phones and Accessories',
                      'home': 'Home',
                      'sport': 'Sporting Products',
                      'photography': 'Photography',
                      'musical_instruments': 'Musical Instruments',
                      'gaming': 'Games and Consoles',
                      'health': 'Health and Beauty',
                      'personal_electronics': 'Personal Electronics',
                      'pet': 'Pet Supplies',
                      'jewellery': 'Jewellery',
                      'clothing': 'Clothing and Accesories'}
    
    parent_cat = parent_mapping[category.parent_category]
    sub_cat = category.title
    products = list()
    for row in es.basic_search('sub_category', query):
        print(row)
        row = Result(row['id'], row['title'], row['src'], row['price'], row['website'],
                     row['url'], row['_score'], row['sub_category_prob'])
        products.append(row)

    products = sorted(products, key=lambda x: x.sub_prob, reverse=True)
    form = SearchForm()
    filter_form = FilterForm()
    
    context = {'category': category, 'parent_cat': parent_cat, 'sub_cat': sub_cat,
               'products': products, 'form': form, 'filter': filter_form,
               'query': query}
    
    return render(request, 'search/categories_results.html', context=context)
