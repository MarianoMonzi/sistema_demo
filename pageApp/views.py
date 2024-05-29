from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.sessions.models import Session
from django.db import IntegrityError, transaction
from .forms import ClienteForm, ListaCorrectivaForm, ListaPreventivaForm, TareaForm
from .models import Cliente, Tarea, ListaCorrectiva, ListaPreventiva, Planillas, PlanillaCliente, MensajeWhatsApp
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.forms.models import model_to_dict
from django.db.models import Q
import requests

def index(request):
    return render(request, 'index.html')

def loginlubricentro(request):

    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'login.html', {
                'form': AuthenticationForm,
                'error': 'Username or Password is incorrect'
            })
        else:
            login(request, user)
            return redirect('clientes')

@login_required
def signout(request):
    logout(request)
    return redirect('login')

def get_username(request):
    if request.user.is_authenticated:
        username = request.user.username
        return JsonResponse({'username': username})
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)

      
@login_required
def clientes(request):
    clientes_con_info = []

    # Obtener la fecha y hora actual

    # Obtener todos los clientes con sus próximas visitas
    for cliente in Cliente.objects.all():
        proxima_visita = 'No tiene proxima visita'
        # Obtener la próxima tarea del cliente
        proxima_tarea = Tarea.objects.filter(cliente=cliente.id, proxservicio__gte=timezone.now().date()).order_by('proxservicio').first()
        if proxima_tarea:
            proxima_visita = proxima_tarea.proxservicio
            clientes_con_info.append({
                'cliente': cliente,
                'proxima_visita': proxima_visita,
                'tiene_proxima_visita': True
            })
        else:
            
            clientes_con_info.append({
                'cliente': cliente,
                'proxima_visita': proxima_visita,
                'tiene_proxima_visita': False
            })

    clientes_con_info.sort(key=lambda x: (not x['tiene_proxima_visita'], x['proxima_visita']))

    return render(request, 'cliente.html', {'clientes': clientes_con_info})


def detalles_cliente(request):
    if request.method == 'GET' and 'cliente_id' in request.GET:
        cliente_id = request.GET['cliente_id']
        cliente = Cliente.objects.get(id=cliente_id)
        tareas = Tarea.objects.filter(cliente=cliente)

        tarea_proxima = tareas.filter(proxservicio__gte=timezone.now().date()).order_by('proxservicio').first()
        detalles_tareas = []

        # Agregar primero las tareas próximas y luego las pasadas a la lista de detalles de tareas
        if tarea_proxima:
            tipo_servicio = tarea_proxima.planilla.lista_tipo if tarea_proxima.planilla else ''

            detalle_tarea_proxima = {
                'id': tarea_proxima.id,
                'fecha': tarea_proxima.fecha,
                'servicio': tipo_servicio,
                'kilometros': tarea_proxima.kilometros,
                'proxservicio': tarea_proxima.proxservicio,
                'mecanico': tarea_proxima.mecanico.username if tarea_proxima.mecanico else ''
            }
            detalles_tareas.append(detalle_tarea_proxima)

        # Aquí puedes preparar los detalles del cliente para enviar de vuelta al frontend
        detalles_cliente = {
            'nombre': cliente.nombre,
            'patente': cliente.patente,
            'modelo': cliente.modelo,
            'numero': cliente.numero,
            'tarea_proxima': tarea_proxima.proxservicio if tarea_proxima else None  
            # Agrega más campos si los necesitas
        }
        return render(request, 'detalles_cliente.html', {'cliente': detalles_cliente})
    else:
        return JsonResponse({'error': 'ID de cliente no proporcionado'}, status=400)


