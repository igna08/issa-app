from app import app, db, Administrador, bcrypt

with app.app_context():
    # You can change the admin credentials here
    admin_email = "admin@example.com"
    admin_password = "password"
    admin_name = "Admin"

    # Check if the admin already exists
    if Administrador.query.filter_by(email=admin_email).first():
        print(f"Admin with email {admin_email} already exists.")
    else:
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        new_admin = Administrador(
            nombre=admin_name,
            email=admin_email,
            password=hashed_password
        )
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user {admin_name} created successfully.")
