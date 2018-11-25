import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fdialog
import pickle
import threading
from error_identification.error_identification_gui import ErrorIdentification

# Training models
MODELS = ['Decision Tree', 'SVM', 'Perceptron', 'Random Forest', 'Naive Bayes']
ERROR_TYPES = ['lex-notTrWord', 'lex-incTrWord']


class TrainModelWindow(object):
    """Error Identification model training window.
    Contains implementation for selecting a BLAST file and
    the ML method to train the model.
    """

    def __init__(self, master):
        self.train_model_window = tk.Toplevel(master.master)
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
        self.model_type.set(MODELS[0])
        self.model_label = tk.Label(
            self.train_model_widget, text=_('Model type'))
        self.model_label.grid(row=2, column=0, pady=10)
        self.model_menu = tk.OptionMenu(
            self.train_model_widget, self.model_type, *MODELS)
        self.model_menu.grid(row=2, column=1, columnspan=2,
                             pady=10, sticky=tk.W)

        # Done
        self.done_button = tk.Button(
            self.train_model_widget, text=_('Done'), command=self.run_train_model)
        self.done_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Cancel
        self.cancel_button = tk.Button(
            self.train_model_widget, text=_('Cancel'), command=self.cancel_train_model)
        self.cancel_button.grid(row=3, column=1, columnspan=3, pady=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.train_model_window, mode='indeterminate')

        self.error_ident = None
        self.filenames = dict()
        self.train_model_window.protocol('WM_DELETE_WINDOW', self.close_window)

    def get_filename_callback(self, event):
        """Asks for a file and set `self.filenames`
        """
        filename = fdialog.askopenfile(title=_('Select a file'))
        if filename:
            if event.widget.message == 'BLAST':
                self.filenames['blast'] = filename.name
                self.blast_path_text.config(state=tk.NORMAL)
                self.blast_path_text.delete('1.0', tk.END)
                self.blast_path_text.insert('end', filename.name)
                self.blast_path_text.config(state=tk.DISABLED)

    def run_train_model(self):
        """Starts the training for the model.
        Creates a new ErrorIdentification object then starts a thread for the training.
        Also displays the progressbar.
        """
        # Start training thread
        self.error_ident = ErrorIdentification()
        train_thread = threading.Thread(target=self.train_model)
        train_thread.start()

        # Show progressbar and start update callback
        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=10)
        self.progress_bar.start(50)
        self.progress_bar.after(5, self.update_progress_bar_callback)

    def train_model(self):
        """Performs the training of the model in a separate
        thread created by `self.run_train_model`. Also saves the model
        in a pickle if the training was completed.
        """
        try:
            assert self.filenames['blast']
        except (AssertionError, KeyError):
            tk.messagebox.showerror(_('Select files'), _('It is necessary to select all files.'))
        else:
            self.error_ident.train(self.filenames['blast'],
                                   self.model_type.get(),
                                   error_types=ERROR_TYPES)
            if not self.error_ident.stop:
                # Training was not canceled, save model
                save_filename = 'model_' + self.model_type.get().replace(' ', '_') + '.pkl'
                with open(save_filename, 'wb') as model_file:
                    pickle.dump(self.error_ident, model_file)
                tk.messagebox.showinfo(_('Saved'), _('File saved as: ') + save_filename)
            self.error_ident.stop = True

    def cancel_train_model(self):
        """Handles the cancelling of a training.
        If there is no training running, it closes the window.
        """
        if self.error_ident:
            if self.error_ident.stop:
                self.close_window()
            else:
                self.error_ident.stop = True
        else:
            self.close_window()

    def close_window(self):
        """Handles the window close.
        If there is a training running, it should be cancelled first.
        """
        if self.error_ident:
            if not self.error_ident.stop:
                self.cancel_train_model()
        self.train_model_window.destroy()

    def update_progress_bar_callback(self):
        """Updates the progressbar each 50ms while the training is running.
        """
        if self.error_ident:
            if not self.error_ident.stop:
                self.progress_bar.update()
                self.progress_bar.after(50, self.update_progress_bar_callback)
            else:
                self.progress_bar.stop()
                self.progress_bar.grid_remove()

