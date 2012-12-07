from django.db import models
from django.db.models.query import QuerySet


class PlayerQuerySet(QuerySet):
    def matching_category(self, category):
        filters = {'gender': category.gender}
        if category.min_age is not None:
            filters["age__gte"] = category.min_age
        if category.max_age is not None:
            filters["age__lte"] = category.max_age

        return self.filter(**filters)


class PlayerManager(models.Manager):
    def get_query_set(self):
        return PlayerQuerySet(self.model)


class CategoryQuerySet(QuerySet):
    def matching_player(self, player):
        return self.filter(gender=player.gender)\
                   .exclude(min_age__gt=player.age)\
                   .exclude(max_age__lt=player.age)


class CategoryManager(models.Manager):
    def get_query_set(self):
        return CategoryQuerySet(self.model)
