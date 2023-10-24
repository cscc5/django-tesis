#!/usr/bin/env bash
# exit on error
set -o errexit

# Aqui empieza
#!/bin/bash

# Activar el entorno virtual (asegúrate de que el entorno virtual esté activo)

# Dependencias problemáticas
problematic_dependency="paquete_a_validar"

# Verificar si la dependencia está instalada
if pip list | grep -q "$problematic_dependency"; then
    echo "El paquete $problematic_dependency está instalado en el entorno virtual."
    # Realizar verificaciones adicionales, si es necesario
else
    echo "El paquete $problematic_dependency no está instalado en el entorno virtual."
    # Tomar acciones adicionales, si es necesario (por ejemplo, omitir su uso)
    
    # Continuar el despliegue (suponiendo que no es crítico para el despliegue)
fi

# Resto del script de pre-despliegue

# Ejecutar el despliegue
#aqui termina

#poetry install
#pip3 install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate