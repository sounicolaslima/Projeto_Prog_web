from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pagamentos, name='listar_pagamentos'),
    path('cadastrar/', views.cadastrar_pagamento, name='cadastrar_pagamento'),
    path('<int:pagamento_id>/visualizar/', views.visualizar_pagamento, name='visualizar_pagamento'),
    path('<int:pagamento_id>/editar/', views.editar_pagamento, name='editar_pagamento'),
    path('<int:pagamento_id>/excluir/', views.excluir_pagamento, name='excluir_pagamento'),  # NOVA URL
]