def tareas_cliente(request):
    if request.method == 'GET' and 'cliente_id' in request.GET:
        cliente_id = request.GET['cliente_id']
        cliente = get_object_or_404(Cliente, id=cliente_id)
        
        # Obtener todas las tareas del cliente
        tareas = Tarea.objects.filter(cliente=cliente)

        # Obtener las tareas próximas a la fecha actual y ordenarlas por proxservicio ascendente
        tareas_proximas = tareas.filter(proxservicio__gte=timezone.now().date()).order_by('proxservicio')

        # Obtener las tareas pasadas y ordenarlas por proxservicio descendente
        tareas_pasadas = tareas.filter(proxservicio__lt=timezone.now().date()).order_by('-proxservicio')

        detalles_tareas = []

        # Agregar primero las tareas próximas y luego las pasadas a la lista de detalles de tareas
        for tarea in tareas_proximas:
            tipo_servicio = tarea.planilla.lista_tipo if tarea.planilla else ''

            detalle = {
                'id': tarea.id,
                'fecha': tarea.fecha,
                'servicio': tipo_servicio,
                'kilometros': tarea.kilometros,
                'proxservicio': tarea.proxservicio,
                'mecanico': tarea.mecanico.username if tarea.mecanico else ''
            }
            detalles_tareas.append(detalle)

        for tarea in tareas_pasadas:
            tipo_servicio = tarea.planilla.lista_tipo if tarea.planilla else ''

            detalle = {
                'id': tarea.id,
                'fecha': tarea.fecha,
                'servicio': tipo_servicio,
                'kilometros': tarea.kilometros,
                'proxservicio': tarea.proxservicio,
                'mecanico': tarea.mecanico.username if tarea.mecanico else ''
            }
            detalles_tareas.append(detalle)

        return JsonResponse({'tareas': detalles_tareas})
    else:
        return JsonResponse({'error': 'ID de cliente no proporcionado'}, status=400)
    
