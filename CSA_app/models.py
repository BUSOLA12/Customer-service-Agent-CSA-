from django.db import models
import random
import string
# Create your models here.

class Property(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image_urls = models.JSONField(blank=True, null=True)
    image = models.ImageField(upload_to='property_images/', default='property_images/default.jpg')
    property_identifier = models.CharField(max_length=255, unique=True, blank=True, editable=False)
    
    def generate_property_id(self):
        """Generate a custom property identifier (e.g., #12345)"""
        return f"{random.randint(10000, 99999)}"  # Generates a number like #12345

    def save(self, *args, **kwargs):
        """Override the save method to set a custom property identifier"""
        if not self.property_identifier:  # If the property identifier isn't already set
            self.property_identifier = self.generate_property_id()
        super(Property, self).save(*args, **kwargs)


    def __str__(self):
        return self.name
    
class Customer(models.Model):
    
    name = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    preferences = models.JSONField(null=True, blank=True, default=dict)
    
    def __str__(self):
        return self.phone_number or 'Unknown Customer'
    
class Interaction(models.Model):
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    Interaction_type = models.CharField(max_length=255)
    notes = models.TextField(null=True)

    def __str__(self):
        return f'{self.customer.name} - {self.property.name}'