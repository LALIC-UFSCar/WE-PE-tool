import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fdialog
import nltk.translate.ibm2 as align
import queue
from readers.read_blast import BlastReader
from error_identification.error_identification_gui import ErrorIdentification


class ErrorIdentificationWindow(object):
    """Error Identification Window class.
    Contains implementation for training and testing models.
    Also has an implementation to run a pretrained default model.
    The window also shows the source and output sentences, with the
    specification of the identified error
    """

    def __init__(self, application):
        self.app = application
        self.error_identification_window = tk.Toplevel(application.master)
        self.error_identification_window.title(_('Error Identification'))
        self.error_identification_widget = tk.Frame(
            self.error_identification_window)
        self.error_identification_widget.grid(
            row=0, column=0, pady=10, padx=10)

        # Menu
        self.menubar = tk.Menu(self.error_identification_window)
        self.menubar.add_command(
            label=_('Train'), command=lambda: TrainModelWindow(self))
        self.menubar.add_command(label=_('Test'))
        self.menubar.add_command(label=_('Execute'))
        self.error_identification_window.config(menu=self.menubar)

        # Src
        self.widget_src = tk.Frame(self.error_identification_widget)
        self.widget_src.grid(row=0, column=0, pady=10, padx=10)
        self.label_src = tk.Label(self.widget_src, text='Src')
        self.label_src.grid(row=0, column=0, padx=(0, 10))
        self.src_text = tk.Text(self.widget_src, height=5)
        self.src_text.tag_config('DESTAQUE', background='cyan')
        self.src_text.config(state=tk.DISABLED)
        self.src_text.grid(row=0, column=1)

        # Sys
        self.widget_sys = tk.Frame(self.error_identification_widget)
        self.widget_sys.grid(row=1, column=0, pady=10, padx=10)
        self.label_sys = tk.Label(self.widget_sys, text='Sys')
        self.label_sys.grid(row=0, column=0, padx=(0, 10))
        self.sys_text = tk.Text(self.widget_sys, height=5)
        self.sys_text.tag_config('DESTAQUE', background='cyan')
        self.sys_text.config(state=tk.DISABLED)
        self.sys_text.grid(row=0, column=1)

        # Error
        self.widget_error = tk.Frame(self.error_identification_widget)
        self.widget_error.grid(row=3, column=0, pady=10, padx=10)
        self.label_error = tk.Label(self.widget_error, text=_('Error'))
        self.label_error.grid(row=0, column=0, padx=(0, 10))
        self.error_text = tk.Text(self.widget_error, height=1)
        self.error_text.config(state=tk.DISABLED)
        self.error_text.grid(row=0, column=1)

        # Training models
        self.available_models = ['Decision Tree',
                                 'SVM', 'Perceptron', 'Random Forest']


class TrainModelWindow(object):

    def __init__(self, master):
        self.train_model_window = tk.Toplevel(
            master.error_identification_widget)
        self.train_model_window.title(_('Train Error Identification Model'))
        self.train_model_widget = tk.Frame(self.train_model_window)
        self.train_model_widget.grid(row=0, column=0, pady=10, padx=10)

        # BLAST File selection
        self.blast_path_label = tk.Label(
            self.train_model_widget, text=_('BLAST file'))
        self.blast_path_label.grid(row=0, column=0, sticky=tk.W)
        self.blast_path_text = tk.Text(self.train_model_widget, height=1)
        self.blast_path_text.config(state=tk.DISABLED)
        self.blast_path_text.grid(row=0, column=1, padx=10)
        self.blast_path_button = tk.Button(
            self.train_model_widget, text=_('Select'))
        self.blast_path_button.bind('<Button-1>', self.get_filename_callback)
        self.blast_path_button.message = 'BLAST'
        self.blast_path_button.grid(row=0, column=2)

        # Model selection
        self.model_type = tk.StringVar(self.train_model_widget)
        self.model_type.set(master.available_models[0])
        self.model_label = tk.Label(
            self.train_model_widget, text=_('Error type'))
        self.model_label.grid(row=2, column=0, pady=10)
        self.model_menu = tk.OptionMenu(
            self.train_model_widget, self.model_type, *master.available_models)
        self.model_menu.grid(row=2, column=1, columnspan=2,
                             pady=10, sticky=tk.W)

        # Done
        self.done_button = tk.Button(
            self.train_model_widget, text=_('Done'), command=self.train_model)
        self.done_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.cancel_button = tk.Button(
            self.train_model_widget, text=_('Cancel'), command=print)
        self.cancel_button.grid(row=3, column=1, columnspan=3, pady=10)

        self.filenames = dict()

    def get_filename_callback(self, event):
        filename = fdialog.askopenfile(title=_('Select a file'))
        if filename:
            if event.widget.message == 'BLAST':
                self.filenames['blast'] = filename.name
                self.blast_path_text.config(state=tk.NORMAL)
                self.blast_path_text.delete('1.0', tk.END)
                self.blast_path_text.insert('end', filename.name)
                self.blast_path_text.config(state=tk.DISABLED)

    def train_model(self):
        try:
            assert self.filenames['blast']
        except (AssertionError, KeyError):
            tk.messagebox.showerror(_('Select files'), _(
                'It is necessary to select all files.'))
        else:
            ErrorIdentification().train(
                self.filenames['blast'], self.model_type.get())
