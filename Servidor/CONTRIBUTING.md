# Contribución a Smart Classroom AI

¡Gracias por contribuir al proyecto! 🎉

## 📋 Guía Rápida

### 1. Setup Inicial
```bash
# Fork el repo y clona tu fork
git clone https://github.com/TU-USUARIO/ProyectoCasaAbierta.git
cd ProyectoCasaAbierta

# Agrega el upstream
git remote add upstream https://github.com/ORIGINAL-OWNER/ProyectoCasaAbierta.git

# Crea un branch para tu feature
git checkout -b feature/mi-feature
```

### 2. Convenciones de Código

#### Python Style Guide
Seguimos **PEP 8** con algunas adiciones:

```python
# Type hints obligatorios en funciones públicas
def process_image(image: np.ndarray, threshold: float = 0.6) -> List[float]:
    """
    Process image and extract features
    
    Args:
        image: Input image as numpy array
        threshold: Detection threshold (default: 0.6)
    
    Returns:
        List of feature vectors
    
    Raises:
        ValueError: If image is invalid
    """
    pass

# Async cuando sea posible
async def fetch_student_data(student_id: str) -> Dict[str, Any]:
    result = await student_crud.find_by_id(student_id)
    return result

# Logging apropiado
logger.info(f"Processing student {student_id}")
logger.error(f"Failed to process: {str(e)}", exc_info=True)
```

#### Naming Conventions
- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

### 3. Commit Messages

Usamos **Conventional Commits**:

```bash
# Features
git commit -m "feat(attendance): add batch verification endpoint"

# Bug fixes
git commit -m "fix(emotions): handle null confidence values"

# Documentation
git commit -m "docs(readme): update API examples"

# Refactoring
git commit -m "refactor(services): extract common image processing"

# Tests
git commit -m "test(enrollment): add unit tests for enrollment service"

# Performance
git commit -m "perf(face-service): optimize embedding generation"
```

### 4. Pull Request Process

#### Checklist antes de PR:
- [ ] Código sigue PEP 8
- [ ] Tests unitarios incluidos
- [ ] Documentación actualizada (docstrings)
- [ ] No hay hardcoded credentials
- [ ] Logs apropiados agregados
- [ ] Type hints en funciones públicas
- [ ] Manejo de errores implementado

#### Template de PR:
```markdown
## Descripción
Breve descripción del cambio

## Tipo de cambio
- [ ] Bug fix
- [ ] Nueva feature
- [ ] Breaking change
- [ ] Documentación

## Testing
Describe las pruebas realizadas

## Checklist
- [ ] Tests pasan localmente
- [ ] Documentación actualizada
- [ ] Code review solicitado
```

### 5. Estructura de Tests

```python
# tests/test_face_service.py
import pytest
from app.services.face_service import FaceRecognitionService

@pytest.fixture
def face_service():
    return FaceRecognitionService()

def test_generate_embedding_success(face_service, sample_image):
    """Test successful embedding generation"""
    embedding = face_service.generate_embedding(sample_image)
    
    assert len(embedding) == 128
    assert all(isinstance(x, float) for x in embedding)

def test_generate_embedding_no_face(face_service, empty_image):
    """Test error when no face detected"""
    with pytest.raises(FaceNotDetectedException):
        face_service.generate_embedding(empty_image)
```

### 6. Code Review Guidelines

#### Como Reviewer:
- ✅ Ser constructivo y amable
- ✅ Explicar el "por qué" de tus sugerencias
- ✅ Aprobar si es "good enough", no esperar perfección
- ❌ No hacer comments sin contexto ("esto está mal")

#### Como Author:
- ✅ Responder a todos los comments
- ✅ Hacer cambios pequeños e iterativos
- ✅ Agradecer el feedback
- ❌ No tomar los comments personal

### 7. Branches Strategy

```
main (producción) ← develop (staging) ← feature/* (development)
```

- `main`: Código en producción
- `develop`: Staging/pre-producción
- `feature/*`: Desarrollo de features
- `hotfix/*`: Fixes urgentes para producción

### 8. Reporte de Bugs

Usa el template:

```markdown
**Descripción del Bug**
Descripción clara del problema

**Para Reproducir**
1. Endpoint: POST /api/v1/attendance/verify
2. Payload: {...}
3. Error: {...}

**Comportamiento Esperado**
Qué debería suceder

**Screenshots**
Si aplica

**Environment**
- OS: Windows 11
- Python: 3.9.10
- Branch: develop
```

### 9. Feature Requests

```markdown
**Feature Propuesta**
Descripción de la feature

**Problema que Resuelve**
Por qué es necesaria

**Solución Propuesta**
Cómo se implementaría

**Alternativas Consideradas**
Otras opciones evaluadas

**Impacto**
- Frontend: Sí/No
- Backend: Sí/No
- Database: Sí/No
```

### 10. Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [DeepFace GitHub](https://github.com/serengil/deepface)
- [PEP 8 Style Guide](https://pep8.org)
- [Conventional Commits](https://www.conventionalcommits.org)

## 🤝 Contacto

- **Slack**: #smart-classroom-dev
- **Email**: tech-lead@example.com
- **Issues**: GitHub Issues

---

¡Gracias por hacer Smart Classroom AI mejor! 🚀
