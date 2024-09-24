from django.shortcuts import render
from django.http import HttpResponse

# Variables para almacenar los datos recibidos
ramos_guardados = []
actividades_guardadas = []

def index(request):
    return render(request, 'index.html')

def guardar_ramos_y_actividades(request):
    if request.method == 'POST':
        ramos_completos = []
        actividades_completas = []

        # Procesamos los ramos
        for index, ramo_nombre in enumerate(request.POST.getlist('ramos')):
            nombre_ramo = request.POST.get(f'ramos[{index}][nombre]')
            horarios = []

            # Procesamos los horarios del ramo (hasta 3 horarios)
            for i in range(3):
                dia = request.POST.get(f'ramos[{index}][horarios][{i}][dia]')
                hora_inicio = request.POST.get(f'ramos[{index}][horarios][{i}][inicio]')
                hora_termino = request.POST.get(f'ramos[{index}][horarios][{i}][termino]')

                # Verificamos que todos los campos de horario estén completos
                if dia and hora_inicio and hora_termino:
                    horarios.append({
                        'dia': dia,
                        'inicio': hora_inicio,
                        'termino': hora_termino
                    })

            ramos_completos.append({
                'nombre': nombre_ramo,
                'horarios': horarios,
            })

        # Procesamos las actividades extracurriculares
        for index, actividad_nombre in enumerate(request.POST.getlist('actividades')):
            nombre_actividad = request.POST.get(f'actividades[{index}][nombre]')
            tipo = request.POST.get(f'actividades[{index}][tipo]')

            # Si la actividad tiene horario fijo, procesamos los horarios
            if tipo == 'fijo':
                horarios = []
                for i in range(3):  # Permitir hasta 3 horarios fijos
                    dia = request.POST.get(f'actividades[{index}][horarios][{i}][dia]')
                    hora_inicio = request.POST.get(f'actividades[{index}][horarios][{i}][inicio]')
                    hora_termino = request.POST.get(f'actividades[{index}][horarios][{i}][termino]')

                    if dia and hora_inicio and hora_termino:
                        horarios.append({
                            'dia': dia,
                            'inicio': hora_inicio,
                            'termino': hora_termino,
                        })

                actividades_completas.append({
                    'nombre': nombre_actividad,
                    'tipo': 'fijo',
                    'horarios': horarios,
                })

            # Si la actividad tiene horas semanales
            elif tipo == 'semanal':
                horas_semanales = request.POST.get(f'actividades[{index}][horas_semanales]')
                actividades_completas.append({
                    'nombre': nombre_actividad,
                    'tipo': 'semanal',
                    'horas_semanales': horas_semanales,
                })

        # Guardamos la lista de ramos y actividades
        ramos_guardados.extend(ramos_completos)
        actividades_guardadas.extend(actividades_completas)

        # Imprimir en consola para verificar
        print("Ramos Guardados:", ramos_completos)
        print("Actividades Guardadas:", actividades_completas)

        # Retornar un mensaje de éxito
        return HttpResponse(f"Se guardaron {len(ramos_completos)} ramos y {len(actividades_completas)} actividades correctamente.")
    else:
        return HttpResponse("No se recibieron datos.")