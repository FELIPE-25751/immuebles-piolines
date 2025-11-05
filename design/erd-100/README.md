# ERD de 100 tablas (PostgreSQL) — Borrador técnico

Este directorio contiene un esquema SQL con 100 tablas conectadas entre sí mediante claves foráneas, organizado por módulos (Identidad, Inmuebles, Contratos, Pagos, Mantenimientos, Notificaciones, Integraciones, Catálogos/Geo, Reportes, Mensajería, Tareas, Archivos, Tags).

Decisiones asumidas (puedes cambiarlas antes de ejecutar):
- Motor: PostgreSQL
- PK: BIGSERIAL (enteros autoincrementales)
- Multitenencia: sí (todas las tablas incluyen `tenant_id` → `tenant.id`)
- Borrado: soft-delete opcional (`deleted_at`), y `ON DELETE` según el tipo:
  - Historial/log/adjuntos: `ON DELETE CASCADE`
  - Maestras/relaciones clave: `ON DELETE RESTRICT` o `SET NULL` cuando aplique
- Timestamps: `created_at`, `updated_at` con default `now()`

Archivos:
- `schema.sql`: DDL con 100 `CREATE TABLE` y sus `FOREIGN KEY` correspondientes.
- `ERD.drawio`: Diagrama multipágina (Overview, módulos 01..11, Relaciones Transversales y Global Completo).

Uso local (opcional):
- Crea una base vacía y ejecuta el DDL con psql:
  - `psql -h <host> -U <user> -d <db> -f schema.sql`
- Para revertir, elimina la base o ejecuta `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` (modifica según tu entorno).

Notas:
- El grafo es conectado: desde cualquier módulo puedes llegar a otro (p. ej., `usuario` → `contrato` → `pago` → `notificacion`), sin caer en un grafo completo (todos-con-todos) que sería inmanejable.
- Puedes abrir este directorio en VS Code y, con tu extensión Draw.io, construir el ERD visual a partir de estas tablas (o pedir que lo genere yo en un archivo `.drawio.svg`).

Exportar imágenes (PNG/SVG/PDF) desde Draw.io:
- Abre `ERD.drawio` y selecciona la pestaña que quieres exportar (ej. `04 - Contratos`).
- Archivo > Exportar como > PNG/SVG/PDF.
- Asegúrate de:
  - Desmarcar “Solo selección”.
  - Marcar “Recortar” (Crop) para que el lienzo se ajuste al contenido.
  - Escala 1x (o 2x si quieres más resolución).
  - Página actual (o el rango de páginas que prefieras).
- Tip: si al exportar sale “en blanco” pero con una imagen muy grande (p. ej., 16000×8000), es porque se exportó la página completa sin contenido visible. Cambia a la pestaña correcta y marca “Recortar”. También puedes ir a Organizar > Tamaño de página > Ajustar a contenido para que la página se reduzca al dibujo.