class TestModelWindow(object):
    def __init__(self, master):
        self.test_model_window = tk.Toplevel(master.master)
        self.test_model_window.title(_('Train Error Identification Model'))
        self.test_model_widget = tk.Frame(self.test_model_window)
        self.test_model_widget.grid(row=0, column=0, pady=10, padx=10)

        # Src File selection
        self.src_path_label = tk.Label(self.test_model_widget,
                                       text=_('Source file'))
        self.src_path_label.grid(row=0, column=0, sticky=tk.W)
        self.src_path_text = tk.Text(self.test_model_widget, height=1)
        self.src_path_text.config(state=tk.DISABLED)
        self.src_path_text.grid(row=0, column=1, padx=10)
        self.src_path_button = tk.Button(self.test_model_widget,
                                         text=_('Select'))
        self.src_path_button.bind('<Button-1>', self.get_filename_callback)
        self.src_path_button.message = 'Src'
        self.src_path_button.grid(row=0, column=2)

        # Sys File selection
        self.sys_path_label = tk.Label(self.test_model_widget,
                                       text=_('Machine Translation file'))
        self.sys_path_label.grid(row=1, column=0, sticky=tk.W)
        self.sys_path_text = tk.Text(self.test_model_widget, height=1)
        self.sys_path_text.config(state=tk.DISABLED)
        self.sys_path_text.grid(row=1, column=1, padx=10)
        self.sys_path_button = tk.Button(self.test_model_widget,
                                         text=_('Select'))
        self.sys_path_button.bind('<Button-1>', self.get_filename_callback)
        self.sys_path_button.message = 'Sys'
        self.sys_path_button.grid(row=1, column=2)

        # Model selection
        self.model_path_label = tk.Label(self.test_model_widget,
                                         text=_('ML model file'))
        self.model_path_label.grid(row=2, column=0, sticky=tk.W)
        self.model_path_text = tk.Text(self.test_model_widget, height=1)
        self.model_path_text.config(state=tk.DISABLED)
        self.model_path_text.grid(row=2, column=1, padx=10)
        self.model_path_button = tk.Button(self.test_model_widget,
                                           text=_('Select'))
        self.model_path_button.bind('<Button-1>', self.get_filename_callback)
        self.model_path_button.message = 'Model'
        self.model_path_button.grid(row=2, column=2)

        # Done
        self.done_button = tk.Button(
            self.test_model_widget, text=_('Done'), command=self.run_test_model)
        self.done_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Cancel
        self.cancel_button = tk.Button(
            self.test_model_widget, text=_('Cancel'), command=self.cancel_test_model)
        self.cancel_button.grid(row=3, column=1, columnspan=3, pady=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.test_model_window,
                                            mode='indeterminate')

        self.error_ident = None
        self.filenames = dict()
        self.test_model_window.protocol('WM_DELETE_WINDOW',
                                        self.close_window)

    def get_filename_callback(self, event):
        """Asks for a file and set `self.filenames`
        """
        filename = fdialog.askopenfile(title=_('Select a file'))
        if filename:
            if event.widget.message == 'Src':
                self.filenames['src'] = filename.name
                self.src_path_text.config(state=tk.NORMAL)
                self.src_path_text.delete('1.0', tk.END)
                self.src_path_text.insert('end', filename.name)
                self.src_path_text.config(state=tk.DISABLED)
            elif event.widget.message == 'Sys':
                self.filenames['sys'] = filename.name
                self.sys_path_text.config(state=tk.NORMAL)
                self.sys_path_text.delete('1.0', tk.END)
                self.sys_path_text.insert('end', filename.name)
                self.sys_path_text.config(state=tk.DISABLED)
            elif event.widget.message == 'Model':
                self.filenames['model'] = filename.name
                self.model_path_text.config(state=tk.NORMAL)
                self.model_path_text.delete('1.0', tk.END)
                self.model_path_text.insert('end', filename.name)
                self.model_path_text.config(state=tk.DISABLED)

    def run_test_model(self):
        """Starts the test for the model.
        Creates a new ErrorIdentification object then starts a thread for the classification.
        Also displays the progressbar.
        """
        with open(self.filenames['model'], 'rb') as _file:
            self.error_ident = pickle.load(_file)
        test_thread = threading.Thread(target=self.test_model)
        test_thread.start()

        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=10)
        self.progress_bar.start(50)
        self.progress_bar.after(5, self.update_progress_bar_callback)

    def test_model(self):
        """Performs the test of the model in a separate
        thread created by `self.run_test_model`. Also saves the classification
        in a BLAST file.
        """
        try:
            assert self.filenames['src']
            assert self.filenames['sys']
            assert self.filenames['model']
        except (AssertionError, KeyError):
            tk.messagebox.showerror(_('Select files'), _('It is necessary to select all files.'))
        else:
            save_filename = self.filenames['sys'] + '-blast'
            _class = self.error_ident.classify(self.filenames['src'],
                                               self.filenames['sys'])

            if not self.error_ident.stop:
                with open(save_filename, 'w') as _file:
                    _file.write(_class)
                    tk.messagebox.showinfo(_('Saved'), _('File saved as: ') + save_filename)
            self.error_ident.stop = True

    def cancel_test_model(self):
        """Handles the cancelling of a test.
        If there is no test running, it closes the window.
        """
        if self.error_ident:
            if self.error_ident.stop:
                self.close_window()
            else:
                self.error_ident.stop = True
        else:
            self.close_window()

    def close_window(self):
        """Handles the window close.
        If there is a traning running, it should be cancelled first.
        """
        if self.error_ident:
            if not self.error_ident.stop:
                self.cancel_test_model()
        self.test_model_window.destroy()

    def update_progress_bar_callback(self):
        """Updates the progressbar each 50ms while the training is running.
        """
        if self.error_ident:
            if not self.error_ident.stop:
                self.progress_bar.update()
                self.progress_bar.after(50, self.update_progress_bar_callback)
            else:
                self.progress_bar.stop()
                self.progress_bar.grid_remove()