def obtener_primera_tarea(cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    tareas = Tarea.objects.filter(cliente=cliente)

    # Obtener la primera tarea próxima
    tarea_proxima = tareas.filter(proxservicio__gte=timezone.now().date()).order_by('fecha').first()

    return tarea_proxima, cliente.numero

def format_fecha(fecha):
    # Diccionario para mapear los nombres de los meses
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    # Extraer el día, mes y año de la fecha
    dia = fecha.day
    mes = meses[fecha.month]
    año = fecha.year

    # Formatear la fecha como "5 de Mayo de 2024"
    return f"{dia} {mes} {año}"

def buscar_cliente(request):
    query = request.GET.get('q')
    clientes_filtrados = []

    if query:
        query = query.replace(' ', '')

        # Filtrar clientes por patente ignorando espacios
        clientes_filtrados = Cliente.objects.filter(
            Q(patente__iregex=r'\s*'.join(query)) |
            Q(nombre__icontains=query) |
            Q(modelo__icontains=query)
        ).distinct()

        clientes_con_info_filtrados = []
        for cliente in clientes_filtrados:
            cliente_dict = model_to_dict(cliente)
            tareas = Tarea.objects.filter(cliente=cliente.id, proxservicio__gte=timezone.now().date()).order_by('proxservicio').first()
            ultima_visita = 'No tiene proxima visita'
            if tareas:
                ultima_visita = format_fecha(tareas.proxservicio)

            cliente_dict['ultima_visita'] = ultima_visita
            clientes_con_info_filtrados.append(cliente_dict)

    else:  # Si la consulta está vacía, devolver todos los clientes con última visita y ordenarlos por 'proxservicio'
        clientes = Cliente.objects.all()
        clientes_con_info_filtrados = []

        for cliente in clientes:
            cliente_dict = model_to_dict(cliente)
            cliente_dict['ultima_visita'] = 'No tiene proxima visita'  # Añadir la clave 'ultima_visita' con valor None por defecto

            tareas = Tarea.objects.filter(cliente=cliente.id, proxservicio__gte=timezone.now().date()).order_by('proxservicio').first()
            if tareas:
                cliente_dict['ultima_visita'] = format_fecha(tareas.proxservicio)

            clientes_con_info_filtrados.append(cliente_dict)

        # Ordenar clientes por 'proxservicio'
        clientes_con_info_filtrados.sort(key=lambda x: x['ultima_visita'] if x['ultima_visita'] != 'No tiene proxima visita' else '9999-12-31')

    return JsonResponse(clientes_con_info_filtrados, safe=False)

def guardar_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        numero = request.POST.get('numero')
        patente = request.POST.get('patente')
        vehiculo = request.POST.get('vehiculo')

        cliente_nuevo = Cliente(
            nombre=nombre, numero=numero, patente=patente, modelo=vehiculo)


        cliente_nuevo.save()
        return JsonResponse({'message': 'Cliente guardado correctamente', 'cliente_id': cliente_nuevo.pk})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def editar_cliente(request):
    if request.method == 'POST':
        cliente_id = request.GET.get('cliente_id')
        if cliente_id is None:
            return JsonResponse({'error': 'ID del cliente no proporcionado'}, status=400)

        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

        # Obtener los campos actualizados del cliente del cuerpo de la solicitud PATCH
        nombre = request.POST.get('nombre')
        numero = request.POST.get('numero')
        patente = request.POST.get('patente')
        modelo = request.POST.get('modelo')

        # Actualizar los campos del cliente solo si se proporcionaron nuevos valores
        if nombre:
            cliente.nombre = nombre
        if numero:
            cliente.numero = numero
        if patente:
            cliente.patente = patente
        if modelo:
            cliente.modelo = modelo

        cliente.save()  # Guardar los cambios en el cliente

        return JsonResponse({'message': 'Cliente actualizado correctamente'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def crear_planilla(cliente_id, selectServicio):
    cliente = Cliente.objects.get(id=cliente_id)
    planilla = None

    if selectServicio == 'Servicio Correctivo':
        planilla = Planillas(cliente=cliente, lista_tipo=selectServicio)
        try:
            planilla.save()
        except IntegrityError as e:
            # Manejar la excepción de clave única u otros errores de integridad
            print(f"Error al guardar la planilla correctiva: {e}")
    else:
        planilla = Planillas(cliente=cliente, lista_tipo=selectServicio)
        try:
            planilla.save()
        except IntegrityError as e:
            # Manejar la excepción de clave única u otros errores de integridad
            print(f"Error al guardar la planilla preventiva: {e}")

    return planilla

def guardar_tarea(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                cliente_id = request.POST['cliente_id']
                cliente = Cliente.objects.get(id=cliente_id)
                fecha = request.POST.get('fecha')
                proxservicio = request.POST.get('proxservicio')
                selectServicio = request.POST.get('servicio')
                mecanico_id = request.POST['mecanico']
                mecanico = User.objects.get(id=mecanico_id)
                kilometros = request.POST.get('kilometros')

                planilla = crear_planilla(cliente_id, selectServicio)

                if planilla:
                    tarea_nueva = Tarea(
                        cliente=cliente,
                        fecha=fecha,
                        planilla=planilla,
                        kilometros=kilometros,
                        proxservicio=proxservicio,
                        mecanico=mecanico
                    )
                    tarea_nueva.save()
                    print('Tarea guardada correctamente')
                    return JsonResponse({'message': 'Tarea guardada correctamente'})
                else:
                    print('Planilla no creada')
                    return JsonResponse({'message': 'Planilla no creada'}, status=500)
        except Cliente.DoesNotExist:
            print(f'Cliente con id {cliente_id} no existe')
            return JsonResponse({'error': 'Cliente no existe'}, status=404)
        except User.DoesNotExist:
            print(f'Mecánico con id {mecanico_id} no existe')
            return JsonResponse({'error': 'Mecánico no existe'}, status=404)
        except Exception as e:
            print(f'Error guardando la tarea: {e}')
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def eliminar_tarea_cliente(request):
    if request.method == 'DELETE' and 'tarea_cliente_id' in request.GET:
        tarea_cliente_id = request.GET['tarea_cliente_id']
        tarea = get_object_or_404(Tarea, id=tarea_cliente_id)
        tarea.delete()
        return JsonResponse({'success': 'Tarea del cliente eliminada correctamente'})
    else:
        return JsonResponse({'error': 'ID de tarea no proporcionado o método incorrecto'}, status=400)
    
def eliminar_cliente(request):
    if request.method == 'DELETE' and 'cliente_id' in request.GET:
        cliente_id = request.GET['cliente_id']
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.delete()
        return JsonResponse({'success': 'Cliente eliminado correctamente'})
    else:
        return JsonResponse({'error': 'ID de cliente no proporcionado o método incorrecto'}, status=400)





def planilla_correctiva(request):
    items = ListaCorrectiva.objects.all()
    print(items)  # Obtener todas las tareas guardadas
    if request.method == 'POST':
        form = ListaCorrectivaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('planilla_correctiva')
    else:
        form = ListaCorrectivaForm()
    return render(request, 'planillaCorrectiva.html', {'items': items})


def planilla_preventiva(request):
    items = ListaPreventiva.objects.all()  # Obtener todas las tareas guardadas
    if request.method == 'POST':
        form = ListaPreventivaForm(request.POST)
        if form.is_valid():
            print(form)
            form.save()
            # Puedes redirigir a una página de éxito
            return redirect('planilla_preventiva')
    else:
        form = ListaPreventivaForm()
    return render(request, 'planillaPreventiva.html', {'items': items})


def planilla_personal(request):
    if request.method == 'POST':
        tarea_id = request.POST.get('tarea_id')
        print(tarea_id)
        planilla_id = get_object_or_404(Planillas, id=tarea_id)
        

        # Obtener todos los items enviados en el formulario
        items_post = {k: v for k, v in request.POST.items() if k.startswith('item_')}

        for item_key, item_value in items_post.items():
            cambio = request.POST.get(f'cambio_{item_key.split("_")[-1]}', False)
            checkbox = request.POST.get(f'check_{item_key.split("_")[-1]}', False)
            observaciones = request.POST.get(f'observaciones_{item_key.split("_")[-1]}', '')

            # Verificar si hay PlanillaCliente existentes para este item y esta planilla
            planilla_clientes = PlanillaCliente.objects.filter(planillaId=planilla_id, nombre=item_value)

            if planilla_clientes.exists():
                # Si hay PlanillaCliente existentes, actualizar la primera encontrada
                planilla_cliente = planilla_clientes.first()
                planilla_cliente.cambio = cambio == 'on'
                planilla_cliente.checkbox = checkbox == 'on'
                planilla_cliente.observaciones = observaciones
                planilla_cliente.save()
            else:
                # Si no hay PlanillaCliente existentes, crear uno nuevo
                PlanillaCliente.objects.create(
                    planillaId=planilla_id,
                    nombre=item_value,
                    cambio=cambio == 'on',
                    checkbox=checkbox == 'on',
                    observaciones=observaciones
                )

        return redirect('clientes')
    else:
        cliente_id = request.GET.get('cliente_id')
        cliente = Cliente.objects.get(id=cliente_id)
        fechaTarea = request.GET.get('fecha')
        kmsTarea = request.GET.get('kms')
        tarea_id = request.GET.get('tarea_id')
        
        if PlanillaCliente.objects.filter(planillaId=tarea_id):
            items = PlanillaCliente.objects.filter(planillaId=tarea_id)
            return render(request, 'planilla.html', {'items': items, 'cliente': cliente, 'fecha': fechaTarea, 'kms': kmsTarea})
        else:
            selectServicio = request.GET.get('servicio')
            itemsCorrectivos = ListaCorrectiva.objects.all()
            itemsPreventivos = ListaPreventiva.objects.all()
            listaItems = []
            

            if selectServicio == 'Servicio Correctivo':
                for item in itemsCorrectivos:                    
                    listaItems.append(item)

                return render(request, 'planilla.html', {'items': listaItems, 'cliente': cliente, 'fecha': fechaTarea, 'kms': kmsTarea})
            else:
                for item in itemsPreventivos:
                    listaItems.append(item)

                return render(request, 'planilla.html', {'items': listaItems, 'cliente': cliente, 'fecha': fechaTarea, 'kms': kmsTarea})


def detalle_cliente_planilla(request):
    cliente_id = request.GET['cliente_id']
    cliente = Cliente.objects.get(id=cliente_id)
    # Aquí puedes preparar los detalles del cliente para enviar de vuelta al frontend
    detalles_cliente = {
        'nombre': cliente.nombre,
        'patente': cliente.patente,
        'modelo': cliente.modelo,
        'numero': cliente.numero,
        # Agrega más campos si los necesitas
    }
    return detalles_cliente


def eliminar_item_correctiva(request):
    if request.method == 'DELETE' and 'item_id' in request.GET:
        item_id = request.GET['item_id']
        item = get_object_or_404(ListaCorrectiva, id=item_id)
        item.delete()
        return JsonResponse({'success': 'Item eliminado correctamente'})
    else:
        return JsonResponse({'error': 'ID de item no proporcionado o método incorrecto'}, status=400)


def eliminar_item_preventiva(request):
    if request.method == 'DELETE' and 'item_id' in request.GET:
        item_id = request.GET['item_id']
        item = get_object_or_404(ListaPreventiva, id=item_id)
        item.delete()
        return JsonResponse({'success': 'Item eliminado correctamente'})
    else:
        return JsonResponse({'error': 'ID de item no proporcionado o método incorrecto'}, status=400)


def obtener_nombres_mecanicos(request):
    if request.method == 'GET':
        # Filtrar usuarios que sean mecánicos (puedes ajustar esto según tu lógica de identificación de mecánicos)
        mecanicos = User.objects.all()

        # Obtener los nombres de los mecánicos
        nombres_mecanicos = [
            {'id': mecanico.id, 'nombre': mecanico.username} for mecanico in mecanicos]

        return JsonResponse({'mecanicos': nombres_mecanicos})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def planilla(request):
    return render(request, 'planilla.html')


def enviar(request, telefono_envia, fecha_service, kilometros):
    # Token de acceso de Facebook
    token = 'EAALodXPhMJMBOzq4voUpdxdYjo651acMTTZCJzvtZCwTQGbjf7eC8PoWC1HUBYMo2VoftZA8U3Sbp55xJLw2C3fbu5GB32OhLBLdSvZC51isxhQHbNuhxXOqR2lSd64604kNRJCMzqG9Q6yyY7ZBLU8Ie4ctOSjDy8uxZCwV7GJ3GcPe8QhZCQYgq90nuU5DDy5'
    
    # Identificador de número de teléfono
    id_numero_telefono = ''
    
    
    # URL de la API de WhatsApp
    url = f"https://graph.facebook.com/v19.0/{id_numero_telefono}/messages"
    
    # Headers para la solicitud
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Cuerpo de la solicitud con template personalizado
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono_envia,
        "type": "template",
        "template": {
            "name": "appointment_reminder",  # Nombre del template personalizado
            "language": {
                "code": "en_US"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": fecha_service
                        },
                        {
                            "type": "text",
                            "text": kilometros
                        }
                    ]
                }
            ]
        }
    }
    
    # Realizar la solicitud POST
    response = requests.post(url, headers=headers, json=payload)
    
    # Verificar la respuesta
    if response.status_code == 200:
        return JsonResponse({'Mensaje': 'Enviado correctamente'}, status=200)
    else:
        return JsonResponse({'Mensaje': 'Error al enviar mensaje', 'Detalles': response.json()}, status=response.status_code)

