from django.db import models


class Pokemon(models.Model):
    """Покемон"""
    title = models.CharField(verbose_name='наименование', max_length=200)
    title_en = models.CharField(
        verbose_name='наименование на английском',
        max_length=200,
        blank=True
    )
    title_jp = models.CharField(
        verbose_name='наименование на японском',
        max_length=200,
        blank=True
    )
    description = models.TextField(verbose_name='описание', blank=True)
    image = models.ImageField(
        verbose_name='фотография',
        upload_to='pokemons',
        null=True,
        blank=True
    )
    previous_evolution = models.ForeignKey(
        'self',
        related_name='next_evolutions',
        verbose_name='предыдущая эволюция',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.title}'


class PokemonEntity(models.Model):
    """Характеристики Покемона"""
    pokemon = models.ForeignKey(
        Pokemon,
        verbose_name='покемон',
        on_delete=models.CASCADE
    )
    lat = models.FloatField(verbose_name='широта')
    lon = models.FloatField(verbose_name='долгота')
    appeared_at = models.DateTimeField(
        verbose_name='когда появился',
        null=True,
        blank=True
    )
    disappeared_at = models.DateTimeField(
        verbose_name='когда исчезнет',
        null=True,
        blank=True
    )
    level = models.IntegerField(verbose_name='уровень', null=True, blank=True)
    health = models.IntegerField(
        verbose_name='здоровье',
        null=True,
        blank=True
    )
    strength = models.IntegerField(verbose_name='сила', null=True, blank=True)
    defence = models.IntegerField(verbose_name='защита', null=True, blank=True)
    stamina = models.IntegerField(
        verbose_name='выносливость',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.pokemon.title}: {self.lat}, {self.lon}"
