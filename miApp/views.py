from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ramo, HorarioRamo, ActividadExtracurricular, HorarioActividad, Calendario, Preferencia
from django.http import HttpResponse
from .forms import RegistroForm, PreferenciaForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from openai import OpenAI

#Vista predeterminada
def index(request):
    # Si el usuario está autenticado, lo redirigimos al formulario de ingreso de ramos
    if request.user.is_authenticated:
        return redirect('ingresar_ramos')  # Redirige al formulario de ramos
    else:
        # Si no está autenticado, lo redirigimos al login
        return redirect('login')

#Formulario para ingresar ramos y actividades
@login_required
def ingresar_ramos(request):
    # Obtener los ramos y actividades del usuario actual
    ramos = Ramo.objects.filter(user=request.user)
    actividades = ActividadExtracurricular.objects.filter(user=request.user)

    return render(request, 'ingresar_ramos.html', {
        'ramos': ramos,
        'actividades': actividades,
    })

#Ver y eliminar ramos y actividades
@login_required
def mostrar_ramos(request):
    # Obtener los ramos del usuario actual
    ramos = Ramo.objects.filter(user=request.user).prefetch_related('horarios')
    
    # Obtener las actividades del usuario actual
    actividades = ActividadExtracurricular.objects.filter(user=request.user).prefetch_related('horarios')

    # Pasar los datos al template
    return render(request, 'mostrar_ramos.html', {
        'ramos': ramos,
        'actividades': actividades,
    })

#Función que permite asignar los ramos y actividades al usuario
@login_required
def guardar_ramos_y_actividades(request):
    if request.method == 'POST':
        # Procesamos los ramos
        ramo_index = 0
        while f'ramos_{ramo_index}_nombre' in request.POST:
            nombre_ramo = request.POST.get(f'ramos_{ramo_index}_nombre')
            dificultad_ramo = request.POST.get(f'ramos_{ramo_index}_dificultad')
            ramo = Ramo.objects.create(nombre=nombre_ramo, dificultad=dificultad_ramo, user=request.user)

            horario_index = 0
            while f'ramos_{ramo_index}_horarios_{horario_index}_dia' in request.POST:
                dia = request.POST.get(f'ramos_{ramo_index}_horarios_{horario_index}_dia')
                hora_inicio = request.POST.get(f'ramos_{ramo_index}_horarios_{horario_index}_inicio')
                hora_termino = request.POST.get(f'ramos_{ramo_index}_horarios_{horario_index}_termino')

                # Solo creamos el horario si tanto la hora de inicio como la hora de término están presentes
                if hora_inicio and hora_termino:
                    HorarioRamo.objects.create(
                        ramo=ramo,
                        dia=dia,
                        hora_inicio=hora_inicio,
                        hora_termino=hora_termino
                    )
                horario_index += 1

            ramo_index += 1

        # Procesamos las actividades extracurriculares
        actividad_index = 0
        while f'actividades_{actividad_index}_nombre' in request.POST:
            nombre_actividad = request.POST.get(f'actividades_{actividad_index}_nombre')
            tipo = request.POST.get(f'actividades_{actividad_index}_tipo')
            actividad = ActividadExtracurricular.objects.create(nombre=nombre_actividad, tipo=tipo, user=request.user)

            if tipo == 'fijo':
                horario_index = 0
                while f'actividades_{actividad_index}_horarios_{horario_index}_dia' in request.POST:
                    dia = request.POST.get(f'actividades_{actividad_index}_horarios_{horario_index}_dia')
                    hora_inicio = request.POST.get(f'actividades_{actividad_index}_horarios_{horario_index}_inicio')
                    hora_termino = request.POST.get(f'actividades_{actividad_index}_horarios_{horario_index}_termino')

                    # Solo creamos el horario si tanto la hora de inicio como la hora de término están presentes
                    if hora_inicio and hora_termino:
                        HorarioActividad.objects.create(
                            actividad=actividad,
                            dia=dia,
                            hora_inicio=hora_inicio,
                            hora_termino=hora_termino
                        )
                    horario_index += 1

            elif tipo == 'semanal':
                horas_semanales = request.POST.get(f'actividades_{actividad_index}_horas_semanales')
                actividad.horas_semanales = horas_semanales
                actividad.save()

            actividad_index += 1

        return redirect('mostrar_ramos')  # Redirige a donde desees
    else:
        return HttpResponse("No se recibieron datos.")

#Maneja el registro de un usuario
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')  # Redirige a la página principal o donde desees
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

#Maneja el log in
def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Usamos 'username' ya que es el campo del formulario
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

#Maneja el cierre de sesion
def cerrar_sesion(request):
    logout(request)
    return redirect('index')

#Función para eliminar un ramo
@login_required
def eliminar_ramo(request, ramo_id):
    # Obtener el ramo y asegurarse de que pertenece al usuario
    ramo = get_object_or_404(Ramo, id=ramo_id, user=request.user)
    ramo.delete()
    messages.success(request, f'El ramo "{ramo.nombre}" ha sido eliminado.')
    return redirect('mostrar_ramos')  # Redirigir a la vista que muestra los ramos y actividades

#Función para eliminar una actividad
@login_required
def eliminar_actividad(request, actividad_id):
    # Obtener la actividad y asegurarse de que pertenece al usuario
    actividad = get_object_or_404(ActividadExtracurricular, id=actividad_id, user=request.user)
    actividad.delete()
    messages.success(request, f'La actividad "{actividad.nombre}" ha sido eliminada.')
    return redirect('mostrar_ramos')  # Redirigir a la vista que muestra los ramos y actividades

