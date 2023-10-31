from django.urls import path
from .views import ClasificadorTextViewSet,BotGeneradorPruebas,WebScraping,BotGeneradorPruebasOpenai


urlpatterns=[

    path("api/clasificador/",ClasificadorTextViewSet.as_view()),
    path("api/generar_pruebas/",BotGeneradorPruebas.as_view()),
    path("api/webscraping/",WebScraping.as_view()),
    path("api/generate_pdf/", BotGeneradorPruebasOpenai.as_view())

]