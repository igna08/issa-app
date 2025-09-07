from app import app, db, Curso

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Add sample courses
    cursos = [
        Curso(tipo='profesorado', nombre='Profesorado de Matemática', precio=100.00),
        Curso(tipo='profesorado', nombre='Profesorado de Historia', precio=100.00),
        Curso(tipo='secundario', nombre='Secundario Completo', precio=80.00),
        Curso(tipo='otros', nombre='Curso de Verano', precio=50.00)
    ]

    db.session.bulk_save_objects(cursos)
    db.session.commit()

print("Database seeded successfully.")
