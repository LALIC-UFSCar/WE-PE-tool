'''APE using Word Embeddings execution window'''
import tkinter as tk
import tkinter.filedialog as fdialog
import tkinter.ttk as ttk
import tkinter.messagebox as msgb
import os
import queue
from readers.read_blast import BlastReader
from readers.read_muse_embeds import MuseReader
from post_edit import PostEditor


class PostEditWindow(object):
    '''
    APE Window class.
    Contains implementation for selecting the BLAST file and the bilingual embeddings files.
    Also creates threads to perform the APE and deal with cancelling events.
    '''

    def __init__(self, application):
        self.app = application
        self.blast_window = tk.Toplevel(application.master)
        self.blast_widget = tk.Frame(self.blast_window)
        self.blast_widget.grid(row=0, column=0, pady=10, padx=10)

        # BLAST
        self.blast_path_label = tk.Label(
            self.blast_widget, text=_('BLAST file'))
        self.blast_path_label.grid(row=0, column=0, sticky=tk.W)
        self.blast_path_text = tk.Text(self.blast_widget, height=1)
        self.blast_path_text.config(state=tk.DISABLED)
        self.blast_path_text.grid(row=0, column=1, padx=10)
        self.blast_path_button = tk.Button(self.blast_widget, text=_('Select'))
        self.blast_path_button.bind('<Button-1>', self.get_filename_callback)
        self.blast_path_button.message = 'BLAST'
        self.blast_path_button.grid(row=0, column=2)

        # EN
        self.en_path_label = tk.Label(
            self.blast_widget, text=_('Embeddings EN'))
        self.en_path_label.grid(row=1, column=0, sticky=tk.W)
        self.en_path_text = tk.Text(self.blast_widget, height=1)
        self.en_path_text.config(state=tk.DISABLED)
        self.en_path_text.grid(row=1, column=1, padx=10)
        self.en_path_button = tk.Button(self.blast_widget, text=_('Select'))
        self.en_path_button.bind('<Button-1>', self.get_filename_callback)
        self.en_path_button.message = 'EN'
        self.en_path_button.grid(row=1, column=2)

        # PT
        self.pt_path_label = tk.Label(
            self.blast_widget, text=_('Embeddings PT'))
        self.pt_path_label.grid(row=2, column=0, sticky=tk.W)
        self.pt_path_text = tk.Text(self.blast_widget, height=1)
        self.pt_path_text.config(state=tk.DISABLED)
        self.pt_path_text.grid(row=2, column=1, padx=10)
        self.pt_path_button = tk.Button(self.blast_widget, text=_('Select'))
        self.pt_path_button.bind('<Button-1>', self.get_filename_callback)
        self.pt_path_button.message = 'PT'
        self.pt_path_button.grid(row=2, column=2)

        self.error_type = tk.StringVar(self.blast_widget)
        self.error_type.set(application.errors[0])

        self.error_label = tk.Label(self.blast_widget, text=_('Error type'))
        self.error_label.grid(row=3, column=0, pady=10)
        self.error_menu = tk.OptionMenu(
            self.blast_widget, self.error_type, *application.errors)
        self.error_menu.grid(row=3, column=1, columnspan=2,
                             pady=10, sticky=tk.W)

        # Done
        self.done_button = tk.Button(
            self.blast_widget, text=_('Done'), command=self.load_muse)
        self.done_button.grid(row=4, column=0, columnspan=2, pady=10)
        self.cancel_button = tk.Button(self.blast_widget,
                                       text=_('Cancel'),
                                       command=self.close_window_callback)
        self.cancel_button.grid(row=4, column=1, columnspan=3, pady=10)
        self.cancel_ape_button = tk.Button(self.blast_widget,
                                           text=_('Cancel'),
                                           command=self.cancel_ape_callback)
        self.stop = False
        self.should_close = False

        # Threads
        self.ape_queue = queue.Queue()
        self.muse_en_queue = queue.Queue()
        self.muse_pt_queue = queue.Queue()
        self.running_threads = list()

        # Muse embeddings
        self.emb_en = dict()
        self.emb_pt = dict()

        self.blast_window.protocol('WM_DELETE_WINDOW',
                                   self.close_window_callback)

    def get_filename_callback(self, event):
        '''
        Select a file and set the according path view.
        '''
        filename = fdialog.askopenfile(title=_('Select a file'))
        try:
            assert filename
        except AssertionError:
            pass
        else:
            if event.widget.message == 'BLAST':
                self.blast_path_text.config(state=tk.NORMAL)
                self.blast_path_text.delete('1.0', tk.END)
                self.blast_path_text.insert('end', filename.name)
                self.blast_path_text.config(state=tk.DISABLED)
            elif event.widget.message == 'EN':
                self.en_path_text.config(state=tk.NORMAL)
                self.en_path_text.delete('1.0', tk.END)
                self.en_path_text.insert('end', filename.name)
                self.en_path_text.config(state=tk.DISABLED)
            else:
                self.pt_path_text.config(state=tk.NORMAL)
                self.pt_path_text.delete('1.0', tk.END)
                self.pt_path_text.insert('end', filename.name)
                self.pt_path_text.config(state=tk.DISABLED)

    def close_window_callback(self):
        '''
        Handles closing window.
        Needs to wait for all threads to stop running.
        '''
        self.cancel_ape_callback()
        self.should_close = True
        self.running_threads = [
            thread for thread in self.running_threads if thread.is_alive()]
        if not self.running_threads:
            self.blast_window.destroy()
        else:
            self.blast_window.after(100, self.close_window_callback)

    def cancel_ape_callback(self):
        '''
        Button Cancel pressed, but does not close the window.
        '''
        self.cancel_ape_button.config(state=tk.DISABLED)
        self.stop = True

    def load_muse(self):
        '''
        Loads MUSE embeddings files.
        Each file is loaded by a separate thread.
        '''
        en_path = self.en_path_text.get('1.0', tk.END).strip()
        pt_path = self.pt_path_text.get('1.0', tk.END).strip()

        try:
            assert en_path
            assert pt_path
        except AssertionError:
            tk.messagebox.showerror(_('Select files'),
                                    _('It is necessary to select all files.'))
        else:
            try:
                # Source embeddings thread
                self.running_threads.append(MuseReader(self,
                                                       en_path,
                                                       self.muse_en_queue))
            except FileNotFoundError:
                tk.messagebox.showerror(_('File not found'),
                                        _('MUSE file for English Embeddings not found.'))
            else:
                try:
                    # Target embeddings thread
                    self.running_threads.append(MuseReader(self,
                                                           pt_path,
                                                           self.muse_pt_queue))
                except FileNotFoundError:
                    tk.messagebox.showerror(_('File not found'),
                                            _('MUSE file for Portuguese Embeddings not found.'))
                else:
                    self.blast_window.after(100, self.load_muse_callback)

                    self.done_button.grid_forget()
                    self.cancel_button.grid_forget()
                    self.blast_path_button.config(state=tk.DISABLED)
                    self.en_path_button.config(state=tk.DISABLED)
                    self.pt_path_button.config(state=tk.DISABLED)
                    self.error_menu.config(state=tk.DISABLED)

    def load_blast(self):
        '''
        Loads BLAST file.
        Filters the errors by the one selected by the user.
        '''
        blast_path = self.blast_path_text.get('1.0', tk.END).strip()

        try:
            assert blast_path
        except AssertionError:
            tk.messagebox.showerror(
                _('Select files'), _('It is necessary to select all files.'))
        else:
            try:
                blast_reader = BlastReader(blast_path)
            except FileNotFoundError:
                tk.messagebox.showerror(
                    _('File not found'), _('BLAST file not found.'))
            else:
                errors = blast_reader.get_filtered_errors(
                    [self.error_type.get()])

                self.filename = os.path.splitext(os.path.split(blast_path)[1])[
                    0] + '_APE_' + self.error_type.get()

                # Progress bar to track the APE process
                progress_var = tk.DoubleVar()
                self.progress_bar = ttk.Progressbar(
                    self.blast_window, variable=progress_var, maximum=len(errors))
                self.cancel_ape_button.config(state=tk.NORMAL)
                self.cancel_ape_button.grid(
                    row=5, column=0, columnspan=3, pady=10)
                self.progress_bar.grid(row=4, column=0, columnspan=3, pady=10)

                # Post Editing Thread
                self.running_threads.append(PostEditor(self,
                                                       blast_reader,
                                                       progress_var))
                self.blast_window.after(100, self.ape_queue_callback)

    def load_muse_callback(self):
        '''
        Checks if MUSE files were completely loaded.
        If both were loaded and the program must not stop, performs the APE
        on the BLAST file'''
        try:
            if not self.emb_en:
                self.emb_en = self.muse_en_queue.get_nowait()
            if not self.emb_pt:
                self.emb_pt = self.muse_pt_queue.get_nowait()
        except queue.Empty:
            self.blast_window.after(100, self.load_muse_callback)
        else:
            if not self.stop:
                self.load_blast()

    def ape_queue_callback(self):
        '''
        Checks if the APE has finished.
        If the thread has been canceled, re-enable buttons
        '''
        try:
            msg = self.ape_queue.get_nowait()
            if msg == 0:
                msgb.showinfo(_('Saved'), _('File saved as: ') + self.filename)
                self.close_window_callback()
            else:
                if not self.should_close:
                    self.stop = False
                    self.progress_bar.destroy()
                    self.cancel_ape_button.grid_forget()
                    self.done_button.grid(
                        row=4, column=0, columnspan=2, pady=10)
                    self.cancel_button.grid(
                        row=4, column=1, columnspan=3, pady=10)
                    self.blast_path_button.config(state=tk.NORMAL)
                    self.en_path_button.config(state=tk.NORMAL)
                    self.pt_path_button.config(state=tk.NORMAL)
                    self.error_menu.config(state=tk.NORMAL)
        except queue.Empty:
            self.blast_window.after(100, self.ape_queue_callback)
