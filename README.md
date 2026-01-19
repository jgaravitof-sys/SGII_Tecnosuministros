# SIGIV - Sistema de Gestión de Inventarios y Ventas

Sistema de escritorio para gestión integral de inventarios y ventas desarrollado en Python. Incluye control de productos, registro de ventas, generación de reportes, métricas visuales y sistema de alertas de stock.

## Descripción

SIGIV (Sistema de Gestión de Inventarios y Ventas) es una aplicación de escritorio que permite a pequeñas y medianas empresas gestionar su inventario, registrar ventas, generar facturas en PDF y visualizar métricas de rendimiento mediante gráficos interactivos. El sistema cuenta con autenticación de usuarios y diferentes niveles de acceso según roles.

## Características

- **Gestión de Inventario**: Agregar, editar, eliminar y consultar productos
- **Sistema de Ventas**: Registro de ventas con carrito de compras y control de stock
- **Consultas Avanzadas**: Búsqueda por código, categoría, proveedor, precio y cantidad
- **Generación de Reportes**: Exportación de tickets de venta en formato PDF
- **Métricas Visuales**: Gráficos de productos más vendidos, más costosos e ingresos por periodo
- **Sistema de Alertas**: Notificaciones automáticas de stock bajo y eventos del sistema
- **Gestión de Usuarios**: Control de acceso con 4 roles (Administrador, Vendedor, Bodega, Gerente)
- **Interfaz Moderna**: Diseño oscuro con tema Dracula

## Tecnologías

- **Python 3.x**
- **Tkinter** - Interfaz gráfica
- **SQLite3** - Base de datos
- **ReportLab** - Generación de PDF
- **Matplotlib** - Visualización de gráficos

## Requisitos

- Python 3.7 o superior
- Bibliotecas requeridas:
```bash
pip install reportlab matplotlib
```

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/sigiv-tecnosuministros.git
cd sigiv-tecnosuministros
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
python sigiv.py
```

## Uso

### Usuarios Predeterminados

El sistema incluye usuarios de prueba:
```
Administrador:
- Usuario: admin
- Contraseña: admin123

Vendedor:
- Usuario: vendedor
- Contraseña: venta123

Bodega:
- Usuario: bodega
- Contraseña: bodega123

Gerente:
- Usuario: gerente
- Contraseña: gerente123
```

### Roles y Permisos

**Administrador**
- Acceso completo al sistema
- Gestión de inventario
- Gestión de usuarios
- Reportes y métricas
- Registro de ventas

**Vendedor**
- Registro de ventas
- Consulta de stock
- Generación de reportes

**Bodega**
- Gestión de inventario
- Visualización de alertas

**Gerente**
- Visualización de métricas
- Reportes
- Alertas del sistema

## Funcionalidades Principales

### Inventario
- Agregar nuevos productos con código autogenerado
- Editar información de productos existentes
- Eliminar productos
- Consultas por código, categoría, proveedor, precio y cantidad

### Ventas
- Sistema de carrito de compras
- Actualización automática de stock
- Generación de tickets en PDF
- Historial completo de ventas

### Reportes
- Listado de ventas realizadas
- Exportación de facturas en PDF
- Detalles completos de cada transacción

### Métricas
- Productos más vendidos (Top 10)
- Productos más costosos (Top 10)
- Ingresos por día, semana, mes y año
- Gráficos interactivos con Matplotlib

### Alertas
- Notificaciones automáticas de stock bajo (≤3 unidades)
- Registro de eventos del sistema
- Alertas de productos críticos tras ventas

## Estructura del Proyecto
```
├── sigiv.py              # Aplicación principal
├── sigivbd.db            # Base de datos SQLite (generada automáticamente)
├── requirements.txt      # Dependencias del proyecto
└── README.md            # Documentación
```

## Base de Datos

El sistema utiliza SQLite con las siguientes tablas:

- `usuarios` - Información de usuarios y roles
- `productos` - Catálogo de productos
- `ventas` - Registro de transacciones
- `detalle_ventas` - Detalles de productos vendidos
- `alertas` - Registro de alertas del sistema



## Autores

- Juan Felipe Garavito Feo


## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Soporte

Para reportar problemas o sugerir mejoras, por favor abre un issue en el repositorio.
