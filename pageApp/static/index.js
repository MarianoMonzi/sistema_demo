document.addEventListener('DOMContentLoaded', function () {
    const abrir = document.getElementById('open');
    const cerrar = document.getElementById('close');
    const popup = document.getElementById('popup');
    const overlay = document.getElementById('overlay');
    

    abrir.onclick = function () {
        popup.style.display = 'block';
        overlay.style.display = 'block';
    };

    cerrar.onclick = function () {
        popup.style.animation = 'slideUp 0.5s ease';
        setTimeout(function () {
            popup.style.display = 'none';
            overlay.style.display = 'none';
            popup.style.animation = 'slideDown 0.5s ease';
            window.location.reload();  // Redireccionar o recargar la página
        }, 250);
    };

    overlay.onclick = function () {
        popup.style.animation = 'slideUp 0.5s ease';
        setTimeout(function () {
            popup.style.display = 'none';
            overlay.style.display = 'none';
            popup.style.animation = 'slideDown 0.5s ease';
            window.location.reload();  // Redireccionar o recargar la página
        }, 250);
    };





    

    

    


});

function ajaxBuscar(query){
    $.ajax({
        type: 'GET',
        url: '/buscar_cliente/',
        data: {
            q: query
        },
        success: function (response) {
            console.log(response)
            $('#clientesTable').empty();  // Vaciamos la tabla antes de actualizar
            if (response.length > 0) {
                $.each(response, function (index, item) {
                    // Construir la fila de la tabla con los datos de cada cliente
                    var row = `<tr>
                        <td>${item.patente}</td>
                        <td>${item.ultima_visita}</td>
                        <td>${item.modelo}</td>
                        <td class="openUser" data-cliente-id="${item.id}">${item.nombre}</td>
                        </tr>`;
                    $('#clientesTable').append(row);
                });
            } else {
                $('#clientesTable').append('<tr><td colspan="4">No se encontraron resultados para "' + query + '"</td></tr>');
            }
        },
        error: function (xhr, status, error) {
            console.log('Error al obtener resultados de búsqueda');
        }
    });
}

$('#searchInput').on('input', function () {
    var query = $(this).val().trim();       

    ajaxBuscar(query)

    
});


$(document).ready(function () {
    // Cargar nombres de mecánicos al cargar la página
    $.ajax({
        type: 'GET',
        url: '/obtener_nombres_mecanicos/',
        success: function (response) {
            var select = document.getElementById('selectMecanico');


            if (select) {
                select.innerHTML = '<option value="">Selecciona un mecánico...</option>';

                response.mecanicos.forEach(function (mecanico) {
                    var option = document.createElement('option');
                    option.value = mecanico.id; // Puedes usar el ID si lo necesitas
                    option.textContent = mecanico.nombre;
                    select.appendChild(option);
                });
            }




        },
        error: function (xhr, status, error) {
            alert('Error al cargar nombres de mecánicos');
        }
    });

    $('#nuevoClienteForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/guardar_cliente/',
            data: $(this).serialize(),
            success: function (response) {
                $('#nuevoClienteForm')[0].reset();
                $('#popup').hide();
                
                // Agregar el ID del cliente al input hidden
                $('#clienteIdInput').val(response.cliente_id);
                console.log($('#clienteIdInput').val());
                
                // Abre el popup de detalles del cliente
                $('#detalleClienteContainer').load('/detalles_cliente/?cliente_id=' + response.cliente_id);
                $('#popupUser').fadeIn();
                $('#overlay').fadeIn();
            },
            error: function (xhr, status, error) {
                alert('Error al guardar el cliente');
            }
        });
    });

    $('#nuevaTareaForm').submit(function (e) {
        e.preventDefault();
        
        // Obtener el valor del select
        var selectServicio = $('#selectServicio').val();

        // Enviar el formulario por AJAX
        guardarTarea(selectServicio);
    });    
});


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Buscar el token CSRF
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function cargarDetallesCliente(clienteId) {
    $.ajax({
        type: 'GET',
        url: '/detalles_cliente/',
        data: { cliente_id: clienteId },
        success: function (response) {
            // Actualizar el contenido del popup con los detalles del cliente
            $('#detalleClienteContainer').html(response);

            $.ajax({
                type: 'GET',
                url: '/tareas_cliente/',
                data: { cliente_id: clienteId },
                success: function (response) {
                    $('#tbody-tareas').empty(); // Vaciar el contenido existente antes de agregar nuevas tareas

                    response.tareas.forEach(function (tarea) {
                        var fila = `<tr data-tarea_cliente-id="${tarea.id}">
                        <td>${tarea.fecha}</td>
                        <td>${tarea.servicio}</td>
                        <td>${tarea.kilometros}</td>
                        <td>${tarea.proxservicio}</td>
                        <td>${tarea.mecanico}</td>
                        <td><a href="/planilla/?servicio=${tarea.servicio}&cliente_id=${clienteId}&fecha=${tarea.fecha}&kms=${tarea.kilometros}&tarea_id=${tarea.id}"><i class="ri-file-list-2-line"></i></a><i class="ri-close-circle-line" ></i></td>
                        </tr>`;
                        $('#tbody-tareas').append(fila);
                    });
                },
                error: function (xhr, status, error) {
                    alert('Error al cargar los detalles de las tareas');
                }
            });

            $('#popupUser').fadeIn();
            $('#overlay').fadeIn();
        },
        error: function (xhr, status, error) {
            alert('Error al cargar los detalles del cliente');
        }
    });
}

// Evento para abrir el popup del cliente al hacer clic en su nombre
$(document).on('click', '.openUser', function() {
    var clienteId = $(this).data('cliente-id');
    cargarDetallesCliente(clienteId);

    

    
});



function guardarTarea(selectServicio) {
    $.ajax({
        type: 'POST',
        url: '/guardar_tarea/',
        data: $('#nuevaTareaForm').serialize(),
        success: function (response) {
            alert('Tarea guardada correctamente');
            var planillaUrl = `/planilla/?servicio=${response.servicio}&cliente_id=${response.cliente_id}&fecha=${response.fecha}&kms=${response.kilometros}&tarea_id=${response.tarea_id}`;

            window.location.href = planillaUrl;
            //location.reload();  // Recargar la página
            $('#nuevaTareaForm')[0].reset();
            $('#popup').hide();
        },
        error: function (xhr, status, error) {
            alert('Error al guardar Tarea');
            console.error(xhr.responseText);
        }
    });
}