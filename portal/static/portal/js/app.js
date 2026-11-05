// Menú lateral en pantallas pequeñas
document.querySelectorAll('[data-menu]').forEach(function (b) {
  b.addEventListener('click', function () { document.getElementById('lateral').classList.toggle('abierto'); });
});
// Confirmación antes de eliminar
document.querySelectorAll('form[data-confirmar]').forEach(function (f) {
  f.addEventListener('submit', function (e) { if (!confirm(f.dataset.confirmar)) e.preventDefault(); });
});
// Seleccionar todos los colaboradores (casillas de horarios)
document.querySelectorAll('[data-marcar-todos]').forEach(function (m) {
  m.addEventListener('change', function () {
    document.querySelectorAll('input[name="' + m.dataset.marcarTodos + '"]').forEach(function (c) { c.checked = m.checked; });
  });
});
// Oculta las horas cuando el tipo de jornada es descanso
var tipo = document.getElementById('tipo');
if (tipo) {
  var alternar = function () {
    document.querySelectorAll('[data-solo-turno]').forEach(function (g) { g.style.display = tipo.value === 'turno' ? '' : 'none'; });
  };
  tipo.addEventListener('change', alternar); alternar();
}
