from django.urls import path
from . import views

urlpatterns = [
    path("", views.listar_pagamentos, name="listar_pagamentos"),
    path("cadastrar/", views.cadastrar_pagamento, name="cadastrar_pagamento"),
]
