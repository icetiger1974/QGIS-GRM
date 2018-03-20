from PyQt4.QtGui import QMessageBox

def show_error_message(message, parent):
   """
   """
   msg = QMessageBox(parent)
   msg.setIcon(QMessageBox.Critical)
   msg.setInformativeText(message)
   msg.setWindowTitle("Error")
   msg.setStandardButtons(QMessageBox.Ok)
   retval = msg.exec_()

def c_bool(value):
   if value == 'true':
      return True
   return False

def bool_c(value):
   if value:
      return 'true'
   return 'false'