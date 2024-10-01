from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index(request):
    # Si el usuario está autenticado, lo redirigimos al formulario de ingreso de ramos
    if request.user.is_authenticated:
        return redirect('ingresar_ramos')  # Redirige al formulario de ramos
    else:
        # Si no está autenticado, lo redirigimos al login
        return redirect('login')

# Vista protegida para ingresar ramos
@login_required  # Este decorador asegura que solo usuarios autenticados puedan acceder
def ingresar_ramos(request):
    # Aquí va la lógica de tu formulario de ingreso de ramos
    return render(request, 'ingresar_ramos.html')  # Página para ingresar ramos

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

def guardar_ramos_y_actividades(request):
    if request.method == 'POST':
        ramos_completos = []
        actividades_completas = []

        # Procesamos los ramos
        ramo_index = 0
        while f'ramos_{ramo_index}_nombre' in request.POST:
            nombre_ramo = request.POST.get(f'ramos_{ramo_index}_nombre')
            dificultad_ramo = request.POST.get(f'ramos_{ramo_index}_dificultad')
            horarios = []

            # Procesamos los horarios del ramo (hasta 3 horarios)
            horario_index = 0
            while f'ramos_{ramo_index}_horarios_{horario_index}_dia' in request.POST:
                dia = request.POST.get(f'ramos_{ramo_index}_horarios_{horario_index}_dia')
                hora_inicio = request.POST.get(f'ramos_{ramo_index}_horarios_{horario_index}_inicio')
                hora_termino = request.POST.get(f'ramos_{ramo_index}_horarios_{horario_index}_termino')

                if dia and hora_inicio and hora_termino:
                    horarios.append({
                        'dia': dia,
                        'inicio': hora_inicio,
                        'termino': hora_termino,
                    })
                horario_index += 1

            ramos_completos.append({
                'nombre': nombre_ramo,
                'dificultad': dificultad_ramo,
                'horarios': horarios,
            })
            ramo_index += 1

        # Procesamos las actividades extracurriculares
        actividad_index = 0
        while f'actividades_{actividad_index}_nombre' in request.POST:
            nombre_actividad = request.POST.get(f'actividades_{actividad_index}_nombre')
            tipo = request.POST.get(f'actividades_{actividad_index}_tipo')

            if tipo == 'fijo':
                horarios = []
                horario_index = 0
                while f'actividades_{actividad_index}_horarios_{horario_index}_dia' in request.POST:
                    dia = request.POST.get(f'actividades_{actividad_index}_horarios_{horario_index}_dia')
                    hora_inicio = request.POST.get(f'actividades_{actividad_index}_horarios_{horario_index}_inicio')
                    hora_termino = request.POST.get(f'actividades_{actividad_index}_horarios_{horario_index}_termino')

                    if dia and hora_inicio and hora_termino:
                        horarios.append({
                            'dia': dia,
                            'inicio': hora_inicio,
                            'termino': hora_termino,
                        })
                    horario_index += 1

                actividades_completas.append({
                    'nombre': nombre_actividad,
                    'tipo': 'fijo',
                    'horarios': horarios,
                })

            elif tipo == 'semanal':
                horas_semanales = request.POST.get(f'actividades_{actividad_index}_horas_semanales')
                actividades_completas.append({
                    'nombre': nombre_actividad,
                    'tipo': 'semanal',
                    'horas_semanales': horas_semanales,
                })

            actividad_index += 1

        # Guardar los datos en la sesión
        request.session['ramos'] = ramos_completos
        request.session['actividades'] = actividades_completas

        # Generamos el prompt
        prompt = generar_prompt(ramos_completos, actividades_completas)

        # Mostramos el prompt en la pantalla
        return render(request, 'mostrar_prompt.html', {'prompt': prompt})

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
