-- Esquema de 100 tablas conectadas (PostgreSQL)
-- Decisiones: BIGSERIAL, multitenencia (tenant_id), timestamps, soft-delete
-- Orden: Catálogos/Identidad primero, luego módulos; al final relaciones transversales

BEGIN;

-- 01) Núcleo de multitenencia y usuarios (12)
CREATE TABLE tenant (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE usuario (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL,
  tipo TEXT NOT NULL, -- propietario, inquilino, admin, proveedor
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE rol (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE permiso (
  id BIGSERIAL PRIMARY KEY,
  codigo TEXT NOT NULL UNIQUE,
  descripcion TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rol_permiso (
  id BIGSERIAL PRIMARY KEY,
  rol_id BIGINT NOT NULL REFERENCES rol(id) ON DELETE CASCADE,
  permiso_id BIGINT NOT NULL REFERENCES permiso(id) ON DELETE CASCADE,
  UNIQUE(rol_id, permiso_id)
);

CREATE TABLE usuario_rol (
  id BIGSERIAL PRIMARY KEY,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  rol_id BIGINT NOT NULL REFERENCES rol(id) ON DELETE CASCADE,
  UNIQUE(usuario_id, rol_id)
);

CREATE TABLE sesion_usuario (
  id BIGSERIAL PRIMARY KEY,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  ultimo_login TIMESTAMPTZ,
  ip TEXT,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE auditoria_evento (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  usuario_id BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  entidad TEXT NOT NULL,
  entidad_id BIGINT,
  accion TEXT NOT NULL,
  datos JSONB,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE preferencia_usuario (
  id BIGSERIAL PRIMARY KEY,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  clave TEXT NOT NULL,
  valor TEXT,
  UNIQUE(usuario_id, clave)
);

CREATE TABLE proveedor (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  email TEXT,
  telefono TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE cliente (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  usuario_id BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  nombre TEXT NOT NULL,
  email TEXT,
  telefono TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

-- 02) Geografía y catálogos (10)
CREATE TABLE pais (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL
);
CREATE TABLE ciudad (
  id BIGSERIAL PRIMARY KEY,
  pais_id BIGINT NOT NULL REFERENCES pais(id) ON DELETE RESTRICT,
  nombre TEXT NOT NULL
);
CREATE TABLE barrio (
  id BIGSERIAL PRIMARY KEY,
  ciudad_id BIGINT NOT NULL REFERENCES ciudad(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL
);
CREATE TABLE tipo_inmueble (id BIGSERIAL PRIMARY KEY, nombre TEXT NOT NULL);
CREATE TABLE tipo_documento (id BIGSERIAL PRIMARY KEY, nombre TEXT NOT NULL);
CREATE TABLE banco (id BIGSERIAL PRIMARY KEY, nombre TEXT NOT NULL);
CREATE TABLE moneda (id BIGSERIAL PRIMARY KEY, codigo TEXT NOT NULL UNIQUE);
CREATE TABLE impuesto (id BIGSERIAL PRIMARY KEY, nombre TEXT NOT NULL, tasa NUMERIC(6,3) NOT NULL);
CREATE TABLE estado_generico (id BIGSERIAL PRIMARY KEY, modulo TEXT NOT NULL, nombre TEXT NOT NULL);
CREATE TABLE motivo_generico (id BIGSERIAL PRIMARY KEY, modulo TEXT NOT NULL, nombre TEXT NOT NULL);

-- 03) Inmuebles (12)
CREATE TABLE inmueble (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  propietario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE RESTRICT,
  tipo_id BIGINT NOT NULL REFERENCES tipo_inmueble(id) ON DELETE RESTRICT,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  direccion TEXT NOT NULL,
  barrio_id BIGINT REFERENCES barrio(id) ON DELETE SET NULL,
  ciudad_id BIGINT REFERENCES ciudad(id) ON DELETE SET NULL,
  area NUMERIC(10,2) NOT NULL,
  habitaciones INT NOT NULL DEFAULT 0,
  banos INT NOT NULL DEFAULT 0,
  parqueaderos INT NOT NULL DEFAULT 0,
  precio_arriendo NUMERIC(12,2) NOT NULL,
  precio_administracion NUMERIC(12,2) NOT NULL DEFAULT 0,
  deposito_seguridad NUMERIC(12,2) NOT NULL DEFAULT 0,
  estado_id BIGINT REFERENCES estado_generico(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE imagen_inmueble (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  principal BOOLEAN NOT NULL DEFAULT FALSE,
  orden INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE caracteristica_tipo (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL
);

CREATE TABLE caracteristica_inmueble (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  tipo_id BIGINT NOT NULL REFERENCES caracteristica_tipo(id) ON DELETE RESTRICT,
  valor TEXT
);

CREATE TABLE documento_inmueble (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  tipo_documento_id BIGINT NOT NULL REFERENCES tipo_documento(id) ON DELETE RESTRICT,
  ruta TEXT NOT NULL,
  creado_por BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE historial_estado_inmueble (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  estado_id BIGINT NOT NULL REFERENCES estado_generico(id) ON DELETE RESTRICT,
  motivo_id BIGINT REFERENCES motivo_generico(id) ON DELETE SET NULL,
  cambiado_por BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  cambiado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE visita_inmueble (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  interesado_id BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  agendada_para TIMESTAMPTZ NOT NULL,
  resultado TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE bloqueo_calendario (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  fecha_inicio TIMESTAMPTZ NOT NULL,
  fecha_fin TIMESTAMPTZ NOT NULL,
  motivo TEXT
);

CREATE TABLE avaluo_inmueble (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  valor NUMERIC(12,2) NOT NULL,
  fecha TIMESTAMPTZ NOT NULL
);

-- 04) Contratos (12)
CREATE TABLE contrato (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE RESTRICT,
  inquilino_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE RESTRICT,
  numero TEXT NOT NULL UNIQUE,
  estado_id BIGINT REFERENCES estado_generico(id) ON DELETE SET NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  valor_arriendo NUMERIC(12,2) NOT NULL,
  valor_administracion NUMERIC(12,2) NOT NULL DEFAULT 0,
  valor_deposito NUMERIC(12,2) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE firma_contrato (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  firma TEXT NOT NULL,
  ip TEXT,
  user_agent TEXT,
  firmado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(contrato_id, usuario_id)
);

CREATE TABLE anexo_contrato (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  tipo_documento_id BIGINT REFERENCES tipo_documento(id) ON DELETE SET NULL,
  ruta TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE historial_estado_contrato (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  estado_id BIGINT NOT NULL REFERENCES estado_generico(id) ON DELETE RESTRICT,
  motivo_id BIGINT REFERENCES motivo_generico(id) ON DELETE SET NULL,
  cambiado_por BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  cambiado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE prorroga_contrato (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  nueva_fecha_fin DATE NOT NULL,
  aprobado_por BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  aprobado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE penalidad_contrato (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  descripcion TEXT NOT NULL,
  monto NUMERIC(12,2) NOT NULL,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE garantia_contrato (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  descripcion TEXT,
  valor NUMERIC(12,2) NOT NULL
);

CREATE TABLE version_contrato (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  numero_version INT NOT NULL,
  contenido TEXT NOT NULL,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(contrato_id, numero_version)
);

CREATE TABLE documento_contrato (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  tipo_documento_id BIGINT REFERENCES tipo_documento(id) ON DELETE SET NULL,
  ruta TEXT NOT NULL,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE solicitud_arriendo (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  solicitante_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  propietario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  estado_id BIGINT REFERENCES estado_generico(id) ON DELETE SET NULL,
  mensaje TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 05) Pagos y contable (16)
CREATE TABLE cuenta_bancaria (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  usuario_id BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  banco_id BIGINT REFERENCES banco(id) ON DELETE SET NULL,
  numero TEXT NOT NULL,
  tipo TEXT,
  moneda_id BIGINT REFERENCES moneda(id) ON DELETE SET NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE pago (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT NOT NULL REFERENCES contrato(id) ON DELETE CASCADE,
  periodo_inicio DATE NOT NULL,
  periodo_fin DATE NOT NULL,
  fecha_vencimiento DATE NOT NULL,
  monto NUMERIC(12,2) NOT NULL,
  monto_pagado NUMERIC(12,2) NOT NULL DEFAULT 0,
  estado_id BIGINT REFERENCES estado_generico(id) ON DELETE SET NULL,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE registro_pago (
  id BIGSERIAL PRIMARY KEY,
  pago_id BIGINT NOT NULL REFERENCES pago(id) ON DELETE CASCADE,
  monto NUMERIC(12,2) NOT NULL,
  medio TEXT,
  comprobante TEXT,
  registrado_por BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  registrado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE factura (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT REFERENCES contrato(id) ON DELETE SET NULL,
  numero TEXT NOT NULL UNIQUE,
  moneda_id BIGINT REFERENCES moneda(id) ON DELETE SET NULL,
  total NUMERIC(12,2) NOT NULL,
  emitida_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE factura_detalle (
  id BIGSERIAL PRIMARY KEY,
  factura_id BIGINT NOT NULL REFERENCES factura(id) ON DELETE CASCADE,
  descripcion TEXT NOT NULL,
  cantidad NUMERIC(10,2) NOT NULL,
  precio NUMERIC(12,2) NOT NULL
);

CREATE TABLE impuesto_detalle (
  id BIGSERIAL PRIMARY KEY,
  factura_id BIGINT NOT NULL REFERENCES factura(id) ON DELETE CASCADE,
  impuesto_id BIGINT REFERENCES impuesto(id) ON DELETE SET NULL,
  base NUMERIC(12,2) NOT NULL,
  valor NUMERIC(12,2) NOT NULL
);

CREATE TABLE nota_credito (
  id BIGSERIAL PRIMARY KEY,
  factura_id BIGINT NOT NULL REFERENCES factura(id) ON DELETE CASCADE,
  motivo TEXT,
  valor NUMERIC(12,2) NOT NULL,
  creada_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE nota_debito (
  id BIGSERIAL PRIMARY KEY,
  factura_id BIGINT NOT NULL REFERENCES factura(id) ON DELETE CASCADE,
  motivo TEXT,
  valor NUMERIC(12,2) NOT NULL,
  creada_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE conciliacion_bancaria (
  id BIGSERIAL PRIMARY KEY,
  cuenta_bancaria_id BIGINT NOT NULL REFERENCES cuenta_bancaria(id) ON DELETE CASCADE,
  periodo TEXT NOT NULL,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE transaccion_bancaria (
  id BIGSERIAL PRIMARY KEY,
  cuenta_bancaria_id BIGINT NOT NULL REFERENCES cuenta_bancaria(id) ON DELETE CASCADE,
  fecha TIMESTAMPTZ NOT NULL,
  descripcion TEXT,
  valor NUMERIC(12,2) NOT NULL
);

CREATE TABLE asiento_contable (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT REFERENCES contrato(id) ON DELETE SET NULL,
  fecha TIMESTAMPTZ NOT NULL,
  descripcion TEXT
);

CREATE TABLE asiento_detalle (
  id BIGSERIAL PRIMARY KEY,
  asiento_id BIGINT NOT NULL REFERENCES asiento_contable(id) ON DELETE CASCADE,
  cuenta TEXT NOT NULL,
  debe NUMERIC(12,2) NOT NULL,
  haber NUMERIC(12,2) NOT NULL
);

-- 06) Mantenimientos (10)
CREATE TABLE solicitud_mantenimiento (
  id BIGSERIAL PRIMARY KEY,
  inmueble_id BIGINT NOT NULL REFERENCES inmueble(id) ON DELETE CASCADE,
  solicitante_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  descripcion TEXT NOT NULL,
  estado_id BIGINT REFERENCES estado_generico(id) ON DELETE SET NULL,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orden_trabajo (
  id BIGSERIAL PRIMARY KEY,
  solicitud_id BIGINT NOT NULL REFERENCES solicitud_mantenimiento(id) ON DELETE CASCADE,
  proveedor_id BIGINT REFERENCES proveedor(id) ON DELETE SET NULL,
  asignado_a BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  estado_id BIGINT REFERENCES estado_generico(id) ON DELETE SET NULL,
  creada_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE repuesto (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  precio NUMERIC(12,2)
);

CREATE TABLE orden_repuesto (
  id BIGSERIAL PRIMARY KEY,
  orden_id BIGINT NOT NULL REFERENCES orden_trabajo(id) ON DELETE CASCADE,
  repuesto_id BIGINT REFERENCES repuesto(id) ON DELETE SET NULL,
  cantidad NUMERIC(10,2) NOT NULL,
  precio NUMERIC(12,2) NOT NULL
);

CREATE TABLE evidencia_mantenimiento (
  id BIGSERIAL PRIMARY KEY,
  orden_id BIGINT NOT NULL REFERENCES orden_trabajo(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  nota TEXT,
  creada_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cotizacion_mantenimiento (
  id BIGSERIAL PRIMARY KEY,
  solicitud_id BIGINT NOT NULL REFERENCES solicitud_mantenimiento(id) ON DELETE CASCADE,
  proveedor_id BIGINT REFERENCES proveedor(id) ON DELETE SET NULL,
  valor NUMERIC(12,2) NOT NULL,
  creada_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE aprobacion_mantenimiento (
  id BIGSERIAL PRIMARY KEY,
  cotizacion_id BIGINT NOT NULL REFERENCES cotizacion_mantenimiento(id) ON DELETE CASCADE,
  aprobado_por BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  aprobado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sla_mantenimiento (
  id BIGSERIAL PRIMARY KEY,
  orden_id BIGINT NOT NULL REFERENCES orden_trabajo(id) ON DELETE CASCADE,
  tiempo_objetivo_horas INT NOT NULL,
  cumplido BOOLEAN
);

CREATE TABLE historial_estado_mantenimiento (
  id BIGSERIAL PRIMARY KEY,
  orden_id BIGINT NOT NULL REFERENCES orden_trabajo(id) ON DELETE CASCADE,
  estado_id BIGINT NOT NULL REFERENCES estado_generico(id) ON DELETE RESTRICT,
  cambiado_por BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  cambiado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 07) Notificaciones y comunicación (9)
CREATE TABLE plantilla_notificacion (
  id BIGSERIAL PRIMARY KEY,
  codigo TEXT NOT NULL UNIQUE,
  canal TEXT NOT NULL, -- email, sms, push
  asunto TEXT,
  cuerpo TEXT
);

CREATE TABLE notificacion (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  titulo TEXT NOT NULL,
  mensaje TEXT,
  tipo TEXT,
  enlace TEXT,
  leida BOOLEAN NOT NULL DEFAULT FALSE,
  fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evento (
  id BIGSERIAL PRIMARY KEY,
  contrato_id BIGINT REFERENCES contrato(id) ON DELETE SET NULL,
  pago_id BIGINT REFERENCES pago(id) ON DELETE SET NULL,
  mantenimiento_id BIGINT REFERENCES orden_trabajo(id) ON DELETE SET NULL,
  tipo TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE envio_notificacion (
  id BIGSERIAL PRIMARY KEY,
  notificacion_id BIGINT NOT NULL REFERENCES notificacion(id) ON DELETE CASCADE,
  canal TEXT NOT NULL,
  estado TEXT,
  intentos INT NOT NULL DEFAULT 0,
  ultima_respuesta TEXT,
  enviado_en TIMESTAMPTZ
);

CREATE TABLE preferencia_notificacion (
  id BIGSERIAL PRIMARY KEY,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  canal TEXT NOT NULL,
  habilitado BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE(usuario_id, canal)
);

CREATE TABLE webhook_externo (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  secreto TEXT,
  activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE log_webhook (
  id BIGSERIAL PRIMARY KEY,
  webhook_id BIGINT NOT NULL REFERENCES webhook_externo(id) ON DELETE CASCADE,
  evento_id BIGINT REFERENCES evento(id) ON DELETE SET NULL,
  estado INT,
  respuesta TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 08) Integraciones / Jobs (7)
CREATE TABLE job_programado (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  cron TEXT NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE job_ejecucion (
  id BIGSERIAL PRIMARY KEY,
  job_id BIGINT NOT NULL REFERENCES job_programado(id) ON DELETE CASCADE,
  inicio TIMESTAMPTZ NOT NULL,
  fin TIMESTAMPTZ,
  exito BOOLEAN,
  detalle TEXT
);

CREATE TABLE endpoint_externo (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  base_url TEXT NOT NULL
);

CREATE TABLE mapeo_endpoint (
  id BIGSERIAL PRIMARY KEY,
  endpoint_id BIGINT NOT NULL REFERENCES endpoint_externo(id) ON DELETE CASCADE,
  entidad TEXT NOT NULL,
  mapeo JSONB NOT NULL
);

CREATE TABLE log_integracion (
  id BIGSERIAL PRIMARY KEY,
  endpoint_id BIGINT REFERENCES endpoint_externo(id) ON DELETE SET NULL,
  payload JSONB,
  respuesta JSONB,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cola_mensajes (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  tema TEXT NOT NULL,
  mensaje JSONB NOT NULL,
  encolado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE intento_cola (
  id BIGSERIAL PRIMARY KEY,
  cola_id BIGINT NOT NULL REFERENCES cola_mensajes(id) ON DELETE CASCADE,
  intento INT NOT NULL,
  estado TEXT,
  detalle TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 09) Reportes / Snapshots (6)
CREATE TABLE snapshot_mensual (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  periodo TEXT NOT NULL,
  kpis JSONB NOT NULL,
  generado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE metrica_agrupada (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  dimensiones JSONB,
  valor NUMERIC(18,4) NOT NULL,
  calculado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE programacion_reporte (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL,
  cron TEXT NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE ejecucion_reporte (
  id BIGSERIAL PRIMARY KEY,
  programacion_id BIGINT NOT NULL REFERENCES programacion_reporte(id) ON DELETE CASCADE,
  inicio TIMESTAMPTZ NOT NULL,
  fin TIMESTAMPTZ,
  exito BOOLEAN,
  salida TEXT
);

CREATE TABLE vista_materializada_control (
  id BIGSERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  ultima_actualizacion TIMESTAMPTZ
);

CREATE TABLE comentario_reporte (
  id BIGSERIAL PRIMARY KEY,
  reporte_id BIGINT REFERENCES programacion_reporte(id) ON DELETE SET NULL,
  usuario_id BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  comentario TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 10) Mensajería interna / Chats (6)
CREATE TABLE conversacion (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  asunto TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE conversacion_usuario (
  id BIGSERIAL PRIMARY KEY,
  conversacion_id BIGINT NOT NULL REFERENCES conversacion(id) ON DELETE CASCADE,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  UNIQUE(conversacion_id, usuario_id)
);

CREATE TABLE mensaje (
  id BIGSERIAL PRIMARY KEY,
  conversacion_id BIGINT NOT NULL REFERENCES conversacion(id) ON DELETE CASCADE,
  autor_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  cuerpo TEXT NOT NULL,
  enviado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE mensaje_leido (
  id BIGSERIAL PRIMARY KEY,
  mensaje_id BIGINT NOT NULL REFERENCES mensaje(id) ON DELETE CASCADE,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  leido_en TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(mensaje_id, usuario_id)
);

CREATE TABLE adjunto_mensaje (
  id BIGSERIAL PRIMARY KEY,
  mensaje_id BIGINT NOT NULL REFERENCES mensaje(id) ON DELETE CASCADE,
  ruta TEXT NOT NULL
);

CREATE TABLE denuncia_mensaje (
  id BIGSERIAL PRIMARY KEY,
  mensaje_id BIGINT NOT NULL REFERENCES mensaje(id) ON DELETE CASCADE,
  reportado_por BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  motivo TEXT,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 11) Archivos y etiquetas (6)
CREATE TABLE archivo (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  ruta TEXT NOT NULL,
  tipo TEXT,
  creado_por BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE archivo_relacion (
  id BIGSERIAL PRIMARY KEY,
  archivo_id BIGINT NOT NULL REFERENCES archivo(id) ON DELETE CASCADE,
  entidad TEXT NOT NULL,
  entidad_id BIGINT NOT NULL
);

CREATE TABLE tag (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  nombre TEXT NOT NULL
);

CREATE TABLE entidad_tag (
  id BIGSERIAL PRIMARY KEY,
  tag_id BIGINT NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
  entidad TEXT NOT NULL,
  entidad_id BIGINT NOT NULL
);

CREATE TABLE favorito (
  id BIGSERIAL PRIMARY KEY,
  usuario_id BIGINT NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  entidad TEXT NOT NULL,
  entidad_id BIGINT NOT NULL
);

CREATE TABLE tarea (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  asignado_a BIGINT REFERENCES usuario(id) ON DELETE SET NULL,
  estado_id BIGINT REFERENCES estado_generico(id) ON DELETE SET NULL,
  vencimiento TIMESTAMPTZ
);

-- Conteo aproximado: 12 + 10 + 12 + 12 + 16 + 10 + 9 + 7 + 6 + 6 + 6 = 106 tablas
-- (Incluye tablas puente, historial y soporte para mantener el grafo conectado)

COMMIT;
