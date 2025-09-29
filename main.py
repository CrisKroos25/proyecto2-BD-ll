import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QComboBox, QHeaderView,
    QInputDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# conexion
try:
    conexion = mysql.connector.connect(
        host="192.168.56.102",  # NDB1 192.168.56.102(admin123) - NDB2 192.168.56.103(admin)
        user="usuario1",
        passwd="admin123",
        database="empresa_db"
    )
except:
    conexion = mysql.connector.connect(
        host="192.168.56.103",  # NDB2 192.168.56.103(admin) - NDB1 192.168.56.102(admin123)
        user="usuario1",
        passwd="admin",
        database="empresa_db"
    )

cursor = conexion.cursor()


class EmpresaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión Profesional 💼")
        self.setGeometry(150, 100, 950, 600)
        self.setStyleSheet("background-color: #ffffff; color: #000000; font-family: Arial;")

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #e0e0e0;
                padding: 12px 25px;
                border-radius: 12px;
                margin-right: 5px;
                font-weight: bold;
                color: #000000;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)

        self.tab_cliente = QWidget()
        self.tab_contacto = QWidget()
        self.tab_empleado = QWidget()

        self.tabs.addTab(self.tab_cliente, "👤 Clientes")
        self.tabs.addTab(self.tab_contacto, "📞 Contactos")
        self.tabs.addTab(self.tab_empleado, "🧑‍💼 Empleados")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.setup_tab_cliente()
        self.setup_tab_contacto()
        self.setup_tab_empleado()

    def setup_tab_cliente(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        form = QHBoxLayout()
        self.entry_nombre_cliente = QLineEdit()
        self.entry_email_cliente = QLineEdit()
        self.entry_nombre_cliente.setPlaceholderText("Nombre del cliente")
        self.entry_email_cliente.setPlaceholderText("Correo electrónico")
        self.entry_nombre_cliente.setStyleSheet(
            "padding:5px; border-radius:5px; border:1px solid #ccc; color: #000000;"
        )
        self.entry_email_cliente.setStyleSheet(
            "padding:5px; border-radius:5px; border:1px solid #ccc; color: #000000;"
        )
        form.addWidget(QLabel("Nombre:"))
        form.addWidget(self.entry_nombre_cliente)
        form.addWidget(QLabel("Email:"))
        form.addWidget(self.entry_email_cliente)

        btn_agregar = QPushButton("Agregar Cliente")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color:#2ecc71; color:white; font-weight:bold;
                padding:8px 20px; border-radius:10px;
            }
            QPushButton:hover {
                background-color:#27ae60;
            }
        """)
        btn_agregar.clicked.connect(self.agregar_cliente)

        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(5)  # ID, Nombre, Email, Edit, Delete
        self.tabla_clientes.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Editar", "Eliminar"])
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_clientes.setStyleSheet("""
            QTableWidget { background-color: #ffffff; color: #000000; border-radius:10px; }
            QHeaderView::section { background-color:#3498db; color:white; padding:5px; font-weight:bold; }
        """)
        self.tabla_clientes.setAlternatingRowColors(True)
        self.tabla_clientes.setFont(QFont("Arial", 10))

        layout.addLayout(form)
        layout.addWidget(btn_agregar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.tabla_clientes)

        self.tab_cliente.setLayout(layout)
        self.mostrar_clientes()

    def agregar_cliente(self):
        nombre = self.entry_nombre_cliente.text()
        email = self.entry_email_cliente.text()
        if nombre and email:
            try:
                query = "INSERT INTO cliente (nombre, email) VALUES (%s, %s)"
                cursor.execute(query, (nombre, email))
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Cliente agregado correctamente ✅")
                self.entry_nombre_cliente.clear()
                self.entry_email_cliente.clear()
                self.mostrar_clientes()
                self.cargar_clientes_combo()
            except mysql.connector.Error as e:
                QMessageBox.warning(self, "Error", f"No se pudo guardar: {e}")
        else:
            QMessageBox.warning(self, "Advertencia", "Debes llenar todos los campos ⚠️")

    def mostrar_clientes(self):
        cursor.execute("SELECT * FROM cliente")
        resultados = cursor.fetchall()
        self.tabla_clientes.setRowCount(len(resultados))
        for fila, datos in enumerate(resultados):
            self.tabla_clientes.setItem(fila, 0, QTableWidgetItem(str(datos[0])))
            self.tabla_clientes.setItem(fila, 1, QTableWidgetItem(datos[1]))
            self.tabla_clientes.setItem(fila, 2, QTableWidgetItem(datos[2]))

            btn_edit = QPushButton("✏️")
            btn_edit.setStyleSheet("background-color:#f1c40f; border-radius:5px; color:black;")
            btn_edit.clicked.connect(lambda _, r=fila: self.editar_cliente(r))
            self.tabla_clientes.setCellWidget(fila, 3, btn_edit)

            btn_delete = QPushButton("🗑️")
            btn_delete.setStyleSheet("background-color:#e74c3c; border-radius:5px; color:white;")
            btn_delete.clicked.connect(lambda _, r=fila: self.eliminar_cliente(r))
            self.tabla_clientes.setCellWidget(fila, 4, btn_delete)

    def editar_cliente(self, fila):
        id_cliente = int(self.tabla_clientes.item(fila, 0).text())
        nombre = self.tabla_clientes.item(fila, 1).text()
        email = self.tabla_clientes.item(fila, 2).text()
        nuevo_nombre, ok1 = QInputDialog.getText(self, "Editar Nombre", "Nombre:", text=nombre)
        nuevo_email, ok2 = QInputDialog.getText(self, "Editar Email", "Email:", text=email)
        if ok1 and ok2:
            query = "UPDATE cliente SET nombre=%s, email=%s WHERE id_cliente=%s"
            cursor.execute(query, (nuevo_nombre, nuevo_email, id_cliente))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Cliente editado ✅")
            self.mostrar_clientes()
            self.cargar_clientes_combo()

    def eliminar_cliente(self, fila):
        id_cliente = int(self.tabla_clientes.item(fila, 0).text())
        reply = QMessageBox.question(self, 'Eliminar Cliente', '¿Seguro que deseas eliminar este cliente?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            cursor.execute("DELETE FROM cliente WHERE id_cliente=%s", (id_cliente,))
            conexion.commit()
            self.mostrar_clientes()
            self.cargar_clientes_combo()

    def setup_tab_contacto(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        form = QHBoxLayout()
        self.combo_cliente = QComboBox()
        self.entry_telefono = QLineEdit()
        self.entry_telefono.setPlaceholderText("Teléfono")
        self.entry_telefono.setStyleSheet(
            "padding:5px; border-radius:5px; border:1px solid #ccc; color: #000000;"
        )
        form.addWidget(QLabel("Cliente:"))
        form.addWidget(self.combo_cliente)
        form.addWidget(QLabel("Teléfono:"))
        form.addWidget(self.entry_telefono)

        btn_agregar = QPushButton("Agregar Contacto")
        btn_agregar.setStyleSheet("""
            QPushButton { background-color:#3498db; color:white; font-weight:bold; padding:8px 20px; border-radius:10px; }
            QPushButton:hover { background-color:#2980b9; }
        """)
        btn_agregar.clicked.connect(self.agregar_contacto)

        self.tabla_contactos = QTableWidget()
        self.tabla_contactos.setColumnCount(4)  # ID, Cliente, Teléfono, Eliminar
        self.tabla_contactos.setHorizontalHeaderLabels(["ID", "Cliente", "Teléfono", "Eliminar"])
        self.tabla_contactos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_contactos.setStyleSheet("""
            QTableWidget { background-color:#ffffff; color:#000000; border-radius:10px; }
            QHeaderView::section { background-color:#3498db; color:white; padding:5px; font-weight:bold; }
        """)
        self.tabla_contactos.setAlternatingRowColors(True)
        self.tabla_contactos.setFont(QFont("Arial", 10))

        layout.addLayout(form)
        layout.addWidget(btn_agregar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.tabla_contactos)

        self.tab_contacto.setLayout(layout)
        self.cargar_clientes_combo()
        self.mostrar_contactos()

    def agregar_contacto(self):
        cliente_id = self.combo_cliente.currentData()
        telefono = self.entry_telefono.text()
        if cliente_id and telefono:
            query = "INSERT INTO contacto (id_cliente, telefono) VALUES (%s, %s)"
            cursor.execute(query, (cliente_id, telefono))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Contacto agregado ✅")
            self.entry_telefono.clear()
            self.mostrar_contactos()
        else:
            QMessageBox.warning(self, "Advertencia", "Llena todos los campos ⚠️")

    def mostrar_contactos(self):
        query = """SELECT contacto.id_contacto, cliente.nombre, contacto.telefono
                   FROM contacto
                            JOIN cliente ON contacto.id_cliente = cliente.id_cliente"""
        cursor.execute(query)
        resultados = cursor.fetchall()
        self.tabla_contactos.setRowCount(len(resultados))
        for fila, datos in enumerate(resultados):
            self.tabla_contactos.setItem(fila, 0, QTableWidgetItem(str(datos[0])))
            self.tabla_contactos.setItem(fila, 1, QTableWidgetItem(datos[1]))
            self.tabla_contactos.setItem(fila, 2, QTableWidgetItem(datos[2]))

    def cargar_clientes_combo(self):
        self.combo_cliente.clear()
        cursor.execute("SELECT id_cliente, nombre FROM cliente")
        for id_cliente, nombre in cursor.fetchall():
            self.combo_cliente.addItem(nombre, id_cliente)

    def setup_tab_empleado(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        form = QHBoxLayout()
        self.entry_nombre_empleado = QLineEdit()
        self.entry_puesto_empleado = QLineEdit()
        self.entry_nombre_empleado.setPlaceholderText("Nombre del empleado")
        self.entry_puesto_empleado.setPlaceholderText("Puesto")
        self.entry_nombre_empleado.setStyleSheet(
            "padding:5px; border-radius:5px; border:1px solid #ccc; color: #000000;"
        )
        self.entry_puesto_empleado.setStyleSheet(
            "padding:5px; border-radius:5px; border:1px solid #ccc; color: #000000;"
        )
        form.addWidget(QLabel("Nombre:"))
        form.addWidget(self.entry_nombre_empleado)
        form.addWidget(QLabel("Puesto:"))
        form.addWidget(self.entry_puesto_empleado)

        btn_agregar = QPushButton("Agregar Empleado")
        btn_agregar.setStyleSheet("""
            QPushButton { background-color:#f39c12; color:white; font-weight:bold; padding:8px 20px; border-radius:10px; }
            QPushButton:hover { background-color:#e67e22; }
        """)
        btn_agregar.clicked.connect(self.agregar_empleado)

        self.tabla_empleados = QTableWidget()
        self.tabla_empleados.setColumnCount(5)  # ID, Nombre, Puesto, Edit, Delete
        self.tabla_empleados.setHorizontalHeaderLabels(["ID", "Nombre", "Puesto", "Editar", "Eliminar"])
        self.tabla_empleados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_empleados.setStyleSheet("""
            QTableWidget { background-color:#ffffff; color:#000000; border-radius:10px; }
            QHeaderView::section { background-color:#f39c12; color:white; padding:5px; font-weight:bold; }
        """)
        self.tabla_empleados.setAlternatingRowColors(True)
        self.tabla_empleados.setFont(QFont("Arial", 10))

        layout.addLayout(form)
        layout.addWidget(btn_agregar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.tabla_empleados)

        self.tab_empleado.setLayout(layout)
        self.mostrar_empleados()

    def agregar_empleado(self):
        nombre = self.entry_nombre_empleado.text()
        puesto = self.entry_puesto_empleado.text()
        if nombre and puesto:
            query = "INSERT INTO empleado (nombre, puesto) VALUES (%s, %s)"
            cursor.execute(query, (nombre, puesto))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Empleado agregado ✅")
            self.entry_nombre_empleado.clear()
            self.entry_puesto_empleado.clear()
            self.mostrar_empleados()
        else:
            QMessageBox.warning(self, "Advertencia", "Llena todos los campos ⚠️")

    def mostrar_empleados(self):
        cursor.execute("SELECT * FROM empleado")
        resultados = cursor.fetchall()
        self.tabla_empleados.setRowCount(len(resultados))
        for fila, datos in enumerate(resultados):
            self.tabla_empleados.setItem(fila, 0, QTableWidgetItem(str(datos[0])))
            self.tabla_empleados.setItem(fila, 1, QTableWidgetItem(datos[1]))
            self.tabla_empleados.setItem(fila, 2, QTableWidgetItem(datos[2]))

            btn_edit = QPushButton("✏️")
            btn_edit.setStyleSheet("background-color:#f1c40f; border-radius:5px; color:black;")
            btn_edit.clicked.connect(lambda _, r=fila: self.editar_empleado(r))
            self.tabla_empleados.setCellWidget(fila, 3, btn_edit)

            btn_delete = QPushButton("🗑️")
            btn_delete.setStyleSheet("background-color:#e74c3c; border-radius:5px; color:white;")
            btn_delete.clicked.connect(lambda _, r=fila: self.eliminar_empleado(r))
            self.tabla_empleados.setCellWidget(fila, 4, btn_delete)

    def editar_empleado(self, fila):
        id_empleado = int(self.tabla_empleados.item(fila, 0).text())
        nombre = self.tabla_empleados.item(fila, 1).text()
        puesto = self.tabla_empleados.item(fila, 2).text()
        nuevo_nombre, ok1 = QInputDialog.getText(self, "Editar Nombre", "Nombre:", text=nombre)
        nuevo_puesto, ok2 = QInputDialog.getText(self, "Editar Puesto", "Puesto:", text=puesto)
        if ok1 and ok2:
            query = "UPDATE empleado SET nombre=%s, puesto=%s WHERE id_empleado=%s"
            cursor.execute(query, (nuevo_nombre, nuevo_puesto, id_empleado))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Empleado editado ✅")
            self.mostrar_empleados()

    def eliminar_empleado(self, fila):
        id_empleado = int(self.tabla_empleados.item(fila, 0).text())
        reply = QMessageBox.question(self, 'Eliminar Empleado', '¿Seguro que deseas eliminar este empleado?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            cursor.execute("DELETE FROM empleado WHERE id_empleado=%s", (id_empleado,))
            conexion.commit()
            self.mostrar_empleados()


app = QApplication(sys.argv)
ventana = EmpresaApp()
ventana.show()
sys.exit(app.exec())
