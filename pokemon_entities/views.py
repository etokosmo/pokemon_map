import json

import folium
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone

from .models import Pokemon, PokemonEntity

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    now = timezone.localtime()

    pokemons_entity = PokemonEntity.objects.filter(
        appeared_at__date__lte=now, disappeared_at__date__gte=now)

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemons_entity:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url)
        )

    pokemons_on_page = []
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': pokemon.image.url if pokemon.image else None,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def get_previous_evolution(request, pokemon: Pokemon):
    """Получаем описание покемона из кого эволюционировали"""
    if pokemon.previous_evolution:
        return {
            "title_ru": pokemon.previous_evolution.title,
            "pokemon_id": pokemon.previous_evolution.id,
            "img_url": request.build_absolute_uri(pokemon.previous_evolution.image.url)
        }


def get_next_evolution(request, requested_pokemon: Pokemon):
    """Получаем описание покемона в кого эволюционируем"""
    if not requested_pokemon.next_evolutions.all():
        return None
    pokemon = requested_pokemon.next_evolutions.all()[0]
    return {
        "title_ru": pokemon.title,
        "pokemon_id": pokemon.id,
        "img_url": request.build_absolute_uri(pokemon.image.url)
    }


def show_pokemon(request, pokemon_id):
    try:
        requested_pokemon = Pokemon.objects.get(id=int(pokemon_id))
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')
    
    pokemon = {
        "pokemon_id": requested_pokemon.id,
        "title_ru": requested_pokemon.title,
        "title_en": requested_pokemon.title_en,
        "title_jp": requested_pokemon.title_jp,
        "description": requested_pokemon.description,
        "img_url": request.build_absolute_uri(requested_pokemon.image.url),
        "entities": [
            {
                "level": 15,
                "lat": 55.753244,
                "lon": 37.628423
            },
            {
                "level": 24,
                "lat": 55.743244,
                "lon": 37.635423
            }
        ],
        "next_evolution": get_next_evolution(request, requested_pokemon),
        "previous_evolution": get_previous_evolution(request, requested_pokemon)
    }

    now = timezone.localtime()

    pokemons_entity = PokemonEntity.objects.filter(
        pokemon=requested_pokemon, appeared_at__date__lte=now, disappeared_at__date__gte=now)

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemons_entity:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url)
        )
        pokemon['entities'].append(
            {
                "level": pokemon_entity.level,
                "lat": pokemon_entity.lat,
                "lon": pokemon_entity.lon
            }
        )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon
    })
