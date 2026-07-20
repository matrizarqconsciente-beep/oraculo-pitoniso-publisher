# Oráculo Pitoniso - Publicador Automático

Publica automáticamente el ranking y resultados del Oráculo Pitoniso en redes sociales (Facebook, próximamente más).

## Estructura

```
├── social_publisher.py          # Orquestador principal
├── publishers/
│   └── facebook_client.py      # Publicación en Facebook
├── utils/
│   └── image_generator.py      # Generación de imágenes con Pillow
├── data/
│   └── competition_results.json # Datos de la competencia
├── scripts/
│   └── push_results.ps1        # Script para subir datos desde PC
├── .env                         # Credenciales (NO subir a git)
└── .github/workflows/
    └── publish.yml              # GitHub Actions (automático cada 6h)
```

## Uso

### Local
```bash
pip install -r requirements.txt
python social_publisher.py ranking   # Publicar ranking
python social_publisher.py daily     # Publicar resumen diario
```

### Automático en la nube
GitHub Actions ejecuta `social_publisher.py ranking` cada 6 horas automáticamente.
