import os
# Set dummy env var before importing app to prevent SDK error
os.environ['MERCADOPAGO_ACCESS_TOKEN'] = 'dummy-token-for-scripts'

from app import app, db, Curso

with app.app_context():
    # Clear existing data
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()

    # Add sample courses
    print("Adding sample courses...")
    cursos = [
        Curso(tipo='profesorado', nombre='Profesorado de Matemática', precio=100.00, cupo_maximo=30),
        Curso(tipo='profesorado', nombre='Profesorado de Historia', precio=100.00, cupo_maximo=30),
        Curso(tipo='secundario', nombre='Secundario Completo', precio=80.00, cupo_maximo=50),
        Curso(tipo='otros', nombre='Curso de Verano de Programación', precio=50.00, cupo_maximo=20)
    ]

    db.session.bulk_save_objects(cursos)
    db.session.commit()

print("Database seeded successfully.")