#Maneja el ingreso de preferencias
@login_required
def preferencias(request):
    # Obtén las preferencias del usuario o crea una nueva si no existen
    preferencia, created = Preferencia.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = PreferenciaForm(request.POST, instance=preferencia)

        # Obtener las preferencias personalizadas nuevas del formulario
        nuevas_preferencias = []
        for key, value in request.POST.items():
            if key.startswith('nueva_preferencia_') and value.strip():
                nuevas_preferencias.append(value.strip())
        
        if form.is_valid():
            # Guardar el resto de los campos del formulario
            preferencia = form.save(commit=False)

            # Combinar las preferencias personalizadas existentes con las nuevas
            if preferencia.preferencias_personalizadas:
                # Si ya hay preferencias personalizadas, añádelas a las nuevas
                preferencias_existentes = preferencia.preferencias_personalizadas.splitlines()
                nuevas_preferencias = preferencias_existentes + nuevas_preferencias
            
            # Guardar todas las preferencias personalizadas como una cadena separada por saltos de línea
            preferencia.preferencias_personalizadas = "\n".join(nuevas_preferencias)
            preferencia.save()

            return redirect('preferencias')

    else:
        # Precargar el formulario con los datos existentes
        form = PreferenciaForm(instance=preferencia)
    
    # Dividir las preferencias personalizadas en líneas para mostrarlas
    preferencias_personalizadas = preferencia.preferencias_personalizadas.splitlines() if preferencia.preferencias_personalizadas else []

    return render(request, 'preferencias.html', {
        'form': form,
        'preferencias_personalizadas': preferencias_personalizadas
    })

#Maneja la eliminación de una preferencia
@login_required
def eliminar_preferencia(request, pref):
    preferencia = Preferencia.objects.get(usuario=request.user)
    
    # Filtrar las preferencias para eliminar la que coincide
    preferencias = preferencia.preferencias_personalizadas.splitlines()
    if pref in preferencias:
        preferencias.remove(pref)
        # Guardar las preferencias actualizadas
        preferencia.preferencias_personalizadas = "\n".join(preferencias)
        preferencia.save()

    return redirect('preferencias')

#Maneja la generación de un calendario
@login_required
def pagina_generar_calendario(request):
    user = request.user
    
    # Obtener el último calendario generado por el usuario
    ultimo_calendario = Calendario.objects.filter(usuario=user).order_by('-creado_en').first()

    if request.method == "POST":
        # Obtener ramos y actividades del usuario
        ramos = Ramo.objects.filter(user=user)
        actividades = ActividadExtracurricular.objects.filter(user=user)
        
        # Obtener las preferencias del usuario
        preferencias = Preferencia.objects.get(usuario=user)

        # Formatear los datos para enviarlos a la API
        ramos_info = [{"nombre": ramo.nombre, "dificultad": ramo.dificultad, 
                       "horarios": [{"dia": h.dia, "inicio": h.hora_inicio, "termino": h.hora_termino} for h in ramo.horarios.all()]}
                      for ramo in ramos]

        actividades_info = [{"nombre": actividad.nombre, "tipo": actividad.tipo,
                             "horarios": [{"dia": h.dia, "inicio": h.hora_inicio, "termino": h.hora_termino} for h in actividad.horarios.all()]}
                            if actividad.tipo == "fijo" else {"nombre": actividad.nombre, "horas_semanales": actividad.horas_semanales}
                            for actividad in actividades]

        # Agregar preferencias
        preferencias_info = {
            "horario_estudio": preferencias.horario_estudio, 
            "tiempo_de_viaje_desde_casa_a_la_universidad_minutos": preferencias.tiempo_llegada_uni,
            "tiempo_de_viaje_desde_universidad_a_la_casa_minutos": preferencias.tiempo_llegada_uni,
            "tiempo_preparacion_despues_de_despertar": preferencias.tiempo_preparacion,
            "tiempo_libre_antes_dormir": preferencias.tiempo_antes_dormir
        }

        # Crear el prompt para enviar a la API
        prompt = f"Genera un calendario semanal para un estudiante con los siguientes ramos: {ramos_info} y actividades: {actividades_info}. Quiero que hagas un horario hora por hora de toda la semana, considerando a qué hora debo levantarme, a qué hora debería estudiar (y qué ramo estudiar) y en qué horario hacer otras actividades o estar libre. Quiero que tengas en cuenta la dificultad de cada ramo, entre más difícil, más tiempo de estudio necesita. Además, considera que una persona debe dormir entre 6 y 8 horas. Quiero que al final dejes un consejo para poder conseguir llevar a cabo ese horario propuesto."
        
        # Leer la clave de API desde un archivo de texto
        with open('apikey.txt', 'r') as file:
            openai_api_key = file.read().strip()

        # Crear el cliente para la API de OpenAI
        client = OpenAI(api_key=openai_api_key)

        try:
            # Realizar la solicitud a OpenAI usando el modelo
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Usa gpt-4 si tienes acceso
                messages=[
                    {"role": "system", "content": f"Eres un asistente que genera calendarios personalizados muy detallista. Debes tener en cuenta estas preferencias del estudiante: {preferencias_info}. Siempre considera los viajes, cuanto me demoro desde la casa a la universidad y desde la universidad a la casa."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=15000,
                temperature=0.6,
            )

            # Acceder correctamente al contenido generado
            calendario_generado = response.choices[0].message.content.strip()
            
            # Guardar el nuevo calendario en la base de datos
            nuevo_calendario = Calendario.objects.create(usuario=user, contenido=calendario_generado)
            ultimo_calendario = nuevo_calendario  # Actualizar el último calendario

        except Exception as e:
            calendario_generado = f"Error al generar el calendario: {str(e)}"

    # Renderizar la página con el último calendario, si existe
    return render(request, 'generar_calendario.html', {'ultimo_calendario': ultimo_calendario})


