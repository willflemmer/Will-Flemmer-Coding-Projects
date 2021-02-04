from django.db import models
from search.utils import unique_slug_generator
from django.db.models.signals import pre_save

# Create your models here.
class test(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=535, default='NO NAME')

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'search'
        indexes = [
            models.Index(fields=['title'], name='title_idx')
        ]


class Blog(models.Model):
    
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to = 'blog_images', default = 'default.png')
    subtitle = models.CharField(max_length=500)
    content = models.TextField(default = 'No content yet')
    
    slug = models.SlugField(max_length = 250, unique = True, blank = True)
    
    class Meta:
        app_label = 'search'
        
    def __str__(self):
        return self.title
    
    
class Video(models.Model):
    src = models.TextField(default = 'No Video Link')
    
    class Meta:
        app_label = 'search'
        
    def __str__(self):
        return self.src
    

def slug_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance, instance.title, instance.slug)


def title_id_list(title_list):
    id_list = [title.lower().replace(' ', '-') for title in title_list]
    comb_list = []
    for title, id_name in zip(title_list, id_list):
        comb_list.append([title, id_name])
        
    return comb_list


class Categories(models.Model):

    business_titles = ['Agriculture',
                       'Adhesives',
                       'Building Materials',
                       'Cleaning Supplies',
                       'Electrical Hardware and Supplies',
                       'Maintenance and Safety',
                       'Fuel and Energy',
                       'Healthcare',
                       'Tools',
                       'Office Supplies',
                       'Other']
    
    baby_titles = ['Baby Gear',
                     'Baby Safety and Health',
                     'Bathing and Grooming',
                     'Car Safety Seats',
                     'Carriers and Backpacks',
                     'Diapering',
                     'Feeding',
                     'Nursery Bedding',
                     'Nursery Furniture',
                     'Strollers and Accessories',
                     'Toys for Babys',
                     'Other Baby',
                     ]
    
    
    books = [
 'Accessories',
 'Audiobooks',
 'Catalogs',
 'Children & Young Adults',
 'Fiction & Literature',
 'Magazines',
 'Nonfiction',
 'Textbooks, Education & Reference',
 'Other Books']
    
    photography = [
 'Camera, Drone & Photo Accessories',
 'Digital Cameras',
 'Digital Photo Frames',
 'Film Photography',
 'Flashes & Flash Accessories',
 'Lenses & Filters',
 'Lighting & Studio',
 'Replacement Parts & Tools',
 'Video Production & Editing',
 'Other Cameras & Photo']
    
    phones =[
 'Cell Phones & Smartphones',
 'Smart Watches',
 'Smart Watch Accessories',
 'Cell Phone Accessories',
 'Phone Cards & SIM Cards',
 'Cell Phone & Smartphone Parts',
 'Vintage Cell Phones',
 'Mixed Lots']
    
    clothing = ['Women', 'Men', 'Kids', 'Baby']
    
    
    computers_tablets = [
 'Tablets & eBook Readers',
 'Laptops & Netbooks',
 'Desktops & All-In-Ones',
 'Laptop & Desktop Accessories',
 'Computer Cables & Connectors',
 'Computer Components & Parts',
 'Drives, Storage & Blank Media',
 'Home Networking & Connectivity',
 'Keyboards, Mice & Pointers',
 'Monitors, Projectors & Accs',
 'Printers, Scanners & Supplies',
 'Software',
 'Other Computers & Networking']
    
    
    personal_electronics = [
 'Surveillance & Smart Home Electronics',
 'Virtual Reality',
 'Portable Audio & Headphones',
 'TV, Video & Home Audio',
 'Vehicle Electronics & GPS',
 'Home Telephones & Accessories',
 'Multipurpose Batteries & Power',
 'Radio Communication',
 'Smart Glasses',
 'Other Consumer Electronics']
    
    health = [
 'Bath & Body',
 'Fragrances',
 'Hair Care & Styling',
 'Health Care',
 'Makeup',
 'Nail Care, Manicure & Pedicure',
 'Oral Care',
 'Salon & Spa Equipment',
 'Shaving & Hair Removal',
 'Skin Care',
 'E-Cigarettes, Vapes & Accs',
 'Other Health & Beauty']
    
    home = [
 'Bath',
 'Bedding',
 'Furniture',
 'Home Décor',
 'Home Improvement',
 'Household Supplies & Cleaning',
 'Kitchen Fixtures',
 'Lamps, Lighting & Ceiling Fans',
 'Major Appliances',
 'Rugs & Carpets',
 'Tools & Workshop Equipment',
 'Yard, Garden & Outdoor Living',
 'Other Home & Garden']
    
    jewellery = [
 'Engagement & Wedding',
 'Fashion Jewelry',
 'Fine Jewelry',
 'Handcrafted, Artisan Jewelry',
 'Jewelry Boxes & Organizers',
 'Loose Diamonds & Gemstones',
 "Men's Jewelry",
 'Vintage & Antique Jewelry',
 'Other Jewelry & Watches',
 'Watches, Parts & Accessories']
    
    musical_instrunments = [
 'Brass',
 'DJ Equipment',
 'Guitars & Basses',
 'Karaoke Entertainment',
 'Percussion',
 'Pianos, Keyboards & Organs',
 'String',
 'Wind & Woodwind',
 'Equipment',
 'Other Musical Instruments']
    
    pet_supplies = [
 'Bird Supplies',
 'Cat Supplies',
 'Dog Supplies',
 'Fish & Aquariums',
 'Reptile Supplies',
 'Small Animal Supplies',
 'Trackers',
 'Other Pet Supplies']
    
    sporting_goods = [
 'Boxing, Martial Arts & MMA',
 'Cycling',
 'Fishing',
 'Fitness, Running & Yoga',
 'Golf',
 'Hunting',
 'Indoor Games',
 'Outdoor Sports',
 'Water Sports',
 'Winter Sports',
 'Other Sporting Goods',]
    
    gaming = [
 'Video Games',
 'Video Game Consoles',
 'Video Game Accessories',
 'Replacement Parts & Tools',
 'Video Game Merchandise']
    
    hobbies = [
 'Building Toys',
 'Classic Toys',
 'Diecast & Toy Vehicles',
 'Electronic, Battery & Wind-Up',
 'Games',
 'Models & Kits',
 'Outdoor Toys & Structures',
 'Preschool Toys & Pretend Play',
 'Puzzles',
 'Stuffed Animals',
 'TV & Movie Character Toys',]
    
    
    
    class Meta:
        app_label = 'search'
        
        
    
class SubCategory(models.Model):
    title = models.CharField(max_length = 250, default = 'Empty')
    slug = models.SlugField(max_length = 250, unique = True, blank = True)
    parent_category = models.CharField(max_length = 250, default = 'Empty')
    #html_id = models.CharField(max_length = 250, default = 'Empty')
    mapping = models.CharField(max_length = 250, default = 'Empty')
    
    @property
    
    def html_id(self):
        return self.title.replace(' ', '-').lower()
    
    def nav_id(self):
        return self.html_id + '-nav'
        
    
    #nav_id = models.CharField(max_length = 250, default = nav_id)
        
    class Meta:
        app_label = 'search'
        
    def __str__(self):
        return self.title
        
pre_save.connect(slug_save, sender = Blog)




