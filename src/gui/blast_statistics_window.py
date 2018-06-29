'''BLAST error type statistics window'''
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fdialog
from readers.read_blast import BlastReader


class BLASTStatsWindow(object):
    '''
    BLAST Statistics class.
    Constains implementation for select the BLAST file and perform
    computations for statistics about each error type according to
    the taxonomy in:

    Martins, D.B.J., Caseli, H.M.: Automatic machine translation error identification.
    Machine Translation 29(1), 1-24 (Mar 2015), https://doi.org/10.1007/s10590-014-9163-y
    '''

    def __init__(self, application):
        self.app = application
        self.blast_file_path = ''
        self.error_types = {'morph-numberConc': _('Syntactic - Number agreement'),
                            'morph-abstWord': _('Syntactic - Absent word'),
                            'morph-genderConc': _('Syntactic - Gender agreement'),
                            'morph-verbForm': _('Syntactic - Verbal inflection'),
                            'morph-posChg': _('Syntactic - PoS'),
                            'morph-otherMorph': _('Syntactic - Others'),
                            'lex-extWord': _('Lexical - Extra word'),
                            'lex-abstWord': _('Lexical - Absent word'),
                            'lex-notTrWord': _('Lexical - Not translated word'),
                            'lex-incTrWord': _('Lexical - Incorrectly translated word'),
                            'lex-werErrWord': _('Lexical - Spelling error'),
                            'grm-extGrm': _('N-gram - Extra n-gram'),
                            'grm-abstGrm': _('N-gram - Absent n-gram'),
                            'grm-notTrGrm': _('N-gram - Not translated n-gram'),
                            'grm-incTrGram': _('N-gram - Incorrectly translated n-gram'),
                            'ord': _('Reordering - Order'),
                            'oth': _('Others')}
        self.error_stats_values = dict()

        self.load_blast_file()
        self.get_statistics()

        # Create windows
        self.blast_stats_window = tk.Toplevel(application.master)

        # Table
        self.blast_stats_table = ttk.Treeview(
            self.blast_stats_window, columns=(_('Amount'), _('%')))
        self.blast_stats_table.heading('#0', text=_('Error category'))
        self.blast_stats_table.heading('#1', text=_('Amount'))
        self.blast_stats_table.heading('#2', text=_('%'))
        self.blast_stats_table.column('#0', width=260, stretch=tk.YES)
        self.blast_stats_table.column('#1', width=75, stretch=tk.YES)
        self.blast_stats_table.column('#2', width=50, stretch=tk.YES)
        self.blast_stats_table.grid(row=0, column=0, pady=10, padx=10, sticky='nsew')

        self.insert_table_values()

    def load_blast_file(self):
        '''Select a BLAST annotated file'''
        filename = fdialog.askopenfile(title=_('Select a file'))
        try:
            assert filename
        except AssertionError:
            pass
        else:
            self.blast_file_path = filename

    def get_statistics(self):
        '''Read BLAST file and get statistics for each error type'''
        try:
            blast_reader = BlastReader(self.blast_file_path.name)
        except FileNotFoundError:
            tk.messagebox.showerror(
                _('File not found'), _('BLAST file not found.'))
        except AttributeError:
            pass
        else:
            total_errors = len(
                blast_reader.get_filtered_errors(self.error_types.keys()))

            for _type in self.error_types:
                error_occurences = len(
                    blast_reader.get_filtered_errors([_type]))
                error_percentage = (error_occurences / total_errors) * 100
                self.error_stats_values[_type] = (
                    error_occurences, '{0:.2f}'.format(error_percentage))

    def insert_table_values(self):
        '''Inserts values in the table'''
        for _type in sorted(self.error_stats_values):
            self.blast_stats_table.insert(
                '', 'end', text=self.error_types[_type], values=self.error_stats_values[_type])