def enviar_mensajes_pendientes(request):
    mensajes_pendientes = MensajeWhatsApp.objects.filter(
        enviar_mensaje=True,
        enviado=False
    )
    print(mensajes_pendientes)

    clientes_a_enviar = []

    for mensaje in mensajes_pendientes:
        try:
            print(f"Cliente ID: {mensaje.cliente_id}, Enviar mensaje: {mensaje.enviar_mensaje}, Fecha envío: {mensaje.fecha_envio}")          
            
            # Enviar el mensaje
            enviar_mensaje_whatsapp(request, mensaje.cliente_id, mensaje.tarea_id)
                # Marcar el mensaje como enviado
            mensaje.marcar_como_enviado()

                # Agregar a la lista de clientes a los que se les ha enviado el mensaje
            clientes_a_enviar.append({
                'cliente_id': mensaje.cliente_id,
                'fecha_envio': mensaje.fecha_envio,
                'mensaje_id': mensaje.pk
            })

        except Cliente.DoesNotExist:
            continue

    return JsonResponse({'clientes_a_enviar': clientes_a_enviar}) 

def enviar_mensaje_whatsapp(request, cliente_id, tarea_id):
    # Obtener la hora actual con la zona horaria correcta
    hora_actual = timezone.localtime().time()
    hora_límite = timezone.datetime.strptime("07:00", "%H:%M").time()

    # Verificar si la hora actual es mayor o igual a las 9 AM
    if hora_actual >= hora_límite:
        try:
            tarea = Tarea.objects.get(pk=tarea_id)
            telefono = tarea.cliente.numero  # Suponiendo que el cliente tiene un campo 'numero'
            fecha_service = tarea.fecha.strftime('%d/%m')  # Formato de fecha
            kilometros = tarea.kilometros
            return enviar(request, telefono, fecha_service, kilometros)
        except Tarea.DoesNotExist:
            # No hay tareas futuras, devolver una respuesta vacía o mensaje adecuado
            return JsonResponse({'Mensaje': 'No hay tareas futuras disponibles para el cliente'}, status=200)
    else:
        # Si la hora actual es menor a las 9 AM, devolver un mensaje adecuado
        return JsonResponse({'Mensaje': 'Los mensajes solo se pueden enviar después de las 9 AM'}, status=200)
    
