''' Main Window'''
#  -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.filedialog as fdialog
from readers.read_ape import ApeReader
import gui.error_identification_window as error_ident
from .ape_window import PostEditWindow
from .blast_statistics_window import BLASTStatsWindow


class Application(object):
    '''
    Application class.
    Contains implementations for the main window, which shows and controls the annotation process.
    '''

    def __init__(self, master=None):
        self.master = master
        self.master.title(_('Automatic Post-Editing'))

        self.cur_line = -1
        self.errors = ['lex-incTrWord', 'lex-notTrWord']

        self.filename = ''
        self.ape_reader = None

        # Menu
        self.menubar = tk.Menu(self.master)
        self.apemenu = tk.Menu(self.menubar, tearoff=0)
        self.apemenu.add_command(label=_('Open'), command=self.load_ape_file)

        # Error Identification menu
        self.error_ident_menu = tk.Menu(self.apemenu, tearoff=0)
        self.error_ident_menu.add_command(label=_('Train'),
                                          command=lambda: error_ident.TrainModelWindow(self))
        self.error_ident_menu.add_command(label=_('Test'),
                                          command=lambda: error_ident.TestModelWindow(self))
        self.apemenu.add_cascade(label=_('Error identification'),
                                 menu=self.error_ident_menu)

        self.menubar.add_cascade(label=_('APE'), menu=self.apemenu)

        self.blastmenu = tk.Menu(self.menubar, tearoff=0)
        self.blastmenu.add_command(
            label=_('Open'), command=lambda: PostEditWindow(self))
        self.blastmenu.add_command(
            label=_('Statistics'), command=lambda: BLASTStatsWindow(self))
        self.menubar.add_cascade(label='BLAST', menu=self.blastmenu)

        self.master.config(menu=self.menubar)

        # Src
        self.widget_src = tk.Frame(self.master)
        self.widget_src.grid(row=0, column=0, pady=10, padx=10)
        self.label_src = tk.Label(self.widget_src, text='Src')
        self.label_src.grid(row=0, column=0, padx=(0, 10))
        self.src_text = tk.Text(self.widget_src, height=5)
        self.src_text.tag_config('DESTAQUE', background='cyan')
        self.src_text.config(state=tk.DISABLED)
        self.src_text.grid(row=0, column=1)

        # Ref
        self.widget_ref = tk.Frame(self.master)
        self.widget_ref.grid(row=1, column=0, pady=10, padx=10)
        self.label_ref = tk.Label(self.widget_ref, text='Ref')
        self.label_ref.grid(row=0, column=0, padx=(0, 10))
        self.ref_text = tk.Text(self.widget_ref, height=5)
        self.ref_text.tag_config('DESTAQUE', background='cyan')
        self.ref_text.config(state=tk.DISABLED)
        self.ref_text.grid(row=0, column=1)

        # Sys
        self.widget_sys = tk.Frame(self.master)
        self.widget_sys.grid(row=2, column=0, pady=10, padx=10)
        self.label_sys = tk.Label(self.widget_sys, text='Sys')
        self.label_sys.grid(row=0, column=0, padx=(0, 10))
        self.sys_text = tk.Text(self.widget_sys, height=5)
        self.sys_text.tag_config('DESTAQUE', background='cyan')
        self.sys_text.config(state=tk.DISABLED)
        self.sys_text.grid(row=0, column=1)

        # APE
        self.widget_cor = tk.Frame(self.master)
        self.widget_cor.grid(row=3, column=0, pady=10, padx=10, sticky=tk.W)
        self.label_cor = tk.Label(self.widget_cor, text=_('APE'))
        self.label_cor.grid(row=0, column=0, rowspan=4, padx=(0, 10))
        self.cor_list = tk.Listbox(self.widget_cor, width=35, height=5)
        self.cor_list.grid(row=0, column=1, rowspan=4, padx=(0, 10))
        self.cor_list_scroll = tk.Scrollbar(
            self.widget_cor, command=self.cor_list.yview, orient=tk.VERTICAL)
        self.cor_list_scroll.grid(
            row=0, column=1, rowspan=4, padx=(0, 10), sticky=tk.N + tk.S + tk.E)
        self.cor_list.configure(yscrollcommand=self.cor_list_scroll.set)
        self.correto_button = tk.Button(
            self.widget_cor, text=_('Correct'), width=15)
        self.correto_button.bind('<Button-1>', self.annotate)
        self.correto_button.message = 'CORRETO'
        self.correto_button.grid(row=0, column=2)
        self.parcial_button = tk.Button(
            self.widget_cor, text=_('Partially correct'), width=15)
        self.parcial_button.bind('<Button-1>', self.annotate)
        self.parcial_button.message = 'PARCIAL'
        self.parcial_button.grid(row=1, column=2)
        self.errado_button = tk.Button(
            self.widget_cor, text=_('Wrong'), width=15)
        self.errado_button.bind('<Button-1>', self.annotate)
        self.errado_button.message = 'ERRADO'
        self.errado_button.grid(row=2, column=2)
        self.ignorar_button = tk.Button(
            self.widget_cor, text=_('Ignore'), width=15)
        self.ignorar_button.bind('<Button-1>', self.annotate)
        self.ignorar_button.message = 'IGNORAR'
        self.ignorar_button.grid(row=3, column=2)

        # Next
        self.prev_button = tk.Button(
            self.widget_cor, text=_('Previous'), width=10)
        self.prev_button.bind('<Button-1>', self.next_line)
        self.prev_button.message = 'ANTERIOR'
        self.prev_button.grid(row=3, column=3)
        self.next_button = tk.Button(self.widget_cor, text=_('Next'), width=10)
        self.next_button.bind('<Button-1>', self.next_line)
        self.next_button.message = 'PROXIMO'
        self.next_button.grid(row=3, column=4)

        # Numero da sentenca
        self.sent_num = tk.StringVar()
        self.numero_label = tk.Label(self.master, textvariable=self.sent_num)
        self.numero_label.grid(row=0, column=1, padx=(
            0, 10), pady=10, sticky=tk.N + tk.E)

    def load_ape_file(self):
        '''Loads APE file for annotation'''
        self.filename = fdialog.askopenfilename(title=_('Select a file'))
        assert self.filename
        self.show_annotations()
        return

    def show_annotations(self):
        '''
        Shows annotations for the selected file.
        Highlights aligned words, shows correction suggestions and sentence numbers
        '''
        assert self.filename

        try:
            self.ape_reader = ApeReader(self.filename)
        except RuntimeError:
            tk.messagebox.showerror(
                _('Invalid format'), _('Invalid file format'))
        else:
            self.cur_line = self.ape_reader.cur_line
            if self.cur_line < 0:
                self.cur_line = 0

            # Update source text
            self.src_text.config(state=tk.NORMAL)
            self.src_text.delete('1.0', tk.END)
            self.src_text.insert(
                'end', ' '.join(self.ape_reader.src_lines[self.cur_line]))
            # Get aligned error words columns
            word_col = list()
            for i in self.ape_reader.error_lines[self.cur_line][0]:
                if i >= 0:
                    words = ' '.join(
                        self.ape_reader.src_lines[self.cur_line][:i])
                    col = len(words)
                    if '"' in words:
                        col = col + 2 * words.count('"')
                    word_col.append(col)
            # Highlight aligned error words
            for col in word_col:
                self.src_text.tag_add('DESTAQUE', '1.{} wordstart'.format(
                    col + 1), '1.{} wordend'.format(col + 1))
            self.src_text.config(state=tk.DISABLED)

            # Update reference text
            self.ref_text.config(state=tk.NORMAL)
            self.ref_text.delete('1.0', tk.END)
            self.ref_text.insert(
                'end', ' '.join(self.ape_reader.ref_lines[self.cur_line]))
            word_col = list()
            for i in self.ape_reader.error_lines[self.cur_line][2]:
                if i >= 0:
                    words = ' '.join(self.ape_reader.ref_lines[self.cur_line][:i])
                    col = len(words)
                    if '"' in words:
                        col = col + 2 * words.count('"')
                    word_col.append(col)
            for col in word_col:
                self.ref_text.tag_add('DESTAQUE', '1.{} wordstart'.format(
                    col + 1), '1.{} wordend'.format(col + 1))
            self.ref_text.config(state=tk.DISABLED)

            # Update system output text
            self.sys_text.config(state=tk.NORMAL)
            self.sys_text.delete('1.0', tk.END)
            self.sys_text.insert(
                'end', ' '.join(self.ape_reader.sys_lines[self.cur_line]))
            word_col = list()
            for i in self.ape_reader.error_lines[self.cur_line][1]:
                if i >= 0:
                    words = ' '.join(self.ape_reader.sys_lines[self.cur_line][:i])
                    col = len(words)
                    if '"' in words:
                        col = col + 2 * words.count('"')
                    word_col.append(col)
            for col in word_col:
                self.sys_text.tag_add('DESTAQUE', '1.{} wordstart'.format(
                    col + 1), '1.{} wordend'.format(col + 1))
            self.sys_text.config(state=tk.DISABLED)

            # Update correction suggestions list
            self.cor_list.delete(0, tk.END)
            for (i, word) in enumerate(self.ape_reader.corrections[self.cur_line]):
                self.cor_list.insert(tk.END, word[0])
                self.cor_list.itemconfig(i, {'bg': word[1]})

            # Update sentence number
            self.sent_num.set(
                '{}/{}'.format(self.ape_reader.cur_line + 1, len(self.ape_reader.src_lines)))

    def annotate(self, event):
        '''Controls buttons for the suggestion annotations'''
        if self.cur_line < 0:
            tk.messagebox.showerror(
                _('Open file'), _('It is necessary to open a file'))
        else:
            if not self.cor_list.curselection():
                tk.messagebox.showerror(
                    _('Select something'), _('Select a word to annotate'))
            else:
                self.ape_reader.cur_line = self.cur_line
                if event.widget.message == 'CORRETO':
                    self.ape_reader.corrections[self.cur_line][
                        self.cor_list.curselection()[0]][1] = 'green'
                    self.ape_reader.save()
                elif event.widget.message == 'PARCIAL':
                    self.ape_reader.corrections[self.cur_line][
                        self.cor_list.curselection()[0]][1] = 'yellow'
                    self.ape_reader.save()
                elif event.widget.message == 'ERRADO':
                    self.ape_reader.corrections[self.cur_line][
                        self.cor_list.curselection()[0]][1] = 'red'
                    self.ape_reader.save()
                else:
                    self.ape_reader.corrections[self.cur_line][
                        self.cor_list.curselection()[0]][1] = 'white'
                    self.ape_reader.save()
                self.show_annotations()

    def next_line(self, event):
        '''Controlls next sentence button'''
        if self.cur_line < 0:
            tk.messagebox.showerror(
                _('Open file'), _('It is necessary to open a file'))
        else:
            if event.widget.message == 'PROXIMO' and self.cur_line < len(self.ape_reader.src_lines) - 1:
                self.cur_line = self.cur_line + 1
            elif event.widget.message == 'ANTERIOR' and self.cur_line > 0:
                self.cur_line = self.cur_line - 1
            self.ape_reader.cur_line = self.cur_line
            self.ape_reader.save()
            self.show_annotations()
