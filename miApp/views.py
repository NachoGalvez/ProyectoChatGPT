from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ramo, HorarioRamo, ActividadExtracurricular, HorarioActividad
from django.http import HttpResponse
from .forms import RegistroForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

def index(request):
    # Si el usuario está autenticado, lo redirigimos al formulario de ingreso de ramos
    if request.user.is_authenticated:
        return redirect('ingresar_ramos')  # Redirige al formulario de ramos
    else:
        # Si no está autenticado, lo redirigimos al login
        return redirect('login')

@login_required
def ingresar_ramos(request):
    # Obtener los ramos y actividades del usuario actual
    ramos = Ramo.objects.filter(user=request.user)
    actividades = ActividadExtracurricular.objects.filter(user=request.user)

    return render(request, 'ingresar_ramos.html', {
        'ramos': ramos,
        'actividades': actividades,
    })

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


def generar_prompt(ramos, actividades):
    """
    Función para generar un prompt en lenguaje natural basado en los ramos
    y actividades ingresados por el usuario.
    """
    prompt = "Por favor, genera el mejor horario posible para los siguientes ramos y actividades:\n\n"

    # Añadir los ramos al prompt
    prompt += "Ramos:\n"
    for ramo in ramos:
        prompt += f"- {ramo['nombre']} (Dificultad: {ramo['dificultad']}/10) con los siguientes horarios:\n"
        for horario in ramo['horarios']:
            prompt += f"  Día: {horario['dia']}, de {horario['inicio']} a {horario['termino']}\n"

    # Añadir las actividades extracurriculares al prompt
    prompt += "\nActividades Extracurriculares:\n"
    for actividad in actividades:
        if actividad['tipo'] == 'fijo':
            prompt += f"- {actividad['nombre']} con horarios fijos:\n"
            for horario in actividad['horarios']:
                prompt += f"  Día: {horario['dia']}, de {horario['inicio']} a {horario['termino']}\n"
        elif actividad['tipo'] == 'semanal':
            prompt += f"- {actividad['nombre']} requiere {actividad['horas_semanales']} horas semanales (sin horario fijo).\n"

    prompt += "\nPor favor, optimiza estos horarios de manera que no haya conflictos."

    return prompt


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

def cerrar_sesion(request):
    logout(request)
    return redirect('index')


@login_required
def eliminar_ramo(request, ramo_id):
    # Obtener el ramo y asegurarse de que pertenece al usuario
    ramo = get_object_or_404(Ramo, id=ramo_id, user=request.user)
    ramo.delete()
    messages.success(request, f'El ramo "{ramo.nombre}" ha sido eliminado.')
    return redirect('mostrar_ramos')  # Redirigir a la vista que muestra los ramos y actividades

@login_required
def eliminar_actividad(request, actividad_id):
    # Obtener la actividad y asegurarse de que pertenece al usuario
    actividad = get_object_or_404(ActividadExtracurricular, id=actividad_id, user=request.user)
    actividad.delete()
    messages.success(request, f'La actividad "{actividad.nombre}" ha sido eliminada.')
    return redirect('mostrar_ramos')  # Redirigir a la vista que muestra los ramos y actividades

from django.shortcuts import render, redirect
from .forms import PreferenciaForm
from .models import Preferencia

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
