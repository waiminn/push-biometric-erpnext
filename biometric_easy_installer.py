import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp
import os, json

class BiometricEasyInstaller(QMainWindow):

	def __init__(self):
		super().__init__()
		self.reg_exp_for_ip = "((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?=\s*netmask)"
		self.init_ui()

	def init_ui(self):
		self.counter = 0
		self.setup_window()
		self.setup_textboxes_and_label()
		self.center()
		self.show()

	def setup_window(self):
		self.setFixedSize(470, 550)
		self.setWindowTitle('ERPNext Biometric Service')

	def setup_textboxes_and_label(self):

		self.create_label("API Secret", "api_secret", 20, 0, 200, 30)
		self.create_field("textbox_erpnext_api_secret", 20, 30, 200, 30)

		self.create_label("API Key", "api_key", 20, 60, 200, 30)
		self.create_field("textbox_erpnext_api_key", 20, 90, 200, 30)

		self.create_label("ERPNext URL", "erpnext_url", 20, 120, 200, 30)
		self.create_field("textbox_erpnext_url", 20, 150, 200, 30)


		self.create_label("Pull Frequency (in minutes)", "pull_frequency", 250, 0, 200, 30)
		self.create_field("textbox_pull_frequency", 250, 30, 200, 30)

		#validating integer
		self.onlyInt = QIntValidator(10, 30)
		self.textbox_pull_frequency.setValidator(self.onlyInt)

		self.create_label("Import Start Date (DD/MM/YYYY)", "import_start_date", 250, 60, 200, 30)
		self.create_field("textbox_import_start_date", 250, 90, 200, 30)
		self.validate_data(r"^\d{1,2}/\d{1,2}/\d{4}$", "textbox_import_start_date")

		self.create_separator(210, 470)
		self.create_button('+', 'add', 390, 230, 35, 30, self.add_devices_fields)
		self.create_button('-', 'remove', 420, 230, 35, 30, self.remove_devices_fields)

		self.create_label("Device ID", "device_id", 20, 260, 0, 30)
		self.create_label("Device IP", "device_ip", 170, 260, 0, 30)
		self.create_label("Shift", "shift", 320, 260, 0, 0)

		# First Row for table
		self.create_field("device_id_0", 20, 290, 145, 30)
		self.create_field("device_ip_0", 165, 290, 145, 30)
		self.validate_data(self.reg_exp_for_ip, "device_ip_0")
		self.create_field("shift_0", 310, 290, 145, 30)

		# Actions buttons
		self.create_button('Set Configuration', 'set_conf', 20, 500, 130, 30, self.setup_local_config)
		self.create_button('Start Service', 'start_service', 320, 500, 130, 30, self.integrate_biometric, enable=False)

	# Widgets Genrators
	def create_label(self, label_text, label_name, x, y, height, width):
		setattr(self,  label_name, QLabel(self))
		label  = getattr(self, label_name)
		label.move(x, y)
		label.setText(label_text)
		if height and width:
			label.resize(height, width)
		label.show()

	def create_field(self, field_name, x, y, height, width):
		setattr(self,  field_name, QLineEdit(self))
		field  = getattr(self, field_name)
		field.move(x, y)
		field.resize(height, width)
		field.show()

	def create_separator(self, y, width):
		setattr(self, 'separator', QLineEdit(self))
		field  = getattr(self, 'separator')
		field.move(0, y)
		field.resize(width, 5)
		field.setEnabled(False)
		field.show()

	def create_button(self, button_label, button_name, x, y, height, width, callback_function, enable = True):
		setattr(self,  button_name, QPushButton(button_label, self))
		button = getattr(self, button_name)
		button.move(x, y)
		button.resize(height, width)
		button.clicked.connect(callback_function)
		button.setEnabled(enable)

	def center(self):
		frame = self.frameGeometry()
		screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
		centerPoint = QApplication.desktop().screenGeometry(screen).center()
		frame.moveCenter(centerPoint)
		self.move(frame.topLeft())

	def add_devices_fields(self):
		if self.counter < 5:
			self.counter += 1
			self.create_field("device_id_" + str(self.counter), 20, 290+(self.counter * 30), 145, 30)
			self.create_field("device_ip_" + str(self.counter), 165, 290+(self.counter * 30), 145, 30)
			self.validate_data(self.reg_exp_for_ip, "device_ip_" + str(self.counter))
			self.create_field("shift_" + str(self.counter), 310, 290+(self.counter * 30), 145, 30)

	# data validator
	def validate_data(self, reg_exp, field_name):
		field = getattr(self, field_name)
		reg_ex = QRegExp(reg_exp)
		input_validator = QRegExpValidator(reg_ex, field)
		field.setValidator(input_validator)


	def remove_devices_fields(self):
		if self.counter > 0:
			b  = getattr(self, "shift_" + str(self.counter))
			b.deleteLater()
			b  = getattr(self, "device_id_" + str(self.counter))
			b.deleteLater()
			b  = getattr(self, "device_ip_" + str(self.counter))
			b.deleteLater()

			self.counter -=1

	def integrate_biometric(self):
		self.close()
		print("Starting Service...")
		start_service_command = 'python -c "from push_to_erpnext import infinite_loop; infinite_loop()"'
		os.system(start_service_command)
		create_message_box("Message", "Service Running")

	def setup_local_config(self):
		print("Setting Local Configuration...")
		if os.path.exists("local_config.py"):
			os.remove("local_config.py")

		local_config_py = open("local_config.py", 'w+')

		config = self.get_local_config()
		if not config:
			print("Local Configuration not Updated...")
			return 0

		local_config_py.write(config)

		print("Local Configuration Updated.")

		create_message_box("Message", "Configuration Updated.\n\nClick on Start Service.")

		getattr(self, 'start_service').setEnabled(True)

	def get_device_details(self):
		devices = []
		shifts = []
		for idx in range(0, self.counter+1):
			devices.append({'device_id':getattr(self, "device_id_" + str(idx)).text(),
				'ip':getattr(self, "device_ip_" + str(idx)).text(),
				'punch_direction': '',
				'clear_from_device_on_fetch': ''})
			device = []
			device.append(getattr(self, "device_id_" + str(idx)).text())
			shifts.append({
					'shift_type_name': getattr(self, "shift_" + str(idx)).text(),
					'related_device_id': device
				})

		return devices, shifts

	def get_local_config(self):
		if validate_fields(self) == 0:
			return 0
		string = self.textbox_import_start_date.text()
		formated_date = "".join([ele for ele in reversed(string.split("/"))])

		devices, shifts = self.get_device_details()
		return '''# ERPNext related configs
ERPNEXT_API_KEY = '{0}'
ERPNEXT_API_SECRET = '{1}'
ERPNEXT_URL = '{2}'


# operational configs
PULL_FREQUENCY = {3} or 60 # in minutes
LOGS_DIRECTORY = 'logs' # logs of this script is stored in this directory
IMPORT_START_DATE = '{4}' or None # format: '20190501'

# Biometric device configs (all keys mandatory)
	#- device_id - must be unique, strictly alphanumerical chars only. no space allowed.
	#- ip - device IP Address
	#- punch_direction - 'IN'/'OUT'/'AUTO'/None
	#- clear_from_device_on_fetch: if set to true then attendance is deleted after fetch is successful.
	#(Caution: this feature can lead to data loss if used carelessly.)
devices = {5}

# Configs updating sync timestamp in the Shift Type DocType
shift_type_device_mapping = {6}
'''.format(self.textbox_erpnext_api_key.text(), self.textbox_erpnext_api_secret.text(), self.textbox_erpnext_url.text(), self.textbox_pull_frequency.text(), formated_date, json.dumps(devices), json.dumps(shifts))

def validate_fields(self):
	if not self.textbox_erpnext_api_key.text():
		return create_message_box("Missing Value Required", "Please Set API Key", "warning")
	if not self.textbox_erpnext_api_secret.text():
		return create_message_box("Missing Value Required", "Please Set API Secret", "warning")
	if not self.textbox_erpnext_url.text():
		return create_message_box("Missing Value Required", "Please Set ERPNext URL", "warning")

def create_message_box(title, text, icon="information"):
	msg = QMessageBox()
	msg.setWindowTitle(title)
	msg.setText(text)
	if icon=="warning":
		msg.setIcon(QtWidgets.QMessageBox.Warning)
	else:
		msg.setIcon(QtWidgets.QMessageBox.Information)
	msg.setStyleSheet("QLabel{min-width: 150px;}")
	msg.exec_()
	return 0



def main():
	biometric_app = QApplication(sys.argv)
	biometric_window = BiometricEasyInstaller()
	biometric_app.exec_()

if __name__ == "__main__":
	main()