def guardar_estado_toggle(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        enviar_mensaje = request.POST.get('enviar_mensaje') == 'true'  # Convertir a booleano

        # Obtener el cliente para asegurar que existe

        if Tarea.objects.filter(cliente=cliente_id).exists():
            if MensajeWhatsApp.objects.filter(cliente_id=cliente_id).exists():
                MensajeWhatsApp.objects.filter(cliente_id=cliente_id).update(enviar_mensaje=enviar_mensaje)
                return JsonResponse({'mensaje': 'Estado del toggle actualizado correctamente.'})
            else:
                MensajeWhatsApp.objects.update_or_create(
                cliente_id=cliente_id,
                defaults={'enviar_mensaje': enviar_mensaje}
                )
                return JsonResponse({'mensaje': 'Estado del toggle creado correctamente.'})
        else:
            return JsonResponse({'mensaje': 'Estado del toggle no guardado'})

           


    return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def obtener_estado_toggle(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    # Obtener el primer objeto que coincida o devolver None si no existe
    estado_obj = MensajeWhatsApp.objects.filter(cliente_id=cliente.pk).first()
    
    # Si no existe, devolver un valor predeterminado
    enviar_mensaje = estado_obj.enviar_mensaje if estado_obj else False

    return JsonResponse({'enviar_mensaje': enviar_mensaje}, status=200)


    
def comprobar_mensajes_pendientes(request):
    ahora = timezone.now().date()
    siete_dias_despues = ahora + timezone.timedelta(days=7)

    # Filtrar las tareas con proxservicio entre ahora y siete días después
    tareas_pendientes = Tarea.objects.filter(
        proxservicio__gte=ahora,
        proxservicio__lte=siete_dias_despues
    )

    print(tareas_pendientes)

    for tarea in tareas_pendientes:
        if not MensajeWhatsApp.objects.filter(cliente_id=tarea.cliente.pk, tarea_id=tarea.pk).exists():
            toggleSwitch = MensajeWhatsApp.objects.filter(cliente_id=tarea.cliente.pk, enviar_mensaje=True)
            if toggleSwitch:
                print(tarea)
                MensajeWhatsApp.objects.create(
                    cliente_id=tarea.cliente.pk,
                    tarea_id=tarea.pk,
                    fecha_envio=tarea.fecha,
                    enviado=False,
                    enviar_mensaje=True
                )
        

    return JsonResponse({'mensaje': 'Tareas pendientes guardadas correctamente.'})