    # imported classes for widget
    # ----------------------------------
import sys
from PyQt5 import QtWidgets as qw
from PyQt5 import QtGui as qg
from PyQt5 import QtCore as qc

    # imported classes for data
    # ----------------------------------
import pyodbc as odbc
import pandas as pd

    # imported classes for plotting
    # ----------------------------------
import matplotlib.pyplot as plt


# ------------------------------------------------- APPLICATION ------------------------------------------------- #
class GUI(qw.QMainWindow):

    # Add cls Variables here
    # ----------------------------------
    cnxn = odbc.connect("Driver={SQL Server Native Client 11.0};"
                        "Server=DESKTOP-D3UL9SD;"
                        "Database=Statistics;"
                        "Trusted_Connection=yes;")

    sql_tb = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = 'Statistics'" 
    # ----------------------------------

    # Main application + start app
    # ----------------------------------

    def __init__(self):
        super().__init__()

        l = qw.QGridLayout(self)

        self.title = 'Regression models'
        self.top = 100
        self.left = 100
        self.width = 500
        self.height = 500
        
        self.setWindowTitle(self.title)
        self.setGeometry(self.top,self.left,self.width,self.height)
        self.initUI()

    # Added items to main window
    # ----------------------------------
    def initUI(self):

    # main menu
    # ----------------------------------
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        plot_menu = menubar.addMenu('Plot')
        statistics_menu = menubar.addMenu('Statistics')
        
        # file menu
        open_file = qw.QAction('Open File', self)
        file_menu.addAction(open_file)
        open_file.triggered.connect(self.open_csv) 

        upload_file = qw.QAction('Upload File', self)
        file_menu.addAction(upload_file)
        upload_file.triggered.connect(self.upload_file)

        download_file = qw.QAction('Download File', self)        
        file_menu.addAction(download_file)

        exit_gui = qw.QAction('Exit', self)        
        file_menu.addAction(exit_gui)
        exit_gui.triggered.connect(self.close)

        # plot_menu
        line_plot = qw.QAction('Line Plot', self)
        plot_menu.addAction(line_plot)
        line_plot.triggered.connect(self.line_plot)

        bar_plot = qw.QAction('Bar Plot', self)
        plot_menu.addAction(bar_plot)
        bar_plot.triggered.connect(self.bar_plot)
        
        scatter_plot = qw.QAction('Scatter Plot', self)
        plot_menu.addAction(scatter_plot)
        scatter_plot.triggered.connect(self.scatter_plot)
        
        # statistics menu
        des  = qw.QAction('Descriptives', self)
        statistics_menu.addAction(des)
        
        regression_menu    = statistics_menu.addMenu('Regression')
        
        single_var    = qw.QAction('Linear Regession', self)
        regression_menu.addAction(single_var)

        multi_var     = qw.QAction('Linear Multivariate Regression', self)
        regression_menu.addAction(multi_var)

    # adding table to mainwindow
    # ----------------------------------
        self.table = qw.QTableWidget(self)
        self.table.setRowCount(5)
        self.table.setColumnCount(5)
        self.table.setGeometry(qc.QRect(20,55,500,450))

    # adding dropdown with table in database
    # ----------------------------------
        self.db_label = qw.QLabel(self)
        self.db_label.setText('Current Tables')
        self.db_label.move(20,22)

        self.qboxtable = qw.QComboBox(self)
        self.qboxtable.move(100,22)
        self.qboxtable.activated[str].connect(self.download_file)

    # visualizing GUI
    # ----------------------------------
        self.fill_qboxtable()
        self.show()
    # ----------------------------------

    # Qboxtable with all tables in db
    # ----------------------------------
    def fill_qboxtable(self):
        self.qboxtable.clear()
        df_tb = pd.read_sql(GUI.sql_tb, GUI.cnxn)
        df_tb = df_tb['TABLE_NAME']

        for i in range(len(df_tb)):
            self.qboxtable.addItem(df_tb[i])
    # ----------------------------------

    # Open CSV
    # ----------------------------------
    def open_csv(self):
        fp = qw.QFileDialog.getOpenFileName(self,
                                             'Single File',
                                             '~Desktop\Python\data',
                                             '*.csv')
        # adding data from csv to table
        if fp[0] != '':
            df_csv = pd.read_csv(str(fp[0]))
            column_header = list(df_csv.columns)
            column = 0
            self.table.setColumnCount(df_csv.shape[1]) 
            self.table.setRowCount(df_csv.shape[0]) 
            for i in column_header:
                row = 0
                for j in df_csv[i]:
                    if str(j) != 'nan':
                        newitem = qw.QTableWidgetItem(str(j))
                        self.table.setItem(row, column, newitem)
                    else:
                        empty = qw.QTableWidgetItem('')
                        self.table.setItem(row, column, empty)
                    row = row + 1
                column = column + 1
                    

            # adjust amount of columns in table
            self.table.setColumnCount(len(column_header))

            # add headers to table
            self.table.setHorizontalHeaderLabels(column_header)

        else:
            'Nothing'
            
    # Upload File (still need to work on data types in pandas to give to sql server...)
    # ----------------------------------
    def upload_file(self):

        tb_name, okpressed = qw.QInputDialog.getText(self, 'Table Name', 'Please state table name:')
        if okpressed:
            cursor = GUI.cnxn.cursor()
            sql_tb = "Create table [" + tb_name + "] (index_column float)"
            cursor.execute(str(sql_tb))
            cursor.commit()
        self.fill_qboxtable()

        for i in range(self.table.columnCount()):
            cl_name = str(self.table.horizontalHeaderItem(i).text())
            sql_cl = "Alter table [" + tb_name + "] Add [" + cl_name + "] varchar(255)"
            cursor.execute(str(sql_cl))
            cursor.commit()

        for i in range(self.table.rowCount()):
            sql_in = "insert into " + tb_name + "(index_column) values (" + str(i) + ")"
            cursor.execute(str(sql_in))
            cursor.commit()

        for i in range(self.table.columnCount()):
            cl_name = str(self.table.horizontalHeaderItem(i).text())
            for j in range(self.table.rowCount()):
                item = self.table.item(j,i).text()
                sql_it = "Update [" + tb_name + "] set [" + cl_name + "] = " + "'" +   item +  "' where index_column = " + str(j)
                cursor.execute(str(sql_it))
                cursor.commit()

    # Download File
    # ----------------------------------
    def download_file(self, tb_name):
        sql_re = 'Select * from ' + tb_name
        df_sql = pd.read_sql(sql_re, GUI.cnxn)

        column_header = list(df_sql.columns)
        column = 0
        self.table.setColumnCount(df_sql.shape[1]) 
        self.table.setRowCount(df_sql.shape[0]) 
        for i in column_header:
            row = 0
            for j in df_sql[i]:
                if str(j) != 'nan':
                    newitem = qw.QTableWidgetItem(str(j))
                    self.table.setItem(row, column, newitem)
                else:
                    empty = qw.QTableWidgetItem('')
                    self.table.setItem(row, column, empty)
                row = row + 1
            column = column + 1
                    

        # adjust amount of columns in table
        self.table.setColumnCount(len(column_header))

        # add headers to table
        self.table.setHorizontalHeaderLabels(column_header)    
        
    # Close Application (still needs work)
    # ----------------------------------
    def close(self):
        pass

    # Create dataframe from tablewidget
    # ----------------------------------
    def df_table(self):
        df_main = pd.DataFrame()

        for i in range(self.table.columnCount()):
            cl_name = str(self.table.horizontalHeaderItem(i).text())
            df_main[str(cl_name)] = 1

        for i in range(self.table.columnCount()):
            cl_name = str(self.table.horizontalHeaderItem(i).text())
            for j in range(self.table.rowCount()):
                item = self.table.item(j,i).text()
                if i == 0:
                    df_main = df_main.append({str(cl_name): str(item)}, ignore_index=True)
                else:
                    df_add = pd.DataFrame({cl_name: [item]}, index=[j])
                    df_main.update(df_add)

        return df_main

    # lineplot
    # ----------------------------------
    def line_plot(self):
        df_main = self.df_table()
        plot = list(df_main.columns)

        x_, okpressed = qw.QInputDialog.getItem(self, 'X Variable', 'Please name X variable:', plot)
        y_, okpressed = qw.QInputDialog.getItem(self, 'Y Variable', 'Please name Y variable:', plot)
        x = (list(df_main[str(x_)]))
        y = (list(df_main[str(y_)]))
        plt.plot(x , y)
        plt.show()

    # scatterplot
    # ----------------------------------
    def scatter_plot(self):
        df_main = self.df_table()
        plot = list(df_main.columns)

        x_, okpressed = qw.QInputDialog.getItem(self, 'X Variable', 'Please name X variable:', plot)
        y_, okpressed = qw.QInputDialog.getItem(self, 'Y Variable', 'Please name Y variable:', plot)
        x = (list(df_main[str(x_)]))
        y = (list(df_main[str(y_)]))
        plt.scatter(x , y)
        plt.show()

    # barplot
    # ----------------------------------
    def bar_plot(self):
        df_main = self.df_table()
        plot = list(df_main.columns)

        x_, okpressed = qw.QInputDialog.getItem(self, 'X Variable', 'Please name X variable:', plot)
        y_, okpressed = qw.QInputDialog.getItem(self, 'Y Variable', 'Please name Y variable:', plot)
        x = (list(df_main[str(x_)]))
        y = (list(df_main[str(y_)]))
        plt.scatter(x , y)
        plt.show()

App = qw.QApplication(sys.argv)
W = GUI()
sys.exit(App.exec)
