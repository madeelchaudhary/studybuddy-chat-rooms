from django.db import models

# Create your models here.


class Topic(models.Model):
    name = models.CharField(max_length=200, db_index=True)

    def __str__(self) -> str:
        return self.name
