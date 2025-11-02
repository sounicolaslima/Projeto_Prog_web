from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pagamentos, name='listar_pagamentos'),
    path('<int:pagamento_id>/visualizar/', views.visualizar_pagamento, name='visualizar_pagamento'),
    path('<int:pagamento_id>/pagar/', views.pagar_freelancer, name='pagar_freelancer'),
    path('<int:pagamento_id>/cancelar/', views.cancelar_pagamento, name='cancelar_pagamento'),
]