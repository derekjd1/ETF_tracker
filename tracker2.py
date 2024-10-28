import sys
import yfinance as yf  # finance library
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QLineEdit, QPushButton, QTextEdit, QComboBox, QMessageBox, QMainWindow)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# Main application window
class ETFTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ETF Tracker")
        self.setGeometry(300, 100, 800, 600)

        # Initialize cache and last checked values
        self.etf_data_cache = {}
        self.last_checked_symbol = ""
        self.last_plotted_symbol = ""
        self.last_plotted_period = ""

        # Layout
        layout = QVBoxLayout()

        # Title label with modified font
        title_label = QLabel("ETF Tracker")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")  # Bold title
        layout.addWidget(title_label)

        # ETF Symbol input
        self.etf_symbol_label = QLabel("Enter ETF Symbol:")
        layout.addWidget(self.etf_symbol_label)
        
        self.etf_entry = QLineEdit()
        layout.addWidget(self.etf_entry)

        # Period selection dropdown
        self.period_label = QLabel("Select Period:")
        layout.addWidget(self.period_label)
        
        self.period_menu = QComboBox()
        self.period_menu.addItems(["1mo", "3mo", "6mo", "1y", "2y", "5y"])
        layout.addWidget(self.period_menu)

        # Text box for displaying ETF data (now empty by default)
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

        # Check button with bold styling
        self.check_button = QPushButton("Check")
        self.check_button.setStyleSheet("font-weight: bold;")  # Bold button text
        self.check_button.clicked.connect(self.check_etf)
        layout.addWidget(self.check_button)

        # Plot button with bold styling
        self.plot_button = QPushButton("Plot Trend")
        self.plot_button.setStyleSheet("font-weight: bold;")  # Bold button text
        self.plot_button.clicked.connect(self.open_plot_window)
        layout.addWidget(self.plot_button)

        # Clear button with bold styling
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet("font-weight: bold;")  # Bold button text
        self.clear_button.clicked.connect(self.clear_data)
        layout.addWidget(self.clear_button)

        # Set layout and show
        self.setLayout(layout)

    def fetch_etf_data(self, etf_symbol, period="1d"):
        key = (etf_symbol, period)
        if key in self.etf_data_cache:
            return self.etf_data_cache[key]
        etf = yf.Ticker(etf_symbol)
        data = etf.history(period=period)
        if data.empty:
            QMessageBox.information(self, "Info", f"No data available for {etf_symbol} in the selected period.")
            return None
        self.etf_data_cache[key] = data
        return data

    def check_etf(self):
        etf_symbol = self.etf_entry.text().upper()  # Get the ETF symbol
        
        if not etf_symbol:
            QMessageBox.critical(self, "Error", "Please enter an ETF symbol.")
            return
        
        # Avoid redundant checks if the symbol hasn't changed
        if etf_symbol == self.last_checked_symbol:
            return  # No need to refetch

        # Fetch and cache data if needed
        data = self.fetch_etf_data(etf_symbol)
        if data is None:
            return

        # Display ETF information
        current_price = data['Close'].iloc[-1]  # Most recent price
        text_content = f"Current Price of {etf_symbol}: ${current_price:.2f}\n"

        # Only update the text box if necessary
        if self.text_box.toPlainText().strip() != text_content.strip():
            self.text_box.clear()
            self.text_box.append(text_content)

            # Additional ETF data example
            etf = yf.Ticker(etf_symbol)
            info = etf.info
            self.text_box.append(f"Name: {info.get('longName', 'N/A')}\n")
            self.text_box.append(f"Market Cap: {info.get('marketCap', 'N/A')}\n")
            self.text_box.append(f"52-Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}\n")
            self.text_box.append(f"52-Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}\n")
            self.text_box.append(f"Dividend Yield: {info.get('dividendYield', 'N/A')}\n")
            self.text_box.append(f"Beta: {info.get('beta', 'N/A')}\n")
        
        # Update the last checked value
        self.last_checked_symbol = etf_symbol

    def open_plot_window(self):
        etf_symbol = self.etf_entry.text().upper()
        period = self.period_menu.currentText()

        if not etf_symbol:
            QMessageBox.critical(self, "Error", "Please enter an ETF symbol.")
            return

        data = self.fetch_etf_data(etf_symbol, period)
        if data is None:
            return

        self.plot_window = PlotWindow(etf_symbol, period, data)
        self.plot_window.show()

    def clear_data(self):
        # Clears the text box, input fields, and plot
        self.etf_entry.clear()
        self.text_box.clear()
        self.last_checked_symbol = ""
        self.last_plotted_symbol = ""
        self.last_plotted_period = ""


# Secondary window to display the plot in a larger view
class PlotWindow(QMainWindow):
    def __init__(self, etf_symbol, period, data):
        super().__init__()
        self.setWindowTitle(f"{etf_symbol} - {period} Trend")
        self.setGeometry(200, 100, 1000, 600)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create the plot
        self.figure = plt.figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Plot the data
        self.plot_data(etf_symbol, period, data)

    def plot_data(self, etf_symbol, period, data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Plot the data with green color and add an arrow to the end
        ax.plot(data.index, data['Close'], label="Close Price", color="green")
        ax.set_title(f"{etf_symbol} - {period} Trend")
        ax.set_xlabel("Date", fontsize=10, labelpad=15)
        ax.set_ylabel("Close Price", fontsize=10, labelpad=10)
        ax.legend()


        # Adjust the layout to prevent x-axis label overlap
        self.figure.tight_layout(pad=2)  # Adds padding around the plot

        # More points on x-axis by increasing tick frequency
        ax.tick_params(axis='x', labelsize=8)
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))  # Shows up to 10 x-axis points
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Draw the canvas
        self.canvas.draw()


# Run the application
app = QApplication(sys.argv)
window = ETFTrackerApp()
window.show()
sys.exit(app.exec_())
