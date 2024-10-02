from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index(request):
    # Si el usuario está autenticado, lo redirigimos al formulario de ingreso de ramos
    if request.user.is_authenticated:
        return redirect('ingresar_ramos')  # Redirige al formulario de ramos
    else:
        # Si no está autenticado, lo redirigimos al login
        return redirect('login')

from .models import Ramo, ActividadExtracurricular
@login_required
def ingresar_ramos(request):
    # Obtener los ramos y actividades del usuario actual
    ramos = Ramo.objects.filter(user=request.user)
    actividades = ActividadExtracurricular.objects.filter(user=request.user)

    return render(request, 'ingresar_ramos.html', {
        'ramos': ramos,
        'actividades': actividades,
    })

from django.shortcuts import render
from .models import Ramo, ActividadExtracurricular

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

from .models import Ramo, HorarioRamo, ActividadExtracurricular, HorarioActividad
from django.http import HttpResponse

from django.shortcuts import render, redirect
from .models import Ramo, HorarioRamo, ActividadExtracurricular, HorarioActividad

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

        return redirect('mostrar_prompt')  # Redirige a donde desees
    else:
        return HttpResponse("No se recibieron datos.")


from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm

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

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

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

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Ramo, ActividadExtracurricular

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
