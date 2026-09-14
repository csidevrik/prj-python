# Reglas de trabajo para Claude en este proyecto

> Este archivo NO se carga automáticamente (no se llama `CLAUDE.md`). Si empiezas una sesión nueva, especialmente en otra PC, dile a Claude: **"lee claudio.md"** al inicio.

## Regla principal: no avanzar sin autorización explícita

Antes de:
- Editar o crear archivos de código.
- Correr comandos (Bash/PowerShell), instalar dependencias, o instalar software (ej. Docker).
- Levantar o modificar contenedores/servicios.

Claude debe **explicar qué va a hacer y por qué**, y esperar un **"sí" explícito** antes de ejecutar. No se debe encadenar varios pasos solo porque el usuario aprobó una decisión de diseño (por ejemplo, responder preguntas sobre cómo modelar datos no es aprobación para instalar software o correr scripts).

**Motivo:** en una sesión anterior, tras resolver unas preguntas de diseño sobre el modelo de datos de contratos, Claude instaló Docker Desktop, editó varios archivos, actualizó dependencias y corrió pruebas end-to-end sin pausar a explicar el plan completo primero. El usuario lo marcó como un problema: quiere entender primero, decidir después.

## Excepciones

- Documentación (`.md`) y respuestas explicativas no requieren esta pausa salvo que impliquen tocar código o correr comandos.
- Preguntas de solo lectura (leer archivos, `git status`, explorar el repo) no requieren autorización previa.
